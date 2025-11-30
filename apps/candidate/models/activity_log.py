from django.db import models
from django.contrib.auth.models import User
from .candidate import Candidate
from .interview import Interview


class ActivityLog(models.Model):
    """
    Model to track activity logs for candidate-related actions.
    """
    
    # Action types
    ACTION_TYPES = [
        ('candidate_created', 'Candidato Criado'),
        ('candidate_updated', 'Candidato Atualizado'),
        ('status_changed', 'Status Alterado'),
        ('interview_scheduled', 'Entrevista Agendada'),
        ('interview_updated', 'Entrevista Atualizada'),
        ('interview_cancelled', 'Entrevista Cancelada'),
        ('interview_completed', 'Entrevista Concluída'),
        ('interview_rescheduled', 'Entrevista Reagendada'),
        ('score_updated', 'Pontuação Atualizada'),
        ('note_added', 'Nota Adicionada'),
    ]
    
    # Core fields
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
        verbose_name='Candidato',
        null=True,
        blank=True
    )
    
    # Store candidate name for historical reference (in case candidate is deleted)
    candidate_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nome do Candidato',
        help_text='Nome do candidato no momento da ação'
    )
    
    interview = models.ForeignKey(
        Interview,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
        verbose_name='Entrevista',
        null=True,
        blank=True
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='Usuário'
    )
    
    # Action details
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPES,
        verbose_name='Tipo de Ação'
    )
    
    description = models.TextField(
        verbose_name='Descrição',
        help_text='Descrição detalhada da ação realizada'
    )
    
    # Change tracking (for status changes and updates)
    old_value = models.TextField(
        blank=True,
        null=True,
        verbose_name='Valor Anterior',
        help_text='Valor antes da alteração'
    )
    
    new_value = models.TextField(
        blank=True,
        null=True,
        verbose_name='Novo Valor',
        help_text='Valor após a alteração'
    )
    
    # Metadata
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data e Hora'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='User Agent'
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log de Atividade'
        verbose_name_plural = 'Logs de Atividade'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['action_type']),
            models.Index(fields=['candidate']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        # Use stored candidate_name if candidate was deleted, otherwise use candidate.full_name
        if self.candidate:
            target = self.candidate.full_name
        elif self.candidate_name:
            target = f"{self.candidate_name} (deletado)"
        elif self.interview:
            target = f"Entrevista {self.interview.pk}"
        else:
            target = "N/A"
        return f"{self.get_action_type_display()} - {target} ({self.timestamp.strftime('%d/%m/%Y %H:%M')})"
    
    @classmethod
    def log_action(cls, action_type, description, candidate=None, interview=None, user=None, 
                   old_value=None, new_value=None, request=None):
        """
        Helper method to create activity log entries.
        """
        ip_address = None
        user_agent = None
        
        if request:
            # Get IP address from request
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Get user agent from request
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Store candidate name for historical reference
        candidate_name = candidate.full_name if candidate else None
        
        return cls.objects.create(
            action_type=action_type,
            description=description,
            candidate=candidate,
            candidate_name=candidate_name,
            interview=interview,
            user=user,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )
