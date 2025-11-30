from django.core.management.base import BaseCommand
from apps.candidate.models import CandidateQuestionnaireResponse, CandidateSelectedOption
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fix missing selected options for questionnaire responses'

    def add_arguments(self, parser):
        parser.add_argument('response_id', type=int, help='Response ID to fix')
        parser.add_argument('option_id', type=int, help='Option ID that was selected')

    def handle(self, *args, **options):
        response_id = options['response_id']
        option_id = options['option_id']

        try:
            response = CandidateQuestionnaireResponse.objects.get(id=response_id)
            self.stdout.write(f'Response: {response.candidate.full_name} - {response.template.title}')
            
            question = response.template.questions.first()
            if not question:
                self.stdout.write(self.style.ERROR('No questions found in template'))
                return
            
            option = question.options.get(id=option_id)
            self.stdout.write(f'Question: {question.question_text[:60]}...')
            self.stdout.write(f'Option: {option.option_text[:60]}... ({option.option_points} pts)')
            
            # Delete existing selections for this question
            deleted = CandidateSelectedOption.objects.filter(
                response=response,
                question=question
            ).delete()
            if deleted[0] > 0:
                self.stdout.write(f'Deleted {deleted[0]} existing selections')
            
            # Create new selection
            selection = CandidateSelectedOption.objects.create(
                response=response,
                question=question,
                option=option
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created selection ID: {selection.id}'))
            
            # Recalculate score
            all_options = list(question.options.all())
            max_points = max((opt.option_points or Decimal('0')) for opt in all_options)
            selected_points = option.option_points or Decimal('0')
            
            if max_points > 0:
                fraction = Decimal(selected_points) / Decimal(max_points)
                response.score = fraction * question.points
                response.save()
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Score updated: {response.score}/{response.max_score} '
                    f'({selected_points}/{max_points} × {question.points})'
                ))
            
            # Verify
            count = response.selected_options.count()
            self.stdout.write(self.style.SUCCESS(f'✓ Total selected options: {count}'))
            
        except CandidateQuestionnaireResponse.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Response {response_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            import traceback
            traceback.print_exc()
