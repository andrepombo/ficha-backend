"""
Models package for the candidate app.

This package organizes models into separate modules for better maintainability:
- candidate.py: Candidate and ProfessionalExperience models
- interview.py: Interview model
- scoring.py: ScoringWeight model
- activity_log.py: ActivityLog model
- work_card.py: WorkCard model for Carteira de Trabalho documents
- questionnaire.py: Questionnaire templates and responses
"""

from .candidate import Candidate, ProfessionalExperience
from .interview import Interview
from .scoring import ScoringWeight
from .activity_log import ActivityLog
from .work_card import WorkCard
from .questionnaire import (
    QuestionnaireTemplate,
    Question,
    QuestionOption,
    CandidateQuestionnaireResponse,
    CandidateSelectedOption,
)

__all__ = [
    'Candidate',
    'ProfessionalExperience',
    'Interview',
    'ScoringWeight',
    'ActivityLog',
    'WorkCard',
    'QuestionnaireTemplate',
    'Question',
    'QuestionOption',
    'CandidateQuestionnaireResponse',
    'CandidateSelectedOption',
]
