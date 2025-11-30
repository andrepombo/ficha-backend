"""
Management command to calculate or recalculate scores for all candidates.

Usage:
    python manage.py calculate_scores
    python manage.py calculate_scores --force  # Recalculate even if score exists
"""

from django.core.management.base import BaseCommand
from apps.candidate.models import Candidate
from apps.candidate.scoring_service import CandidateScorer


class Command(BaseCommand):
    help = 'Calculate scores for all candidates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recalculate scores even if they already exist',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        candidates = Candidate.objects.all()
        total = candidates.count()
        
        self.stdout.write(f'Processing {total} candidates...\n')
        
        updated = 0
        skipped = 0
        errors = 0
        
        for i, candidate in enumerate(candidates, 1):
            try:
                # Skip if score exists and not forcing
                if not force and candidate.score > 0:
                    skipped += 1
                    if i % 10 == 0:
                        self.stdout.write(f'Progress: {i}/{total} (Updated: {updated}, Skipped: {skipped})')
                    continue
                
                # Calculate score
                score_data = candidate.calculate_score()
                candidate.save(update_fields=['score', 'score_breakdown', 'score_updated_at'])
                
                updated += 1
                
                # Show progress every 10 candidates
                if i % 10 == 0:
                    self.stdout.write(f'Progress: {i}/{total} (Updated: {updated}, Skipped: {skipped})')
                
                # Show individual result
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ {candidate.full_name}: {score_data["total"]:.1f} ({score_data["grade"]})'
                    )
                )
                
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error processing candidate {candidate.id}: {str(e)}')
                )
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully updated: {updated}'))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'⊘ Skipped (already scored): {skipped}'))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f'✗ Errors: {errors}'))
        self.stdout.write('='*60 + '\n')
        
        if force:
            self.stdout.write(self.style.SUCCESS('All candidate scores have been recalculated!'))
        else:
            self.stdout.write(self.style.SUCCESS('Candidate scores have been calculated!'))
            if skipped > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nTip: Use --force to recalculate scores for all candidates, '
                        f'including those already scored.'
                    )
                )
