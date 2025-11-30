from rest_framework import serializers
from ..models import (
    QuestionnaireTemplate,
    Question,
    QuestionOption,
    CandidateQuestionnaireResponse,
    CandidateSelectedOption,
)


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
    
    def create(self, validated_data):
        print(f"DEBUG SERIALIZER: validated_data = {validated_data}")
        print(f"DEBUG SERIALIZER: option_points in validated_data = {validated_data.get('option_points')}")
        instance = super().create(validated_data)
        print(f"DEBUG SERIALIZER: Created instance with option_points = {instance.option_points}")
        return instance


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
