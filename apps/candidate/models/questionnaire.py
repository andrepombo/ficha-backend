from django.db import models
from django.core.validators import MinValueValidator
from .candidate import Candidate


class QuestionnaireTemplate(models.Model):
    """
    Template for a questionnaire associated with a specific job position.
    Admins create these templates with questions and options.
    """
    position_key = models.CharField(
        max_length=200,
        verbose_name='Position Key',
        help_text='Job position this questionnaire is for (matches Candidate.position_applied)',
        db_index=True
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Title',
        help_text='Descriptive title for this questionnaire'
    )
    step_number = models.PositiveIntegerField(
        default=1,
        verbose_name='Step Number',
        help_text='Order of this questionnaire in the multi-step form (1 = first step after basic info)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Optional description shown to candidates'
    )
    version = models.PositiveIntegerField(
        default=1,
        verbose_name='Version',
        help_text='Version number for tracking changes'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Is Active',
        help_text='Whether this template is active (multiple templates can be active per position)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position_key', 'step_number', '-created_at']
        verbose_name = 'Questionnaire Template'
        verbose_name_plural = 'Questionnaire Templates'
        indexes = [
            models.Index(fields=['position_key', 'is_active']),
            models.Index(fields=['position_key', 'step_number']),
        ]

    def __str__(self):
        return f"{self.title} - {self.position_key} (v{self.version})"

    def get_total_points(self):
        """Calculate total possible points for this questionnaire."""
        return sum(q.points for q in self.questions.all())

    def save(self, *args, **kwargs):
        """Save the template. Multiple templates can be active per position."""
        super().save(*args, **kwargs)


class Question(models.Model):
    """
    A question within a questionnaire template.
    """
    QUESTION_TYPE_CHOICES = [
        ('multi_select', 'Multiple Select'),
        ('single_select', 'Single Select'),
    ]

    SCORING_MODE_CHOICES = [
        ('all_or_nothing', 'All or Nothing'),
        ('partial', 'Partial Credit'),
        ('weighted', 'Weighted (by option points)'),
    ]

    template = models.ForeignKey(
        QuestionnaireTemplate,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Template'
    )
    question_text = models.TextField(
        verbose_name='Question Text',
        help_text='The question to ask the candidate'
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='multi_select',
        verbose_name='Question Type'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Display Order',
        help_text='Order in which this question appears'
    )
    points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0)],
        verbose_name='Points',
        help_text='Points awarded for correct answer'
    )
    scoring_mode = models.CharField(
        max_length=20,
        choices=SCORING_MODE_CHOICES,
        default='all_or_nothing',
        verbose_name='Scoring Mode',
        help_text='How to score this question'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"

    def get_correct_options(self):
        """Return queryset of correct options for this question."""
        return self.options.filter(is_correct=True)


class QuestionOption(models.Model):
    """
    An option/choice for a question.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='Question'
    )
    option_text = models.CharField(
        max_length=500,
        verbose_name='Option Text',
        help_text='The text for this option'
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='Is Correct',
        help_text='Whether this is a correct answer'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Display Order',
        help_text='Order in which this option appears'
    )
    option_points = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name='Option Points',
        help_text='Used for Partial scoring in multi-select: relative points of this correct option'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Question Option'
        verbose_name_plural = 'Question Options'

    def __str__(self):
        correct_marker = '✓' if self.is_correct else '✗'
        return f"{correct_marker} {self.option_text[:50]}"


class CandidateQuestionnaireResponse(models.Model):
    """
    A candidate's response to a questionnaire template.
    Stores the overall score and metadata.
    """
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='questionnaire_responses',
        verbose_name='Candidate'
    )
    template = models.ForeignKey(
        QuestionnaireTemplate,
        on_delete=models.PROTECT,
        related_name='responses',
        verbose_name='Template'
    )
    position_key = models.CharField(
        max_length=200,
        verbose_name='Position Key',
        help_text='Denormalized position key for easier querying',
        db_index=True
    )
    score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.00,
        verbose_name='Score',
        help_text='Total score achieved'
    )
    max_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.00,
        verbose_name='Maximum Score',
        help_text='Maximum possible score'
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Submitted At'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Candidate Questionnaire Response'
        verbose_name_plural = 'Candidate Questionnaire Responses'
        indexes = [
            models.Index(fields=['candidate', 'template']),
            models.Index(fields=['position_key', 'submitted_at']),
        ]

    def __str__(self):
        return f"{self.candidate.full_name} - {self.template.title} ({self.score}/{self.max_score})"

    def get_percentage(self):
        """Calculate percentage score."""
        if self.max_score == 0:
            return 0
        return (float(self.score) / float(self.max_score)) * 100


class CandidateSelectedOption(models.Model):
    """
    Tracks which options a candidate selected for each question.
    Many-to-many relationship between responses and options.
    """
    response = models.ForeignKey(
        CandidateQuestionnaireResponse,
        on_delete=models.CASCADE,
        related_name='selected_options',
        verbose_name='Response'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='candidate_selections',
        verbose_name='Question'
    )
    option = models.ForeignKey(
        QuestionOption,
        on_delete=models.CASCADE,
        related_name='candidate_selections',
        verbose_name='Option'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Candidate Selected Option'
        verbose_name_plural = 'Candidate Selected Options'
        indexes = [
            models.Index(fields=['response', 'question']),
            models.Index(fields=['option']),
        ]
        unique_together = [['response', 'question', 'option']]

    def __str__(self):
        return f"{self.response.candidate.full_name} - Q{self.question.id} - {self.option.option_text[:30]}"
