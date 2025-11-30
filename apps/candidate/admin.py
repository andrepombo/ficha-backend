from django.contrib import admin
from django.db.models import Count
from .models import (
    Candidate, 
    ProfessionalExperience, 
    Interview, 
    ScoringWeight, 
    WorkCard,
    ActivityLog,
    QuestionnaireTemplate,
    Question,
    QuestionOption,
    CandidateQuestionnaireResponse,
    CandidateSelectedOption,
)


class ProfessionalExperienceInline(admin.TabularInline):
    """
    Inline admin for professional experiences.
    """
    model = ProfessionalExperience
    extra = 1
    fields = ('empresa', 'cargo', 'descricao_atividades', 'data_admissao', 'data_desligamento', 'motivo_saida')


class WorkCardInline(admin.TabularInline):
    """
    Inline admin for work card documents.
    """
    model = WorkCard
    extra = 0
    fields = ('file', 'file_name', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    can_delete = True


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """
    Admin interface for managing candidate applications.
    """
    
    list_display = [
        'get_full_name',
        'email',
        'phone_number',
        'position_applied',
        'status',
        'years_of_experience',
        'applied_date',
    ]
    
    list_filter = [
        'status',
        'position_applied',
        'how_found_vacancy',
        'worked_at_pinte_before',
        'applied_date',
        'years_of_experience',
    ]
    
    search_fields = [
        'full_name',
        'email',
        'phone_number',
        'position_applied',
        'skills',
    ]
    
    readonly_fields = ['applied_date', 'updated_date']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'full_name',
                'cpf',
                'email',
                'phone_number',
                'date_of_birth',
            )
        }),
        ('Address', {
            'fields': (
                'address',
                'city',
                'state',
                'postal_code',
                'country',
            ),
            'classes': ('collapse',),
        }),
        ('Professional Information', {
            'fields': (
                'position_applied',
                'current_company',
                'current_position',
                'years_of_experience',
            )
        }),
        ('Indicação (Referral)', {
            'fields': (
                'has_relatives_in_company',
                'referred_by',
                'how_found_vacancy',
                'how_found_vacancy_other',
                'worked_at_pinte_before',
            )
        }),
        ('Documentos', {
            'fields': (
                'resume',
                'photo',
                'cover_letter',
            )
        }),
        ('Skills & Qualifications', {
            'fields': (
                'skills',
                'certifications',
            )
        }),
        ('Availability', {
            'fields': (
                'available_start_date',
                'expected_salary',
            )
        }),
        ('Application Status', {
            'fields': (
                'status',
                'notes',
            )
        }),
        ('Metadata', {
            'fields': (
                'applied_date',
                'updated_date',
            ),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [ProfessionalExperienceInline, WorkCardInline]
    
    actions = ['mark_as_reviewing', 'mark_as_interviewed', 'mark_as_accepted', 'mark_as_rejected']
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist view to add statistics and current date."""
        from datetime import datetime
        
        # Get statistics
        extra_context = extra_context or {}
        extra_context['total_candidates'] = Candidate.objects.count()
        extra_context['pending_count'] = Candidate.objects.filter(status='pending').count()
        extra_context['reviewing_count'] = Candidate.objects.filter(status='reviewing').count()
        extra_context['interviewed_count'] = Candidate.objects.filter(status='interviewed').count()
        extra_context['accepted_count'] = Candidate.objects.filter(status='accepted').count()
        extra_context['rejected_count'] = Candidate.objects.filter(status='rejected').count()
        
        # Add current month and year
        now = datetime.now()
        extra_context['current_month'] = now.strftime('%B')  # Full month name
        extra_context['current_year'] = now.year
        extra_context['current_month_pt'] = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
            'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
            'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
            'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }.get(now.strftime('%B'), now.strftime('%B'))
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def mark_as_reviewing(self, request, queryset):
        """Mark selected candidates as under review."""
        updated = queryset.update(status='reviewing')
        self.message_user(request, f'{updated} candidate(s) marked as under review.')
    mark_as_reviewing.short_description = 'Mark as Under Review'
    
    def mark_as_interviewed(self, request, queryset):
        """Mark selected candidates as interviewed."""
        updated = queryset.update(status='interviewed')
        self.message_user(request, f'{updated} candidate(s) marked as interviewed.')
    mark_as_interviewed.short_description = 'Mark as Interviewed'
    
    def mark_as_accepted(self, request, queryset):
        """Mark selected candidates as accepted."""
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} candidate(s) marked as accepted.')
    mark_as_accepted.short_description = 'Mark as Accepted'
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected candidates as rejected."""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} candidate(s) marked as rejected.')
    mark_as_rejected.short_description = 'Mark as Rejected'


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    """
    Admin interface for managing interviews.
    """
    
    list_display = [
        'title',
        'candidate',
        'interviewer',
        'interview_type',
        'scheduled_date',
        'scheduled_time',
        'status',
        'rating',
    ]
    
    list_filter = [
        'status',
        'interview_type',
        'scheduled_date',
        'interviewer',
        'rating',
    ]
    
    search_fields = [
        'title',
        'candidate__full_name',
        'interviewer__username',
        'interviewer__first_name',
        'interviewer__last_name',
        'location',
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'candidate',
                'title',
                'interview_type',
            )
        }),
        ('Agendamento', {
            'fields': (
                'scheduled_date',
                'scheduled_time',
                'duration_minutes',
                'location',
            )
        }),
        ('Responsável', {
            'fields': (
                'interviewer',
                'created_by',
            )
        }),
        ('Detalhes', {
            'fields': (
                'description',
                'status',
            )
        }),
        ('Feedback', {
            'fields': (
                'feedback',
                'rating',
            ),
            'classes': ('collapse',),
        }),
        ('Notificações', {
            'fields': (
                'candidate_notified',
                'reminder_sent',
            ),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected interviews as completed."""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} entrevista(s) marcada(s) como concluída(s).')
    mark_as_completed.short_description = 'Marcar como Concluída'
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected interviews as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} entrevista(s) cancelada(s).')
    mark_as_cancelled.short_description = 'Cancelar Entrevista'


@admin.register(ScoringWeight)
class ScoringWeightAdmin(admin.ModelAdmin):
    """
    Admin interface for managing scoring weights configuration.
    """
    
    list_display = [
        '__str__',
        'is_active',
        'get_total_display',
        'created_at',
        'updated_at',
    ]
    
    list_filter = [
        'is_active',
        'created_at',
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'get_total_display']
    
    fieldsets = (
        ('Experiência & Habilidades', {
            'fields': (
                'years_of_experience',
                'idle_time',
                'worked_at_pinte_before',
                'has_relatives_in_company',
                'referred_by',
            )
        }),
        ('Educação & Qualificações', {
            'fields': (
                'education_level',
                'courses',
                'skills',
                'certifications',
            )
        }),
        ('Disponibilidade & Logística', {
            'fields': (
                'immediate_availability',
                'own_transportation',
                'travel_availability',
                'height_painting',
            )
        }),
        ('Desempenho em Entrevistas', {
            'fields': (
                'average_rating',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'created_by',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
                'get_total_display',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_total_display(self, obj):
        """Display total points."""
        total = obj.get_total_points()
        if abs(total - 100) < 0.1:
            return f'{total} pontos ✓'
        else:
            return f'{total} pontos ⚠️ (deve ser 100)'
    get_total_display.short_description = 'Total de Pontos'
    
    def save_model(self, request, obj, form, change):
        """Override save to set created_by."""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing and managing activity logs.
    """
    
    list_display = [
        'timestamp',
        'action_type',
        'get_candidate_display',
        'get_user_display',
        'description',
    ]
    
    list_filter = [
        'action_type',
        'timestamp',
    ]
    
    search_fields = [
        'candidate__full_name',
        'candidate_name',
        'description',
        'user__username',
        'user__first_name',
        'user__last_name',
    ]
    
    readonly_fields = [
        'candidate',
        'candidate_name',
        'interview',
        'user',
        'action_type',
        'description',
        'old_value',
        'new_value',
        'timestamp',
        'ip_address',
        'user_agent',
    ]
    
    fieldsets = (
        ('Action Information', {
            'fields': (
                'action_type',
                'description',
                'timestamp',
            )
        }),
        ('Related Objects', {
            'fields': (
                'candidate',
                'candidate_name',
                'interview',
                'user',
            )
        }),
        ('Change Details', {
            'fields': (
                'old_value',
                'new_value',
            ),
            'classes': ('collapse',),
        }),
        ('Request Metadata', {
            'fields': (
                'ip_address',
                'user_agent',
            ),
            'classes': ('collapse',),
        }),
    )
    
    # Allow deletion for admins
    def has_add_permission(self, request):
        """Disable manual creation of logs (should be auto-generated)."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make logs read-only (can only view and delete)."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow admins to delete logs."""
        return request.user.is_superuser
    
    def get_candidate_display(self, obj):
        """Display candidate name (with deleted indicator if applicable)."""
        if obj.candidate:
            return obj.candidate.full_name
        elif obj.candidate_name:
            return f"{obj.candidate_name} (deletado)"
        return "-"
    get_candidate_display.short_description = 'Candidato'
    
    def get_user_display(self, obj):
        """Display user name."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return "Sistema"
    get_user_display.short_description = 'Usuário'
    
    # Bulk delete action
    actions = ['delete_selected']
    
    def delete_selected(self, request, queryset):
        """Allow bulk deletion of activity logs."""
        if not request.user.is_superuser:
            self.message_user(request, 'Apenas superusuários podem deletar logs.', level='error')
            return
        
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} log(s) deletado(s) com sucesso.')
    delete_selected.short_description = 'Deletar logs selecionados'


# ============================================================================
# Questionnaire Admin
# ============================================================================

class QuestionOptionInline(admin.TabularInline):
    """Inline admin for question options."""
    model = QuestionOption
    extra = 2
    fields = ('option_text', 'is_correct', 'order')
    ordering = ('order',)


class QuestionInline(admin.StackedInline):
    """Inline admin for questions."""
    model = Question
    extra = 1
    fields = ('question_text', 'question_type', 'order', 'points', 'scoring_mode')
    ordering = ('order',)
    show_change_link = True


@admin.register(QuestionnaireTemplate)
class QuestionnaireTemplateAdmin(admin.ModelAdmin):
    """Admin interface for questionnaire templates."""
    
    list_display = [
        'title',
        'position_key',
        'version',
        'is_active',
        'get_question_count',
        'get_total_points',
        'created_at',
    ]
    
    list_filter = [
        'is_active',
        'position_key',
        'created_at',
    ]
    
    search_fields = [
        'title',
        'position_key',
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'get_total_points']
    
    fieldsets = (
        ('Template Information', {
            'fields': (
                'title',
                'position_key',
                'version',
                'is_active',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
                'get_total_points',
            ),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [QuestionInline]
    
    actions = ['activate_templates', 'deactivate_templates']
    
    def get_question_count(self, obj):
        """Get number of questions in this template."""
        return obj.questions.count()
    get_question_count.short_description = 'Questions'
    
    def activate_templates(self, request, queryset):
        """Activate selected templates."""
        for template in queryset:
            template.is_active = True
            template.save()
        self.message_user(request, f'{queryset.count()} template(s) activated.')
    activate_templates.short_description = 'Activate selected templates'
    
    def deactivate_templates(self, request, queryset):
        """Deactivate selected templates."""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} template(s) deactivated.')
    deactivate_templates.short_description = 'Deactivate selected templates'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for questions."""
    
    list_display = [
        '__str__',
        'template',
        'question_type',
        'order',
        'points',
        'scoring_mode',
        'get_option_count',
    ]
    
    list_filter = [
        'question_type',
        'scoring_mode',
        'template',
    ]
    
    search_fields = [
        'question_text',
        'template__title',
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Question Information', {
            'fields': (
                'template',
                'question_text',
                'question_type',
                'order',
            )
        }),
        ('Scoring', {
            'fields': (
                'points',
                'scoring_mode',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [QuestionOptionInline]
    
    def get_option_count(self, obj):
        """Get number of options for this question."""
        return obj.options.count()
    get_option_count.short_description = 'Options'


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    """Admin interface for question options."""
    
    list_display = [
        '__str__',
        'question',
        'is_correct',
        'order',
    ]
    
    list_filter = [
        'is_correct',
        'question__template',
    ]
    
    search_fields = [
        'option_text',
        'question__question_text',
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Option Information', {
            'fields': (
                'question',
                'option_text',
                'is_correct',
                'order',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )


class CandidateSelectedOptionInline(admin.TabularInline):
    """Inline admin for candidate selected options."""
    model = CandidateSelectedOption
    extra = 0
    fields = ('question', 'option', 'get_is_correct')
    readonly_fields = ('get_is_correct',)
    can_delete = False
    
    def get_is_correct(self, obj):
        """Display if the selected option is correct."""
        return '✓' if obj.option.is_correct else '✗'
    get_is_correct.short_description = 'Correct?'


@admin.register(CandidateQuestionnaireResponse)
class CandidateQuestionnaireResponseAdmin(admin.ModelAdmin):
    """Admin interface for candidate questionnaire responses."""
    
    list_display = [
        'candidate',
        'template',
        'position_key',
        'score',
        'max_score',
        'get_percentage',
        'submitted_at',
    ]
    
    list_filter = [
        'position_key',
        'template',
        'submitted_at',
    ]
    
    search_fields = [
        'candidate__full_name',
        'template__title',
        'position_key',
    ]
    
    readonly_fields = [
        'candidate',
        'template',
        'position_key',
        'score',
        'max_score',
        'get_percentage',
        'submitted_at',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Response Information', {
            'fields': (
                'candidate',
                'template',
                'position_key',
            )
        }),
        ('Score', {
            'fields': (
                'score',
                'max_score',
                'get_percentage',
            )
        }),
        ('Metadata', {
            'fields': (
                'submitted_at',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [CandidateSelectedOptionInline]
    
    def has_add_permission(self, request):
        """Disable manual creation of responses (should be done via API)."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make responses read-only."""
        return False


@admin.register(CandidateSelectedOption)
class CandidateSelectedOptionAdmin(admin.ModelAdmin):
    """Admin interface for candidate selected options."""
    
    list_display = [
        'response',
        'question',
        'option',
        'get_is_correct',
        'created_at',
    ]
    
    list_filter = [
        'option__is_correct',
        'question__template',
    ]
    
    search_fields = [
        'response__candidate__full_name',
        'question__question_text',
        'option__option_text',
    ]
    
    readonly_fields = [
        'response',
        'question',
        'option',
        'get_is_correct',
        'created_at',
    ]
    
    def get_is_correct(self, obj):
        """Display if the selected option is correct."""
        return '✓' if obj.option.is_correct else '✗'
    get_is_correct.short_description = 'Correct?'
    
    def has_add_permission(self, request):
        """Disable manual creation."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make read-only."""
        return False
