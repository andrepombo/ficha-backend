from django.db import models
from django.contrib.auth.models import User
from .candidate import Candidate


class Interview(models.Model):
    """
    Model to store interview scheduling information for candidates.
    """
    
    # Interview status choices
    STATUS_CHOICES = [
        ('scheduled', 'Agendada'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
        ('rescheduled', 'Reagendada'),
        ('no_show', 'Candidato não compareceu'),
    ]
    
    # Interview type choices
    TYPE_CHOICES = [
        ('phone', 'Telefone'),
        ('video', 'Vídeo'),
        ('in_person', 'Presencial'),
        ('technical', 'Técnica'),
        ('hr', 'RH'),
    ]
    
    # Core fields
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='interviews',
        verbose_name='Candidato'
    )
    
    interviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interviews_conducted',
        verbose_name='Entrevistador'
    )
    
    # Interview details
    title = models.CharField(
        max_length=200,
        verbose_name='Título da Entrevista',
        help_text='Ex: Entrevista Técnica - Desenvolvedor'
    )
    
    interview_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='video',
        verbose_name='Tipo de Entrevista'
    )
    
    scheduled_date = models.DateField(
        verbose_name='Data da Entrevista'
    )
    
    scheduled_time = models.TimeField(
        verbose_name='Horário da Entrevista'
    )
    
    duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name='Duração (minutos)',
        help_text='Duração estimada da entrevista em minutos'
    )
    
    location = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Local/Link',
        help_text='Endereço físico ou link da reunião online'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Detalhes adicionais sobre a entrevista'
    )
    
    # Status and feedback
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Status'
    )
    
    feedback = models.TextField(
        blank=True,
        verbose_name='Feedback',
        help_text='Feedback do entrevistador após a entrevista'
    )
    
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Avaliação',
        help_text='Avaliação de 1 a 5'
    )
    
    # Notification flags
    candidate_notified = models.BooleanField(
        default=False,
        verbose_name='Candidato Notificado'
    )
    
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Lembrete Enviado'
    )
    
    # WhatsApp notification tracking
    whatsapp_sent = models.BooleanField(
        default=False,
        verbose_name='WhatsApp Enviado',
        help_text='Indica se a notificação via WhatsApp foi enviada'
    )
    
    whatsapp_message_sid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='WhatsApp Message SID',
        help_text='ID da mensagem para rastreamento'
    )
    
    whatsapp_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='WhatsApp Enviado em',
        help_text='Data e hora do envio da notificação via WhatsApp'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interviews_created',
        verbose_name='Criado por'
    )
    
    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']
        verbose_name = 'Entrevista'
        verbose_name_plural = 'Entrevistas'
    
    def __str__(self):
        return f"{self.title} - {self.candidate.full_name} ({self.scheduled_date})"
    
    def get_status_color(self):
        """Returns a color code for the status."""
        color_map = {
            'scheduled': '#3B82F6',  # Blue
            'completed': '#10B981',  # Green
            'cancelled': '#EF4444',  # Red
            'rescheduled': '#F59E0B',  # Amber
            'no_show': '#6B7280',  # Gray
        }
        return color_map.get(self.status, '#808080')
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically update candidate status when interview is scheduled.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # If this is a new scheduled interview, update candidate status to 'shortlisted'
        if is_new and self.status == 'scheduled':
            candidate = self.candidate
            # Only update if candidate is still in pending or reviewing status
            if candidate.status in ['pending', 'reviewing']:
                candidate.status = 'shortlisted'
                candidate.save(update_fields=['status'])
        
        # If interview is completed, update candidate status to 'interviewed'
        elif self.status == 'completed' and self.candidate.status == 'shortlisted':
            candidate = self.candidate
            candidate.status = 'interviewed'
            candidate.save(update_fields=['status'])
