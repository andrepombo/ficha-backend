from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.candidate.models import Candidate, Interview
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Seed database with 40 candidates and sample interviews'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with sample data...')
        
        # Create admin user if doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Clear existing data
        Candidate.objects.all().delete()
        Interview.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared existing candidates and interviews'))
        
        # Sample data
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
        
        # Create 40 candidates with different application dates
        candidates = []
        base_datetime = datetime.now()
        
        for i in range(40):
            # Random application date within last 6 months
            days_ago = random.randint(0, 180)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            applied_date = base_datetime - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Generate random phone and CPF
            phone = f"{random.randint(11, 21)} {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"
            cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
            
            full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            candidate = Candidate.objects.create(
                full_name=full_name,
                email=f"{full_name.lower().replace(' ', '.')}@email.com",
                phone_number=phone,
                cpf=cpf,
                date_of_birth=f"{random.randint(1980, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                gender=random.choice(['masculino', 'feminino']),
                disability=random.choice(['sem_deficiencia', 'fisica', 'auditiva', 'visual']),
                has_own_transportation=random.choice(['sim', 'nao']),
                address=f"Rua {random.choice(['das Flores', 'Principal', 'Central', 'do Comércio'])}, {random.randint(1, 999)}",
                city=random.choice(cities),
                state='SP',
                postal_code=f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                country='Brasil',
                position_applied=random.choice(positions),
                current_company=random.choice(['Pinturas ABC', 'Tintas XYZ', 'Reformas 123', 'Autônomo', 'Não informado']),
                current_position=random.choice(['Pintor', 'Auxiliar', 'Ajudante', 'Não informado']),
                years_of_experience=random.randint(0, 15),
                has_relatives_in_company='nao',
                referred_by=random.choice(['', 'João Silva', 'Maria Santos']),
                how_found_vacancy=random.choice(['facebook', 'instagram', 'linkedin', 'indicacao_colaborador', 'sine']),
                worked_at_pinte_before='nao',
                highest_education=random.choice(['fundamental_incompleto', 'fundamental_completo', 'medio_incompleto', 'medio_completo', 'superior_incompleto']),
                currently_employed=random.choice(['sim', 'nao']),
                availability_start=random.choice(['imediato', '15_dias', '30_dias']),
                travel_availability=random.choice(['sim', 'nao']),
                height_painting=random.choice(['sim', 'nao']),
                skills=random.choice(['Pintura residencial, comercial', 'Pintura automotiva', 'Pintura industrial', 'Textura, grafiato']),
                expected_salary=random.randint(1500, 4000),
                status=random.choice(statuses),
                notes=random.choice(['', 'Candidato com boa experiência', 'Recomendado', 'Aguardando documentação'])
            )
            
            # Update applied_date manually (auto_now_add prevents setting it during create)
            Candidate.objects.filter(id=candidate.id).update(applied_date=applied_date)
            candidate.refresh_from_db()
            
            candidates.append(candidate)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(candidates)} candidates'))
        
        # Create some interviews for shortlisted/interviewed candidates
        admin_user = User.objects.get(username='admin')
        interview_candidates = [c for c in candidates if c.status in ['shortlisted', 'interviewed', 'accepted']]
        
        interview_count = 0
        for candidate in interview_candidates[:15]:  # Create interviews for up to 15 candidates
            # Random interview date within next 30 days or past 30 days
            days_offset = random.randint(-30, 30)
            interview_date = base_datetime + timedelta(days=days_offset)
            
            interview_status = 'scheduled' if days_offset > 0 else random.choice(['completed', 'cancelled', 'no_show'])
            
            Interview.objects.create(
                candidate=candidate,
                interviewer=admin_user if random.choice([True, False]) else None,
                title=f"Entrevista - {candidate.full_name}",
                interview_type=random.choice(['phone', 'video', 'in_person']),
                scheduled_date=interview_date.date().isoformat(),
                scheduled_time=f"{random.randint(8, 17):02d}:00",
                duration_minutes=random.choice([30, 45, 60]),
                location=random.choice(['Escritório Central', 'Online - Google Meet', 'Telefone']),
                description=f"Entrevista para vaga de {candidate.position_applied}",
                status=interview_status,
                feedback=random.choice(['', 'Candidato qualificado', 'Boa apresentação', 'Necessita mais experiência']) if interview_status == 'completed' else '',
                rating=random.randint(3, 5) if interview_status == 'completed' else None,
                candidate_notified=True,
                reminder_sent=False,
                created_by=admin_user
            )
            interview_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {interview_count} interviews'))
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write('')
        self.stdout.write('Summary:')
        self.stdout.write(f'  - Total candidates: {Candidate.objects.count()}')
        self.stdout.write(f'  - Pending: {Candidate.objects.filter(status="pending").count()}')
        self.stdout.write(f'  - Reviewing: {Candidate.objects.filter(status="reviewing").count()}')
        self.stdout.write(f'  - Shortlisted: {Candidate.objects.filter(status="shortlisted").count()}')
        self.stdout.write(f'  - Interviewed: {Candidate.objects.filter(status="interviewed").count()}')
        self.stdout.write(f'  - Accepted: {Candidate.objects.filter(status="accepted").count()}')
        self.stdout.write(f'  - Rejected: {Candidate.objects.filter(status="rejected").count()}')
        self.stdout.write(f'  - Total interviews: {Interview.objects.count()}')
