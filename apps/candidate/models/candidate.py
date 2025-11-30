from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
import io
import os


class Candidate(models.Model):
    """
    Model to store candidate information for job applications.
    """
    
    # Status choices
    STATUS_CHOICES = [
        ('incomplete', 'Incomplete Form'),
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('shortlisted', 'Selected for Interview'),
        ('interviewed', 'Interviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    # Portuguese status translations
    STATUS_TRANSLATIONS = {
        'incomplete': 'Incompleto',
        'pending': 'Pendente',
        'reviewing': 'Em Análise',
        'shortlisted': 'Selecionado para Entrevista',
        'interviewed': 'Entrevistado',
        'accepted': 'Aceito',
        'rejected': 'Rejeitado',
    }
    
    # Personal Information
    full_name = models.CharField(max_length=200, verbose_name='Nome Completo', default='')
    
    cpf_regex = RegexValidator(
        regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        message="CPF deve estar no formato: xxx.xxx.xxx-xx"
    )
    cpf = models.CharField(
        max_length=14, 
        verbose_name='CPF', 
        blank=False,
        validators=[cpf_regex],
        help_text='Formato: xxx.xxx.xxx-xx'
    )
    
    email = models.EmailField(validators=[EmailValidator()], verbose_name='Email Address', blank=True, null=True)
    
    phone_regex = RegexValidator(
        regex=r'^\d{2}\s\d{5}-\d{4}$',
        message="Telefone deve estar no formato: xx xxxxx-xxxx"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=13,
        verbose_name='Phone Number',
        help_text='Formato: xx xxxxx-xxxx'
    )
    second_phone_number = models.CharField(
        validators=[phone_regex],
        max_length=13,
        blank=True,
        verbose_name='Second Phone Number',
        help_text='Formato: xx xxxxx-xxxx'
    )
    whatsapp_opt_in = models.BooleanField(
        default=False,
        verbose_name='WhatsApp Opt-in',
        help_text='Candidate agreed to receive WhatsApp notifications'
    )
    whatsapp_opt_in_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='WhatsApp Opt-in Date',
        help_text='When candidate opted in to WhatsApp notifications'
    )
    
    date_of_birth = models.DateField(verbose_name='Date of Birth', null=True, blank=True)
    
    # Gender
    gender = models.CharField(
        max_length=30,
        verbose_name='Sexo',
        choices=[
            ('masculino', 'Masculino'),
            ('feminino', 'Feminino'),
            ('prefiro_nao_informar', 'Prefiro não informar'),
        ],
        blank=True,
        default=''
    )
    
    # Disability Information
    disability = models.CharField(
        max_length=50,
        verbose_name='Possui deficiência? (PCD)',
        choices=[
            ('sem_deficiencia', 'Sem deficiência'),
            ('fisica', 'Física'),
            ('auditiva', 'Auditiva'),
            ('visual', 'Visual'),
            ('mental', 'Mental'),
            ('multipla', 'Múltipla'),
            ('reabilitado', 'Reabilitado'),
        ],
        blank=True,
        default=''
    )
    
    # Transportation
    has_own_transportation = models.CharField(
        max_length=10,
        verbose_name='Possui transporte próprio?',
        choices=[
            ('sim', 'Sim'),
            ('nao', 'Não'),
        ],
        blank=True,
        default=''
    )
    
    # Address Information
    address = models.CharField(max_length=255, verbose_name='Street Address', blank=True)
    city = models.CharField(max_length=100, verbose_name='City', blank=True)
    state = models.CharField(max_length=100, verbose_name='State/Province', blank=True)
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code', blank=True)
    country = models.CharField(max_length=100, verbose_name='Country', default='USA')
    
    # Professional Information
    position_applied = models.CharField(max_length=200, verbose_name='Position Applied For', blank=True, default='')
    current_company = models.CharField(max_length=200, verbose_name='Current Company', blank=True)
    current_position = models.CharField(max_length=200, verbose_name='Current Position', blank=True)
    years_of_experience = models.PositiveIntegerField(verbose_name='Years of Experience', default=0, blank=True, null=True)
    
    # Indicação (Referral Information)
    has_relatives_in_company = models.CharField(
        max_length=10,
        verbose_name='Possui parentes ou amigos na empresa?',
        choices=[
            ('sim', 'Sim'),
            ('nao', 'Não'),
        ],
        blank=True,
        default=''
    )
    
    referred_by = models.CharField(
        max_length=200,
        verbose_name='Indicado Por',
        blank=True,
        help_text='Nome da pessoa que indicou'
    )
    
    how_found_vacancy = models.CharField(
        max_length=100,
        verbose_name='Como ficou sabendo da vaga?',
        choices=[
            ('facebook', 'Facebook'),
            ('indicacao_colaborador', 'Indicação de colaborador'),
            ('instagram', 'Instagram'),
            ('linkedin', 'LinkedIn'),
            ('sine', 'Sine'),
            ('outros', 'Outros'),
        ],
        blank=True,
        default=''
    )
    
    how_found_vacancy_other = models.CharField(
        max_length=200,
        verbose_name='Outros - Especificar',
        blank=True,
        help_text='Especifique se selecionou "Outros"'
    )
    
    worked_at_pinte_before = models.CharField(
        max_length=10,
        verbose_name='Já trabalhou na Pinte Pinturas antes?',
        choices=[
            ('sim', 'Sim'),
            ('nao', 'Não'),
        ],
        blank=True,
        default=''
    )
    
    # Education
    highest_education = models.CharField(
        max_length=100,
        verbose_name='Escolaridade',
        choices=[
            ('analfabeto', 'Analfabeto'),
            ('fundamental_incompleto', 'Ensino fundamental incompleto'),
            ('fundamental_completo', 'Ensino fundamental completo'),
            ('medio_incompleto', 'Ensino Médio incompleto'),
            ('medio_completo', 'Ensino Médio completo'),
            ('tecnica_incompleta', 'Educação Técnica incompleta'),
            ('tecnica_completa', 'Educação Técnica completa'),
            ('superior_incompleta', 'Educação Superior incompleta'),
            ('superior_completa', 'Educação Superior completa'),
        ],
        blank=True,
        default=''
    )
    
    # Informações Extras (Extra Information)
    currently_employed = models.CharField(
        max_length=10,
        verbose_name='Atualmente empregado',
        choices=[
            ('sim', 'Sim'),
            ('nao', 'Não'),
        ],
        blank=True,
        default=''
    )
    
    availability_start = models.CharField(
        max_length=20,
        verbose_name='Disponibilidade para início',
        choices=[
            ('imediato', 'De imediato'),
            ('15_dias', '15 dias'),
            ('30_dias', '30 dias'),
        ],
        blank=True,
        default=''
    )
    
    travel_availability = models.CharField(
        max_length=10,
        verbose_name='Disponibilidade para viagens',
        choices=[
            ('sim', 'Sim'),
            ('nao', 'Não'),
        ],
        blank=True,
        default=''
    )
    
    height_painting = models.CharField(
        max_length=100,
        verbose_name='Faz pintura em altura? Balancim/Cadeirinha/Andaimes',
        choices=[
            ('sim', 'Sim'),
            ('nao', 'Não'),
        ],
        blank=True,
        default=''
    )
    
    # Additional Information
    resume = models.FileField(upload_to='resumes/', verbose_name='Resume/CV', blank=True, null=True)
    photo = models.ImageField(upload_to='candidate_photos/', verbose_name='Foto do Candidato', blank=True, null=True)
    cover_letter = models.TextField(verbose_name='Cover Letter', blank=True)
    
    # Skills and Qualifications
    skills = models.TextField(verbose_name='Skills (comma-separated)', blank=True, help_text='e.g., Python, Django, JavaScript')
    certifications = models.TextField(verbose_name='Certifications', blank=True)
    
    # Availability
    available_start_date = models.DateField(verbose_name='Available Start Date', null=True, blank=True)
    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Expected Salary',
        null=True,
        blank=True,
        help_text='Annual salary expectation'
    )
    
    # Application Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Application Status'
    )
    
    # Scoring
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='Candidate Score',
        help_text='Objective score based on multiple criteria (0-100)'
    )
    score_breakdown = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Score Breakdown',
        help_text='Detailed breakdown of score by category'
    )
    score_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Score Last Updated',
        help_text='When the score was last calculated'
    )
    
    # Metadata
    applied_date = models.DateTimeField(auto_now_add=True, verbose_name='Application Date')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='Last Updated')
    notes = models.TextField(verbose_name='Internal Notes', blank=True, help_text='For employer use only')
    access_code = models.CharField(max_length=8, unique=True, blank=True, null=True, verbose_name='Access Code', help_text='Code for candidate to check application status')
    password_hash = models.CharField(max_length=128, blank=True, null=True, verbose_name='Password Hash')
    
    class Meta:
        ordering = ['-applied_date']
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'
    
    def __str__(self):
        return f"{self.full_name} - {self.position_applied}"
    
    def get_status_pt(self):
        """Get the Portuguese translation of the status."""
        return self.STATUS_TRANSLATIONS.get(self.status, self.status)
    
    def get_full_name(self):
        """Returns the candidate's full name."""
        return self.full_name
    
    def get_status_display_color(self):
        """Returns a color code for the status (useful for frontend)."""
        color_map = {
            'incomplete': '#FFD700',  # Gold
            'pending': '#FFA500',  # Orange
            'reviewing': '#0000FF',  # Blue
            'shortlisted': '#17A2B8',  # Cyan/Teal
            'interviewed': '#800080',  # Purple
            'accepted': '#008000',  # Green
            'rejected': '#FF0000',  # Red
        }
        return color_map.get(self.status, '#808080')
    
    def calculate_score(self):
        """
        Calculate and update the candidate's score using the scoring service.
        Returns the score data.
        """
        from ..scoring_service import CandidateScorer
        from django.utils import timezone
        
        score_data = CandidateScorer.calculate_score(self)
        self.score = score_data['total']
        self.score_breakdown = score_data['breakdown']
        self.score_updated_at = timezone.now()
        
        return score_data
    
    def get_score_grade(self):
        """Returns the letter grade for the current score."""
        from ..scoring_service import CandidateScorer
        return CandidateScorer._get_grade(float(self.score))
    
    def get_score_color(self):
        """Returns the color code for the current score."""
        from ..scoring_service import CandidateScorer
        return CandidateScorer.get_score_color(float(self.score))
    
    def _photo_variant_key(self, variant: str) -> str:
        """Return storage key for a variant based on original photo name.
        Example: candidate_photos/foo/bar.jpg -> candidate_photos/foo/bar_medium.jpg
        """
        if not self.photo:
            return ''
        base, _ext = os.path.splitext(self.photo.name)
        return f"{base}_{variant}.jpg"

    def _generate_photo_variant(self, max_size: int, variant: str, quality: int = 82) -> None:
        """Open original from storage, downscale, strip EXIF, convert to JPEG, and upload variant."""
        if not self.photo:
            return
        orig_name = self.photo.name
        storage = self.photo.storage or default_storage
        try:
            with storage.open(orig_name, 'rb') as f:
                im = Image.open(f)
                # Convert PNG with alpha to RGB over white background
                if im.mode in ('RGBA', 'LA'):
                    bg = Image.new('RGB', im.size, (255, 255, 255))
                    alpha = im.split()[-1]
                    bg.paste(im, mask=alpha)
                    im = bg
                elif im.mode != 'RGB':
                    im = im.convert('RGB')
                # Downscale maintaining aspect ratio
                im.thumbnail((max_size, max_size), Image.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
                buf.seek(0)
                variant_key = self._photo_variant_key(variant)
                storage.save(variant_key, ContentFile(buf.read()))
        except Exception:
            # Fail silently to not block saving the model
            pass

    def save(self, *args, **kwargs):
        """Generate access code if not exists and create photo variants after save."""
        if not self.access_code:
            import random
            import string
            # Generate a unique 8-character code
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not Candidate.objects.filter(access_code=code).exists():
                    self.access_code = code
                    break

        creating = self._state.adding
        old_photo_name = None
        if not creating and self.pk:
            try:
                old = Candidate.objects.only('photo').get(pk=self.pk)
                old_photo_name = old.photo.name if old.photo else None
            except Candidate.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # If photo newly set or changed, generate variants
        if self.photo and (creating or self.photo.name != old_photo_name):
            # medium ~1200px, thumb ~400px
            self._generate_photo_variant(1200, 'medium')
            self._generate_photo_variant(400, 'thumb')


class ProfessionalExperience(models.Model):
    """
    Model to store professional experience information for candidates.
    A candidate can have multiple professional experiences.
    """
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='professional_experiences',
        verbose_name='Candidato'
    )
    
    empresa = models.CharField(
        max_length=200,
        verbose_name='Empresa',
        help_text='Nome da empresa onde trabalhou',
        blank=True
    )
    
    cargo = models.CharField(
        max_length=200,
        verbose_name='Cargo',
        help_text='Cargo ocupado na empresa'
    )
    
    descricao_atividades = models.TextField(
        verbose_name='Descrição das Atividades',
        blank=True,
        help_text='Descreva as principais atividades realizadas'
    )
    
    data_admissao = models.DateField(
        verbose_name='Data de Admissão',
        null=True,
        blank=True
    )
    
    data_desligamento = models.DateField(
        verbose_name='Data de Desligamento',
        null=True,
        blank=True
    )
    
    motivo_saida = models.TextField(
        verbose_name='Motivo da saída',
        blank=True,
        help_text='Explique o motivo da saída da empresa'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_desligamento', '-data_admissao']
        verbose_name = 'Experiência Profissional'
        verbose_name_plural = 'Experiências Profissionais'
    
    def __str__(self):
        return f"{self.cargo} - {self.empresa}"
    
    def get_idle_time_days(self):
        """
        Calculate the number of days since the last job ended (data_desligamento).
        Returns None if there's no end date (still working) or if the date is invalid.
        """
        from datetime import date
        
        if not self.data_desligamento:
            return None
        
        today = date.today()
        if self.data_desligamento > today:
            return None
        
        delta = today - self.data_desligamento
        return delta.days
    
    def get_idle_time_formatted(self):
        """
        Returns a formatted string of the idle time (e.g., "2 anos e 3 meses", "5 meses", "15 dias").
        """
        days = self.get_idle_time_days()
        
        if days is None:
            return None
        
        if days == 0:
            return "Hoje"
        
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        remaining_days = remaining_days % 30
        
        parts = []
        
        if years > 0:
            parts.append(f"{years} ano{'s' if years != 1 else ''}")
        
        if months > 0:
            parts.append(f"{months} {'meses' if months != 1 else 'mês'}")
        
        if not parts and remaining_days > 0:
            parts.append(f"{remaining_days} dia{'s' if remaining_days != 1 else ''}")
        
        return " e ".join(parts) if parts else "Hoje"
