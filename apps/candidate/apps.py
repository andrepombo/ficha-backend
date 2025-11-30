from django.apps import AppConfig


class CandidateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.candidate'
    verbose_name = 'Candidate Management'
    
    def ready(self):
        """Import signals when the app is ready."""
        import apps.candidate.signals  # noqa
