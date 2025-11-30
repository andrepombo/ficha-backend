from django.core.management.base import BaseCommand
from apps.candidate.models import Candidate, ProfessionalExperience
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Creates 20 test candidates for testing purposes'

    def handle(self, *args, **kwargs):
        # Sample data for generating realistic test candidates
        first_names = [
            'João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Juliana', 'Lucas', 'Fernanda',
            'Rafael', 'Camila', 'Bruno', 'Beatriz', 'Felipe', 'Larissa', 'Gustavo',
            'Patricia', 'Rodrigo', 'Amanda', 'Thiago', 'Gabriela'
        ]
        
        last_names = [
            'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves',
            'Pereira', 'Lima', 'Gomes', 'Costa', 'Ribeiro', 'Martins', 'Carvalho',
            'Rocha', 'Almeida', 'Nascimento', 'Araújo', 'Melo', 'Barbosa'
        ]
        
        positions = [
            'Pintor', 'Pintor Industrial', 'Pintor Residencial', 'Pintor Comercial',
            'Ajudante de Pintor', 'Mestre de Obras', 'Supervisor de Pintura',
            'Pintor Automotivo', 'Pintor de Fachadas', 'Aplicador de Textura'
        ]
        
        cities = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre',
            'Brasília', 'Salvador', 'Fortaleza', 'Recife', 'Manaus'
        ]
        
        states = [
            'SP', 'RJ', 'MG', 'PR', 'RS', 'DF', 'BA', 'CE', 'PE', 'AM'
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
        
        companies = [
            'Pinte Pinturas', 'Cores & Tintas Ltda', 'Pintura Express',
            'Acabamento Perfeito', 'Tintas Profissionais', 'Arte em Pintura',
            'Pintura Total', 'Reforma & Pintura', 'Autônomo', 'Construtora ABC'
        ]
        
        statuses = ['pending', 'reviewing', 'interviewed', 'accepted', 'rejected']
        
        education_levels = [
            'analfabeto', 'fundamental_incompleto', 'fundamental_completo',
            'medio_incompleto', 'medio_completo', 'tecnica_incompleta',
            'tecnica_completa', 'superior_incompleta', 'superior_completa'
        ]
        
        genders = ['masculino', 'feminino', 'prefiro_nao_informar']
        disabilities = ['sem_deficiencia', 'fisica', 'auditiva', 'visual']
        yes_no = ['sim', 'nao']
        how_found = ['facebook', 'indicacao_colaborador', 'instagram', 'linkedin', 'sine', 'outros']
        availability_options = ['imediato', '15_dias', '30_dias']
        
        # Clear ALL existing candidates
        deleted_count = Candidate.objects.all().delete()[0]
        if deleted_count > 0:
            self.stdout.write(self.style.WARNING(f'Cleared {deleted_count} existing candidates'))
        
        created_count = 0
        
        for i in range(20):
            # Generate random data
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"
            
            # Generate CPF (format: xxx.xxx.xxx-xx)
            cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
            
            # Generate email
            email = f"{first_name.lower()}.{last_name.lower()}{i}@email.com"
            
            # Generate phone (format: xx xxxxx-xxxx)
            phone = f"{random.randint(11, 99)} {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"
            
            # Generate date of birth (between 18 and 60 years ago)
            days_ago = random.randint(18*365, 60*365)
            date_of_birth = datetime.now().date() - timedelta(days=days_ago)
            
            # Address information
            city_index = random.randint(0, len(cities) - 1)
            city = cities[city_index]
            state = states[city_index]
            address = f"Rua {random.choice(['das Flores', 'Principal', 'do Comércio', 'Central', 'da Paz'])} {random.randint(1, 999)}"
            postal_code = f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
            
            # Professional information
            position_applied = random.choice(positions)
            current_company = random.choice(companies)
            current_position = random.choice(positions)
            years_of_experience = random.randint(0, 25)
            
            # Education
            highest_education = random.choice(education_levels)
            
            # Skills
            skills = random.choice(skills_list)
            
            # Availability
            available_start_date = datetime.now().date() + timedelta(days=random.randint(1, 90))
            expected_salary = random.randint(1800, 5000)
            
            # Status
            status = random.choice(statuses)
            
            # Cover letter
            cover_letter = f"Prezados, tenho {years_of_experience} anos de experiência na área de pintura e gostaria de me candidatar para a vaga de {position_applied}. Possuo habilidades em {skills.lower()}. Estou disponível para começar em {available_start_date.strftime('%d/%m/%Y')}."
            
            # Generate new field values
            gender = random.choice(genders)
            disability = random.choice(disabilities)
            has_transportation = random.choice(yes_no)
            has_relatives = random.choice(yes_no)
            referred_by_name = f"{random.choice(first_names)} {random.choice(last_names)}" if has_relatives == 'sim' else ''
            how_found_vacancy = random.choice(how_found)
            worked_before = random.choice(yes_no)
            currently_employed = random.choice(yes_no)
            availability_start = random.choice(availability_options)
            travel_availability = random.choice(yes_no)
            height_painting = random.choice(yes_no)
            
            try:
                # Create candidate first
                candidate = Candidate.objects.create(
                    full_name=full_name,
                    cpf=cpf,
                    email=email,
                    phone_number=phone,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    disability=disability,
                    has_own_transportation=has_transportation,
                    address=address,
                    city=city,
                    state=state,
                    postal_code=postal_code,
                    country='Brasil',
                    position_applied=position_applied,
                    current_company=current_company,
                    current_position=current_position,
                    years_of_experience=years_of_experience,
                    has_relatives_in_company=has_relatives,
                    referred_by=referred_by_name,
                    how_found_vacancy=how_found_vacancy,
                    how_found_vacancy_other='Indicação de amigo' if how_found_vacancy == 'outros' else '',
                    worked_at_pinte_before=worked_before,
                    highest_education=highest_education,
                    currently_employed=currently_employed,
                    availability_start=availability_start,
                    travel_availability=travel_availability,
                    height_painting=height_painting,
                    skills=skills,
                    certifications='NR-35 (Trabalho em Altura)' if 'altura' in skills.lower() else '',
                    available_start_date=available_start_date,
                    expected_salary=expected_salary,
                    status=status,
                    cover_letter=cover_letter,
                    notes=f'Candidato de teste #{i+1}'
                )
                
                # Create 1-3 professional experiences for each candidate
                num_experiences = random.randint(1, 3)
                for exp_idx in range(num_experiences):
                    exp_company = random.choice(companies)
                    exp_position = random.choice(positions)
                    
                    # Calculate dates for experience
                    years_ago_start = random.randint(1, 15)
                    years_ago_end = random.randint(0, years_ago_start - 1) if years_ago_start > 1 else 0
                    
                    exp_start_date = datetime.now().date() - timedelta(days=years_ago_start * 365)
                    exp_end_date = datetime.now().date() - timedelta(days=years_ago_end * 365) if years_ago_end > 0 else None
                    
                    motivos_saida = [
                        'Busca por novos desafios',
                        'Melhor oportunidade',
                        'Fim do contrato',
                        'Mudança de cidade',
                        'Crescimento profissional'
                    ]
                    
                    ProfessionalExperience.objects.create(
                        candidate=candidate,
                        empresa=exp_company,
                        cargo=exp_position,
                        descricao_atividades=f'Atuei como {exp_position} realizando {skills.split(",")[0].lower()}.',
                        data_admissao=exp_start_date,
                        data_desligamento=exp_end_date,
                        motivo_saida=random.choice(motivos_saida) if exp_end_date else ''
                    )
                
                # Update applied_date to a random date within the last 12 months
                # Using update() to bypass auto_now_add
                days_ago_applied = random.randint(1, 365)
                random_applied_date = datetime.now() - timedelta(days=days_ago_applied, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                Candidate.objects.filter(pk=candidate.pk).update(applied_date=random_applied_date)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created candidate {created_count}: {full_name} - {position_applied} ({status})')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating candidate {full_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully created {created_count} test candidates!')
        )
