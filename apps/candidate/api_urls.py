from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CandidateViewSet, InterviewViewSet, UserViewSet, ActivityLogViewSet
from .api_views.questionnaire_views import (
    QuestionnaireTemplateViewSet,
    QuestionViewSet,
    QuestionOptionViewSet,
    CandidateQuestionnaireResponseViewSet,
    form_initialization,
)
from .api_views.position_views import PositionViewSet

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet, basename='candidate')
router.register(r'interviews', InterviewViewSet, basename='interview')
router.register(r'users', UserViewSet, basename='user')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')
router.register(r'questionnaires', QuestionnaireTemplateViewSet, basename='questionnaire')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'question-options', QuestionOptionViewSet, basename='question-option')
router.register(r'questionnaire-responses', CandidateQuestionnaireResponseViewSet, basename='questionnaire-response')
router.register(r'positions', PositionViewSet, basename='position')

urlpatterns = [
    path('', include(router.urls)),
    path('form/init/', form_initialization, name='form-init'),
]
