#!/usr/bin/env python
"""
Initialize default scoring weights in the database.
Run this script once to create the initial configuration.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import ScoringWeight

def init_scoring_weights():
    """Create initial scoring weight configuration."""
    
    # Check if any configuration exists
    if ScoringWeight.objects.exists():
        print("Scoring weights already exist in database.")
        active_config = ScoringWeight.get_active_config()
        print(f"Active configuration: {active_config}")
        print(f"Total points: {active_config.get_total_points()}")
        return
    
    # Create default configuration
    print("Creating default scoring weights configuration...")
    config = ScoringWeight.objects.create(
        years_of_experience=27,
        idle_time=5,
        education_level=16,
        courses=0,
        skills=2,
        certifications=0,
        immediate_availability=5,
        own_transportation=5,
        travel_availability=5,
        height_painting=5,
        average_rating=30,
        is_active=True
    )
    
    print(f"✓ Created scoring configuration: {config}")
    print(f"✓ Total points: {config.get_total_points()}")
    print("\nConfiguration breakdown:")
    print(f"  Experiência & Habilidades: {config.years_of_experience + config.idle_time} pts")
    print(f"    - Anos de experiência: {config.years_of_experience} pts")
    print(f"    - Tempo parado: {config.idle_time} pts")
    print(f"  Educação & Qualificações: {config.education_level + config.courses + config.skills + config.certifications} pts")
    print(f"  Disponibilidade & Logística: {config.immediate_availability + config.own_transportation + config.travel_availability + config.height_painting} pts")
    print(f"  Desempenho em Entrevistas: {config.average_rating} pts")

if __name__ == '__main__':
    init_scoring_weights()
