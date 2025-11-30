from rest_framework import serializers
from .models import (
    Candidate, 
    ProfessionalExperience, 
    Interview, 
    ActivityLog, 
    WorkCard,
    QuestionnaireTemplate,
    Question,
    QuestionOption,
    CandidateQuestionnaireResponse,
    CandidateSelectedOption,
)
from django.contrib.auth.models import User
import boto3
from django.conf import settings
from botocore.config import Config
import os
from functools import lru_cache


class WorkCardSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkCard model.
    """
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkCard
        fields = ['id', 'file', 'file_url', 'file_name', 'file_size', 'file_extension', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def get_file_url(self, obj):
        """Get the full URL for the file."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_size(self, obj):
        """Get the file size in bytes."""
        return obj.get_file_size()
    
    def get_file_extension(self, obj):
        """Get the file extension."""
        return obj.get_file_extension()


class ProfessionalExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for ProfessionalExperience model.
    """
    idle_time_days = serializers.SerializerMethodField()
    idle_time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfessionalExperience
        fields = ['id', 'empresa', 'cargo', 'descricao_atividades', 'data_admissao', 'data_desligamento', 'motivo_saida', 'idle_time_days', 'idle_time_formatted']
    
    def get_idle_time_days(self, obj):
        """Get the number of days since the last job ended."""
        return obj.get_idle_time_days()
    
    def get_idle_time_formatted(self, obj):
        """Get the formatted idle time string."""
        return obj.get_idle_time_formatted()


class CandidateSerializer(serializers.ModelSerializer):
    """
    Serializer for Candidate model with all fields.
    """
    professional_experiences = ProfessionalExperienceSerializer(many=True, read_only=True)
    work_cards = WorkCardSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ['applied_date', 'updated_date', 'whatsapp_opt_in_date', 'password_hash']
    
    def to_representation(self, instance):
        """Override to return absolute URLs for photo field."""
        data = super().to_representation(instance)
        if data.get('photo') and instance.photo:
            try:
                use_s3 = getattr(settings, 'USE_S3_MEDIA', False)
                if use_s3:
                    # Always return a presigned URL for S3 (works even with AWS_S3_CUSTOM_DOMAIN)
                    s3 = _get_s3_client()
                    bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
                    data['photo'] = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket, 'Key': instance.photo.name},
                        ExpiresIn=getattr(settings, 'AWS_QUERYSTRING_EXPIRE', 3600),
                    )
                else:
                    request = self.context.get('request')
                    url = instance.photo.url
                    # Build absolute URL for local filesystem storage
                    if request and not (url.startswith('http://') or url.startswith('https://')):
                        url = request.build_absolute_uri(url)
                    data['photo'] = url
            except Exception:
                request = self.context.get('request')
                if request:
                    data['photo'] = request.build_absolute_uri(data['photo'])
        # Add presigned or absolute URL for resume and force download for non-PDF
        if data.get('resume') and instance.resume:
            try:
                use_s3 = getattr(settings, 'USE_S3_MEDIA', False)
                filename = os.path.basename(instance.resume.name)
                ext = os.path.splitext(filename)[1].lower()
                if use_s3:
                    s3 = _get_s3_client()
                    bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
                    # Force download for non-PDF by setting Content-Disposition
                    disposition = 'inline' if ext == '.pdf' else 'attachment'
                    data['resume'] = s3.generate_presigned_url(
                        'get_object',
                        Params={
                            'Bucket': bucket,
                            'Key': instance.resume.name,
                            'ResponseContentDisposition': f"{disposition}; filename=\"{filename}\"",
                        },
                        ExpiresIn=getattr(settings, 'AWS_QUERYSTRING_EXPIRE', 3600),
                        HttpMethod='GET'
                    )
                else:
                    request = self.context.get('request')
                    url = instance.resume.url
                    if request and not (url.startswith('http://') or url.startswith('https://')):
                        url = request.build_absolute_uri(url)
                    data['resume'] = url
            except Exception:
                request = self.context.get('request')
                if request:
                    data['resume'] = request.build_absolute_uri(data['resume'])
        # Add variant URLs
        try:
            if instance.photo:
                storage = instance.photo.storage
                base, _ext = os.path.splitext(instance.photo.name)
                medium_key = f"{base}_medium.jpg"
                thumb_key = f"{base}_thumb.jpg"

                use_s3 = getattr(settings, 'USE_S3_MEDIA', False)
                request = self.context.get('request')
                s3 = _get_s3_client() if use_s3 else None

                # original
                data['photo_original'] = data.get('photo')

                # medium
                if use_s3 and s3:
                    # Do not assume variant exists on S3; use original to avoid 404 and extra HEADs
                    data['photo_medium'] = data.get('photo')
                else:
                    if storage.exists(medium_key):
                        url = storage.url(medium_key)
                        if request and not (url.startswith('http://') or url.startswith('https://')):
                            url = request.build_absolute_uri(url)
                        data['photo_medium'] = url
                    else:
                        data['photo_medium'] = data.get('photo')

                # thumb
                if use_s3 and s3:
                    data['photo_thumb'] = data.get('photo')
                else:
                    if storage.exists(thumb_key):
                        url = storage.url(thumb_key)
                        if request and not (url.startswith('http://') or url.startswith('https://')):
                            url = request.build_absolute_uri(url)
                        data['photo_thumb'] = url
                    else:
                        data['photo_thumb'] = data.get('photo')
        except Exception:
            pass
        return data


@lru_cache(maxsize=1)
def _get_s3_client():
    region = getattr(settings, 'AWS_S3_REGION_NAME', None)
    endpoint_url = f"https://s3.{region}.amazonaws.com" if region else None
    return boto3.client(
        's3',
        region_name=region,
        endpoint_url=endpoint_url,
        config=Config(
            signature_version='s3v4',
            s3={
                'addressing_style': 'virtual',
                'us_east_1_regional_endpoint': 'regional',
            },
        ),
    )


class CandidateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing candidates (without large text fields).
    """
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    score_grade = serializers.SerializerMethodField()
    score_color = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'cpf',
            'email',
            'phone_number',
            'date_of_birth',
            'gender',
            'disability',
            'has_own_transportation',
            'position_applied',
            'years_of_experience',
            'has_relatives_in_company',
            'referred_by',
            'how_found_vacancy',
            'how_found_vacancy_other',
            'worked_at_pinte_before',
            'highest_education',
            'currently_employed',
            'availability_start',
            'travel_availability',
            'height_painting',
            'status',
            'applied_date',
            'updated_date',
            'score',
            'score_grade',
            'score_color',
            'score_breakdown',
            'score_updated_at',
        ]
    
    def get_first_name(self, obj):
        """Extract first name from full_name."""
        if obj.full_name:
            parts = obj.full_name.split(' ', 1)
            return parts[0] if parts else ''
        return ''
    
    def get_last_name(self, obj):
        """Extract last name from full_name."""
        if obj.full_name:
            parts = obj.full_name.split(' ', 1)
            return parts[1] if len(parts) > 1 else ''
        return ''
    
    def get_score_grade(self, obj):
        """Get the letter grade for the candidate's score."""
        return obj.get_score_grade()
    
    def get_score_color(self, obj):
        """Get the color code for the candidate's score."""
        return obj.get_score_color()


class CandidateStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating only the status field.
    """
    class Meta:
        model = Candidate
        fields = ['status']


class CandidateNotesUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating only the notes field.
    """
    class Meta:
        model = Candidate
        fields = ['notes']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (for interviewer information).
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name', 'is_superuser']
    
    def get_full_name(self, obj):
        """Get user's full name or username as fallback."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return obj.username


class InterviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Interview model with all fields.
    """
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    candidate_phone = serializers.CharField(source='candidate.phone_number', read_only=True)
    interviewer_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    
    class Meta:
        model = Interview
        fields = [
            'id',
            'candidate',
            'candidate_name',
            'candidate_email',
            'candidate_phone',
            'interviewer',
            'interviewer_name',
            'title',
            'interview_type',
            'scheduled_date',
            'scheduled_time',
            'duration_minutes',
            'location',
            'description',
            'status',
            'status_color',
            'feedback',
            'rating',
            'candidate_notified',
            'reminder_sent',
            'whatsapp_sent',
            'whatsapp_message_sid',
            'whatsapp_sent_at',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_name',
        ]
        read_only_fields = ['created_at', 'updated_at', 'whatsapp_sent', 'whatsapp_message_sid', 'whatsapp_sent_at']
    
    def get_interviewer_name(self, obj):
        """Get interviewer's full name."""
        if obj.interviewer:
            return f"{obj.interviewer.first_name} {obj.interviewer.last_name}".strip() or obj.interviewer.username
        return None
    
    def get_created_by_name(self, obj):
        """Get creator's full name."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None


class InterviewListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing interviews.
    """
    candidate_name = serializers.SerializerMethodField()
    candidate_position = serializers.SerializerMethodField()
    interviewer_name = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    
    class Meta:
        model = Interview
        fields = [
            'id',
            'candidate',
            'candidate_name',
            'candidate_position',
            'interviewer',
            'interviewer_name',
            'title',
            'interview_type',
            'scheduled_date',
            'scheduled_time',
            'duration_minutes',
            'status',
            'status_color',
            'location',
            'rating',
            'feedback',
        ]
    
    def get_candidate_name(self, obj):
        """Get candidate's full name."""
        if obj.candidate:
            return obj.candidate.full_name
        return None
    
    def get_candidate_position(self, obj):
        """Get candidate's applied position."""
        if obj.candidate:
            return obj.candidate.position_applied
        return None
    
    def get_interviewer_name(self, obj):
        """Get interviewer's full name."""
        if obj.interviewer:
            return f"{obj.interviewer.first_name} {obj.interviewer.last_name}".strip() or obj.interviewer.username
        return None
    
    def get_status_color(self, obj):
        """Get color for interview status."""
        status_colors = {
            'scheduled': '#3b82f6',  # Blue
            'completed': '#10b981',  # Green
            'cancelled': '#ef4444',  # Red
            'rescheduled': '#f59e0b',  # Amber
        }
        return status_colors.get(obj.status, '#6b7280')  # Default gray


class ActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for ActivityLog model.
    """
    candidate_name = serializers.SerializerMethodField()
    interview_title = serializers.SerializerMethodField()
    interviewer_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'candidate',
            'candidate_name',
            'interview',
            'interview_title',
            'interviewer_name',
            'user',
            'user_name',
            'action_type',
            'action_type_display',
            'description',
            'old_value',
            'new_value',
            'timestamp',
            'ip_address',
            'user_agent',
        ]
        read_only_fields = ['timestamp']
    
    def get_candidate_name(self, obj):
        """Get candidate's full name (or stored name if candidate was deleted)."""
        if obj.candidate:
            return obj.candidate.full_name
        elif obj.candidate_name:
            return f"{obj.candidate_name} (deletado)"
        return None
    
    def get_interview_title(self, obj):
        """Get interview title."""
        if obj.interview:
            return obj.interview.title
        return None
    
    def get_interviewer_name(self, obj):
        """Get interviewer's full name from the interview."""
        if obj.interview and obj.interview.interviewer:
            interviewer = obj.interview.interviewer
            return f"{interviewer.first_name} {interviewer.last_name}".strip() or interviewer.username
        return None
    
    def get_user_name(self, obj):
        """Get user's full name."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return None


class ActivityLogListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing activity logs.
    """
    candidate_name = serializers.SerializerMethodField()
    interview_title = serializers.SerializerMethodField()
    interviewer_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'candidate_name',
            'interview_title',
            'interviewer_name',
            'user_name',
            'action_type',
            'action_type_display',
            'description',
            'timestamp',
        ]
    
    def get_candidate_name(self, obj):
        """Get candidate's full name (or stored name if candidate was deleted)."""
        if obj.candidate:
            return obj.candidate.full_name
        elif obj.candidate_name:
            return f"{obj.candidate_name} (deletado)"
        return None
    
    def get_interview_title(self, obj):
        """Get interview title."""
        if obj.interview:
            return obj.interview.title
        return None
    
    def get_interviewer_name(self, obj):
        """Get interviewer's full name from the interview."""
        if obj.interview and obj.interview.interviewer:
            interviewer = obj.interview.interviewer
            return f"{interviewer.first_name} {interviewer.last_name}".strip() or interviewer.username
        return None
    
    def get_user_name(self, obj):
        """Get user's full name."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return None


# ============================================================================
# Questionnaire Serializers
# ============================================================================

class QuestionOptionSerializer(serializers.ModelSerializer):
    """Serializer for question options."""
    
    class Meta:
        model = QuestionOption
        fields = [
            'id',
            'option_text',
            'is_correct',
            'option_points',
            'order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuestionOptionPublicSerializer(serializers.ModelSerializer):
    """Public serializer for question options (hides is_correct)."""
    
    class Meta:
        model = QuestionOption
        fields = [
            'id',
            'option_text',
            'order',
        ]
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions with nested options."""
    options = QuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id',
            'question_text',
            'question_type',
            'order',
            'points',
            'scoring_mode',
            'options',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuestionPublicSerializer(serializers.ModelSerializer):
    """Public serializer for questions (hides correct answers)."""
    options = QuestionOptionPublicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id',
            'question_text',
            'question_type',
            'order',
            'options',
        ]
        read_only_fields = ['id']


class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    """Serializer for questionnaire templates with nested questions."""
    questions = QuestionSerializer(many=True, read_only=True)
    total_points = serializers.SerializerMethodField()
    
    class Meta:
        model = QuestionnaireTemplate
        fields = [
            'id',
            'position_key',
            'title',
            'step_number',
            'description',
            'version',
            'is_active',
            'questions',
            'total_points',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_points']
    
    def get_total_points(self, obj):
        """Calculate total points for the questionnaire."""
        return obj.get_total_points()


class QuestionnaireTemplatePublicSerializer(serializers.ModelSerializer):
    """Public serializer for questionnaire templates (hides correct answers)."""
    questions = QuestionPublicSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuestionnaireTemplate
        fields = [
            'id',
            'position_key',
            'title',
            'step_number',
            'description',
            'version',
            'questions',
        ]
        read_only_fields = ['id']


class CandidateSelectedOptionSerializer(serializers.ModelSerializer):
    """Serializer for candidate selected options."""
    option_text = serializers.CharField(source='option.option_text', read_only=True)
    is_correct = serializers.BooleanField(source='option.is_correct', read_only=True)
    
    class Meta:
        model = CandidateSelectedOption
        fields = [
            'id',
            'question',
            'option',
            'option_text',
            'is_correct',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'option_text', 'is_correct']


class CandidateQuestionnaireResponseSerializer(serializers.ModelSerializer):
    """Serializer for candidate questionnaire responses."""
    selected_options = CandidateSelectedOptionSerializer(many=True, read_only=True)
    percentage = serializers.SerializerMethodField()
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    template_title = serializers.CharField(source='template.title', read_only=True)
    
    class Meta:
        model = CandidateQuestionnaireResponse
        fields = [
            'id',
            'candidate',
            'candidate_name',
            'template',
            'template_title',
            'position_key',
            'score',
            'max_score',
            'percentage',
            'selected_options',
            'submitted_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'score',
            'max_score',
            'percentage',
            'submitted_at',
            'created_at',
            'updated_at',
            'candidate_name',
            'template_title',
        ]
    
    def get_percentage(self, obj):
        """Calculate percentage score."""
        return obj.get_percentage()


class SubmitQuestionnaireSerializer(serializers.Serializer):
    """Serializer for submitting questionnaire answers."""
    template_id = serializers.IntegerField(required=True)
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.JSONField()
        ),
        required=True,
        help_text='List of answers: [{"question_id": 1, "selected_option_ids": [1, 3]}, ...]'
    )
    
    def validate_answers(self, value):
        """Validate that answers have the correct structure."""
        for answer in value:
            if 'question_id' not in answer:
                raise serializers.ValidationError("Each answer must have 'question_id'")
            if 'selected_option_ids' not in answer:
                raise serializers.ValidationError("Each answer must have 'selected_option_ids'")
            if not isinstance(answer['selected_option_ids'], list):
                raise serializers.ValidationError("'selected_option_ids' must be a list")
        return value
