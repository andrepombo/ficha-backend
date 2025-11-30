from django.db import models
from django.contrib.auth.models import User


class ScoringWeight(models.Model):
    """
    Model to store scoring configuration weights.
    Only one active configuration should exist at a time.
    """
    # Experience & Skills
    years_of_experience = models.IntegerField(
        default=27,
        verbose_name='Anos de Experiência',
        help_text='Pontos máximos para anos de experiência'
    )
    idle_time = models.IntegerField(
        default=5,
        verbose_name='Tempo Parado',
        help_text='Pontos máximos para tempo parado (desemprego)'
    )
    worked_at_pinte_before = models.IntegerField(
        default=0,
        verbose_name='Trabalhou na Pinte Antes',
        help_text='Pontos máximos para experiência prévia na empresa'
    )
    has_relatives_in_company = models.IntegerField(
        default=0,
        verbose_name='Parentes/Amigos na Empresa',
        help_text='Pontos máximos para ter parentes ou amigos na empresa'
    )
    referred_by = models.IntegerField(
        default=0,
        verbose_name='Indicado Por',
        help_text='Pontos máximos para ser indicado por alguém'
    )
    
    # Education & Qualifications
    education_level = models.IntegerField(
        default=16,
        verbose_name='Nível Educacional',
        help_text='Pontos máximos para nível educacional'
    )
    courses = models.IntegerField(
        default=0,
        verbose_name='Cursos Adicionais',
        help_text='Pontos máximos para cursos adicionais'
    )
    skills = models.IntegerField(
        default=2,
        verbose_name='Habilidades',
        help_text='Pontos máximos para habilidades listadas'
    )
    certifications = models.IntegerField(
        default=0,
        verbose_name='Certificações',
        help_text='Pontos máximos para certificações'
    )
    
    # Availability & Logistics
    immediate_availability = models.IntegerField(
        default=5,
        verbose_name='Disponibilidade Imediata',
        help_text='Pontos máximos para disponibilidade imediata'
    )
    own_transportation = models.IntegerField(
        default=5,
        verbose_name='Transporte Próprio',
        help_text='Pontos máximos para transporte próprio'
    )
    travel_availability = models.IntegerField(
        default=5,
        verbose_name='Disponibilidade para Viagens',
        help_text='Pontos máximos para disponibilidade de viagens'
    )
    height_painting = models.IntegerField(
        default=5,
        verbose_name='Pintura em Altura',
        help_text='Pontos máximos para pintura em altura'
    )
    
    # Interview Performance
    average_rating = models.IntegerField(
        default=30,
        verbose_name='Avaliação Média',
        help_text='Pontos máximos para avaliação média de entrevistas'
    )
    
    # Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Indica se esta é a configuração ativa'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Criado por'
    )
    
    class Meta:
        verbose_name = 'Configuração de Pontuação'
        verbose_name_plural = 'Configurações de Pontuação'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Configuração de Pontuação ({'Ativa' if self.is_active else 'Inativa'}) - {self.created_at.strftime('%d/%m/%Y')}"
    
    def get_total_points(self):
        """Calculate total points across all categories."""
        return (
            self.years_of_experience + self.idle_time +
            self.education_level + self.courses + self.skills + self.certifications +
            self.immediate_availability + self.own_transportation + 
            self.travel_availability + self.height_painting +
            self.average_rating
        )
    
    def to_dict(self):
        """Convert to dictionary format for API responses."""
        return {
            'experience_skills': {
                'years_of_experience': self.years_of_experience,
                'idle_time': self.idle_time,
                'worked_at_pinte_before': self.worked_at_pinte_before,
                'has_relatives_in_company': self.has_relatives_in_company,
                'referred_by': self.referred_by,
            },
            'education': {
                'education_level': self.education_level,
                'courses': self.courses,
                'skills': self.skills,
                'certifications': self.certifications,
            },
            'availability_logistics': {
                'immediate_availability': self.immediate_availability,
                'own_transportation': self.own_transportation,
                'travel_availability': self.travel_availability,
                'height_painting': self.height_painting,
            },
            'interview_performance': {
                'average_rating': self.average_rating,
            }
        }
    
    @classmethod
    def get_active_config(cls):
        """Get the active scoring configuration."""
        config = cls.objects.filter(is_active=True).first()
        if not config:
            # Create default configuration if none exists
            config = cls.objects.create(is_active=True)
        return config
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one active configuration exists."""
        if self.is_active:
            # Deactivate all other configurations
            ScoringWeight.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
