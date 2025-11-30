"""
Work Card (Carteira de Trabalho) model for storing multiple document files per candidate.
"""
from django.db import models
from django.core.validators import FileExtensionValidator
import os


class WorkCard(models.Model):
    """
    Model to store Work Card (Carteira de Trabalho) documents.
    Supports multiple file uploads per candidate.
    """
    candidate = models.ForeignKey(
        'Candidate',
        on_delete=models.CASCADE,
        related_name='work_cards',
        verbose_name='Candidato'
    )
    file = models.FileField(
        upload_to='work_cards/',
        verbose_name='Arquivo da Carteira de Trabalho',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 
                    'bmp', 'tiff', 'txt', 'rtf', 'odt', 'xls', 'xlsx'
                ]
            )
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Upload')
    file_name = models.CharField(max_length=255, blank=True, verbose_name='Nome do Arquivo')
    
    class Meta:
        verbose_name = 'Carteira de Trabalho'
        verbose_name_plural = 'Carteiras de Trabalho'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.file_name or 'Carteira de Trabalho'}"
    
    def save(self, *args, **kwargs):
        # Auto-populate file_name from the uploaded file if not set
        if not self.file_name and self.file:
            self.file_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """Returns the file extension."""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''
    
    def get_file_size(self):
        """Returns the file size in bytes."""
        if self.file:
            return self.file.size
        return 0
