from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.candidate.models import Candidate, QuestionnaireTemplate, Question, ProfessionalExperience
from apps.candidate.api_views.questionnaire_views import CandidateQuestionnaireResponseViewSet
from rest_framework.request import Request
from django.http import HttpRequest
from io import BytesIO
import random
import json
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Seed candidates with randomized questionnaire submissions without deleting existing data.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=30, help='Number of candidates to create')
        parser.add_argument('--position-key', type=str, default=None, help='Restrict to templates of a given position_key')
        parser.add_argument('--submit-forms', action='store_true', help='Also submit questionnaire answers for each candidate (default: true)')
        parser.add_argument('--no-submit-forms', action='store_true', help='Do not submit questionnaire answers')
        parser.add_argument('--delete-existing', action='store_true', help='Delete existing candidates before seeding (DANGEROUS)')

    def handle(self, *args, **options):
        count = options['count']
        position_key_filter = options.get('position_key')
        # Default behavior: submit forms unless explicitly disabled
        no_submit = options.get('no_submit_forms', False)
        submit_forms = options.get('submit_forms', False) or not no_submit
        delete_existing = options.get('delete_existing', False)

        self.stdout.write(self.style.WARNING(f"Seeding {count} candidates (submit forms: {submit_forms})"))

        if delete_existing:
            self.stdout.write(self.style.WARNING('Deleting existing candidates (and cascading related data)...'))
            deleted_count, _ = Candidate.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} candidate-related records'))

        # Prepare data sources
        first_names = [
            'João', 'Maria', 'José', 'Ana', 'Pedro', 'Carla', 'Lucas', 'Juliana',
            'Carlos', 'Fernanda', 'Rafael', 'Patricia', 'Bruno', 'Amanda', 'Felipe',
            'Camila', 'Rodrigo', 'Beatriz', 'Gustavo', 'Larissa', 'Thiago', 'Gabriela',
            'Diego', 'Mariana', 'Vitor', 'Isabela', 'Marcelo', 'Carolina', 'André',
            'Letícia', 'Ricardo', 'Vanessa', 'Leonardo', 'Renata', 'Fábio', 'Daniela',
            'Matheus', 'Aline', 'Paulo', 'Cristina'
        ]
        last_names = [
            'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves',
            'Pereira', 'Lima', 'Gomes', 'Costa', 'Ribeiro', 'Martins', 'Carvalho',
            'Rocha', 'Almeida', 'Nascimento', 'Araújo', 'Melo', 'Barbosa'
        ]
        positions = [
            'Pintor Residencial', 'Pintor Industrial', 'Pintor Automotivo',
            'Auxiliar de Pintura', 'Pintor de Obras', 'Pintor Predial'
        ]
        cities = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Salvador']
        statuses = ['pending', 'reviewing', 'shortlisted', 'interviewed', 'accepted', 'rejected']
        states = ['SP', 'RJ', 'MG', 'PR', 'RS', 'DF', 'BA', 'CE', 'PE', 'AM']
        companies = [
            'Pinte Pinturas', 'Cores & Tintas Ltda', 'Pintura Express',
            'Acabamento Perfeito', 'Tintas Profissionais', 'Arte em Pintura',
            'Pintura Total', 'Reforma & Pintura', 'Construtora ABC', 'Construtora XYZ'
        ]
        skills_list = [
            'Pintura residencial, Pintura comercial, Acabamento fino',
            'Pintura industrial, Pintura eletrostática, Segurança do trabalho',
            'Textura, Grafiato, Pintura decorativa',
            'Pintura automotiva, Funilaria, Polimento',
            'Pintura de fachadas, Trabalho em altura, Rapel',
            'Massa corrida, Gesso, Acabamento',
            'Pintura a rolo, Pintura a pistola, Verniz',
            'Impermeabilização, Pintura epóxi, Pintura de piso',
            'Stencil, Arte decorativa, Pintura artística',
            'Lixamento, Preparação de superfície, Aplicação de primer'
        ]
        education_levels = [
            'analfabeto', 'fundamental_incompleto', 'fundamental_completo',
            'medio_incompleto', 'medio_completo', 'tecnica_incompleta',
            'tecnica_completa', 'superior_incompleta', 'superior_completa'
        ]
        how_found_opts = ['facebook', 'indicacao_colaborador', 'instagram', 'linkedin', 'sine', 'outros']
        availability_opts = ['imediato', '15_dias', '30_dias']

        # Load active questionnaire templates
        templates_qs = QuestionnaireTemplate.objects.filter(is_active=True)
        if position_key_filter:
            templates_qs = templates_qs.filter(position_key=position_key_filter)
        templates = list(templates_qs.prefetch_related('questions__options'))
        if submit_forms and not templates:
            self.stdout.write(self.style.WARNING('No active questionnaire templates found; will create candidates without submissions.'))
            submit_forms = False

        created = 0
        base_datetime = datetime.now()
        for i in range(count):
            # Random application date within last 6 months
            days_ago = random.randint(0, 180)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            applied_date = base_datetime - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

            # Generate unique-ish phone and CPF under validators
            ddd = random.randint(11, 99)
            phone = f"{ddd:02d} {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"
            cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"

            full_name = f"{random.choice(first_names)} {random.choice(last_names)}"

            has_relatives = random.choice(['sim', 'nao'])
            referred_by_name = f"{random.choice(first_names)} {random.choice(last_names)}" if has_relatives == 'sim' else ''
            how_found_val = random.choice(how_found_opts)
            skills_val = random.choice(skills_list)

            candidate = Candidate.objects.create(
                full_name=full_name,
                email=f"{full_name.lower().replace(' ', '.')}+{timezone.now().timestamp():.0f}@example.com",
                phone_number=phone,
                cpf=cpf,
                date_of_birth=f"{random.randint(1980, 2003)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                gender=random.choice(['masculino', 'feminino', 'prefiro_nao_informar']),
                disability=random.choice(['sem_deficiencia', 'fisica', 'auditiva', 'visual', 'mental', 'multipla', 'reabilitado']),
                has_own_transportation=random.choice(['sim', 'nao']),
                address=f"Rua {random.choice(['das Flores', 'Principal', 'Central', 'do Comércio'])}, {random.randint(1, 999)}",
                city=random.choice(cities),
                state=random.choice(states),
                postal_code=f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                country='Brasil',
                position_applied=random.choice(positions),
                current_company=random.choice(['Pinturas ABC', 'Tintas XYZ', 'Reformas 123', 'Autônomo', 'Não informado']),
                current_position=random.choice(['Pintor', 'Auxiliar', 'Ajudante', 'Não informado']),
                years_of_experience=random.randint(0, 20),
                has_relatives_in_company=has_relatives,
                referred_by=referred_by_name,
                how_found_vacancy=how_found_val,
                how_found_vacancy_other='Indicação de amigo' if how_found_val == 'outros' else '',
                worked_at_pinte_before=random.choice(['sim', 'nao']),
                highest_education=random.choice(education_levels),
                currently_employed=random.choice(['sim', 'nao']),
                availability_start=random.choice(availability_opts),
                travel_availability=random.choice(['sim', 'nao']),
                height_painting=random.choice(['sim', 'nao']),
                skills=skills_val,
                certifications='NR-35 (Trabalho em Altura)' if 'altura' in skills_val.lower() else '',
                available_start_date=(base_datetime + timedelta(days=random.randint(3, 60))).date(),
                expected_salary=random.randint(1800, 5000),
                status=random.choice(statuses),
                cover_letter=f"Tenho experiência em {skills_val.lower()} e me interesso pela vaga. Posso iniciar em breve.",
                notes='Seeded candidate for testing'
            )

            # Create 1-3 professional experiences for each candidate
            num_experiences = random.randint(1, 3)
            motivos_saida = [
                'Busca por novos desafios',
                'Melhor oportunidade',
                'Fim do contrato',
                'Mudança de cidade',
                'Crescimento profissional'
            ]
            for _ in range(num_experiences):
                exp_company = random.choice(companies)
                exp_position = random.choice([
                    'Pintor', 'Pintor Industrial', 'Pintor Residencial', 'Pintor Comercial',
                    'Ajudante de Pintor', 'Supervisor de Pintura', 'Pintor Automotivo',
                    'Pintor de Fachadas', 'Aplicador de Textura'
                ])
                years_ago_start = random.randint(1, 15)
                years_ago_end = random.randint(0, years_ago_start - 1) if years_ago_start > 1 else 0
                exp_start_date = datetime.now().date() - timedelta(days=years_ago_start * 365)
                exp_end_date = (datetime.now().date() - timedelta(days=years_ago_end * 365)) if years_ago_end > 0 else None

                ProfessionalExperience.objects.create(
                    candidate=candidate,
                    empresa=exp_company,
                    cargo=exp_position,
                    descricao_atividades=f'Atuei como {exp_position} realizando {skills_val.split(",")[0].lower()}.',
                    data_admissao=exp_start_date,
                    data_desligamento=exp_end_date,
                    motivo_saida=random.choice(motivos_saida) if exp_end_date else ''
                )
            # Update applied date bypassing auto_now_add
            Candidate.objects.filter(id=candidate.id).update(applied_date=applied_date)

            created += 1

            if submit_forms:
                # Submit for each template related to the candidate's position_key if any, else all
                candidate_templates = [t for t in templates if (not position_key_filter or t.position_key == position_key_filter)]
                # If templates are specific to positions, you may want to filter by t.position_key matching candidate.position_applied key mapping
                for template in candidate_templates:
                    answers_payload = []
                    for q in template.questions.all():
                        option_ids = [opt.id for opt in q.options.all()]
                        if not option_ids:
                            continue
                        if getattr(q, 'question_type', 'single_select') == 'multi_select':
                            k = random.randint(1, min(3, len(option_ids)))
                            selected = random.sample(option_ids, k=k)
                        else:
                            selected = [random.choice(option_ids)]
                        answers_payload.append({
                            'question_id': q.id,
                            'selected_option_ids': selected,
                        })

                    if not answers_payload:
                        continue

                    submission_data = {
                        'candidate_id': candidate.id,
                        'template_id': int(template.id),
                        'answers': answers_payload,
                    }

                    # Build DRF request similar to the application flow
                    mock_request = HttpRequest()
                    mock_request.method = 'POST'
                    mock_request.META['CONTENT_TYPE'] = 'application/json'
                    body = json.dumps(submission_data).encode('utf-8')
                    mock_request._body = body
                    mock_request._stream = BytesIO(body)
                    drf_request = Request(mock_request)
                    drf_request._full_data = submission_data

                    viewset = CandidateQuestionnaireResponseViewSet()
                    viewset.request = drf_request
                    try:
                        resp = viewset.submit(drf_request)
                        if resp.status_code not in (201, 200):
                            self.stdout.write(self.style.WARNING(f"Submission for candidate {candidate.id}, template {template.id} returned status {resp.status_code}: {getattr(resp, 'data', None)}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to submit template {template.id} for candidate {candidate.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Created {created} candidates"))
