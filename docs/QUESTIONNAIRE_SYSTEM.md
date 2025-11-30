# Questionnaire System Documentation

## Overview

The questionnaire system allows admins to create dynamic, per-position questionnaires with multiple-choice questions. Candidates answer these questions, and the system automatically computes scores using an all-or-nothing scoring mode. The system also provides analytics endpoints for reporting.

## Architecture

### Models

1. **QuestionnaireTemplate** - Container for a questionnaire tied to a job position
   - `position_key` - Links to `Candidate.position_applied`
   - `title` - Descriptive name
   - `version` - Version tracking
   - `is_active` - Only one active template per position

2. **Question** - Individual question within a template
   - `question_text` - The question to ask
   - `question_type` - `multi_select` or `single_select`
   - `points` - Points awarded for correct answer
   - `scoring_mode` - `all_or_nothing` (default) or `partial`
   - `order` - Display sequence

3. **QuestionOption** - Answer options for a question
   - `option_text` - The option text
   - `is_correct` - Whether this is a correct answer
   - `order` - Display sequence

4. **CandidateQuestionnaireResponse** - A candidate's submission
   - `candidate` - FK to Candidate
   - `template` - FK to QuestionnaireTemplate
   - `score` - Computed score
   - `max_score` - Maximum possible score

5. **CandidateSelectedOption** - Tracks which options were selected
   - `response` - FK to CandidateQuestionnaireResponse
   - `question` - FK to Question
   - `option` - FK to QuestionOption

### Scoring Logic

**All-or-Nothing Mode** (default):
- Candidate must select exactly the correct set of options
- If correct: full points for the question
- If incorrect: zero points

**Future: Partial Mode**:
- Award proportional credit based on overlap with correct answers

## API Endpoints

### Base URL
```
/api/
```

### 1. Questionnaire Templates

#### List all templates (Admin only)
```http
GET /api/questionnaires/
```

#### Create template (Admin only)
```http
POST /api/questionnaires/
Content-Type: application/json

{
  "position_key": "Painter",
  "title": "Safety Knowledge Test",
  "version": 1,
  "is_active": true
}
```

#### Get active template for a position (Public)
```http
GET /api/questionnaires/active/?position_key=Painter
```

Response (hides correct answers for public):
```json
{
  "id": 1,
  "position_key": "Painter",
  "title": "Safety Knowledge Test",
  "version": 1,
  "questions": [
    {
      "id": 1,
      "question_text": "Which PPE items are mandatory?",
      "question_type": "multi_select",
      "order": 1,
      "options": [
        {"id": 1, "option_text": "Helmet", "order": 1},
        {"id": 2, "option_text": "Gloves", "order": 2},
        {"id": 3, "option_text": "Sandals", "order": 3}
      ]
    }
  ]
}
```

#### Activate a template (Admin only)
```http
POST /api/questionnaires/{id}/activate/
```

#### Deactivate a template (Admin only)
```http
POST /api/questionnaires/{id}/deactivate/
```

#### Get template statistics (Admin only)
```http
GET /api/questionnaires/{id}/stats/
```

Response:
```json
{
  "total_responses": 45,
  "average_score": 7.5,
  "average_percentage": 75.0
}
```

### 2. Questions

#### List questions (Admin only)
```http
GET /api/questions/?template_id=1
```

#### Create question (Admin only)
```http
POST /api/questions/
Content-Type: application/json

{
  "template_id": 1,
  "question_text": "Which PPE items are mandatory?",
  "question_type": "multi_select",
  "order": 1,
  "points": 5.0,
  "scoring_mode": "all_or_nothing"
}
```

#### Update question (Admin only)
```http
PUT /api/questions/{id}/
PATCH /api/questions/{id}/
```

#### Delete question (Admin only)
```http
DELETE /api/questions/{id}/
```

### 3. Question Options

#### List options (Admin only)
```http
GET /api/question-options/?question_id=1
```

#### Create option (Admin only)
```http
POST /api/question-options/
Content-Type: application/json

{
  "question_id": 1,
  "option_text": "Helmet",
  "is_correct": true,
  "order": 1
}
```

#### Update option (Admin only)
```http
PUT /api/question-options/{id}/
PATCH /api/question-options/{id}/
```

#### Delete option (Admin only)
```http
DELETE /api/question-options/{id}/
```

### 4. Candidate Responses

#### Submit questionnaire (Public/Authenticated)
```http
POST /api/questionnaire-responses/submit/
Content-Type: application/json

{
  "candidate_id": 123,
  "template_id": 1,
  "answers": [
    {
      "question_id": 1,
      "selected_option_ids": [1, 2]
    },
    {
      "question_id": 2,
      "selected_option_ids": [5]
    }
  ]
}
```

Response:
```json
{
  "id": 456,
  "candidate": 123,
  "candidate_name": "João Silva",
  "template": 1,
  "template_title": "Safety Knowledge Test",
  "position_key": "Painter",
  "score": 7.50,
  "max_score": 10.00,
  "percentage": 75.0,
  "selected_options": [
    {
      "id": 789,
      "question": 1,
      "option": 1,
      "option_text": "Helmet",
      "is_correct": true,
      "created_at": "2025-01-15T10:30:00Z"
    },
    ...
  ],
  "submitted_at": "2025-01-15T10:30:00Z"
}
```

#### List responses (Admin only)
```http
GET /api/questionnaire-responses/
GET /api/questionnaire-responses/?candidate_id=123
GET /api/questionnaire-responses/?position_key=Painter
```

#### Get single response (Admin only)
```http
GET /api/questionnaire-responses/{id}/
```

### 5. Analytics

#### Analytics by position (Admin only)
```http
GET /api/questionnaire-responses/analytics/by-position/
GET /api/questionnaire-responses/analytics/by-position/?position_key=Painter
```

Response:
```json
[
  {
    "position_key": "Painter",
    "template__title": "Safety Knowledge Test",
    "total_responses": 45,
    "avg_score": 7.5,
    "avg_max_score": 10.0,
    "avg_percentage": 75.0
  }
]
```

#### Option distribution (Admin only)
```http
GET /api/questionnaire-responses/analytics/option-distribution/?question_id=1
```

Response:
```json
[
  {
    "option__id": 1,
    "option__option_text": "Helmet",
    "option__is_correct": true,
    "selection_count": 42
  },
  {
    "option__id": 2,
    "option__option_text": "Gloves",
    "option__is_correct": true,
    "selection_count": 40
  },
  {
    "option__id": 3,
    "option__option_text": "Sandals",
    "option__is_correct": false,
    "selection_count": 5
  }
]
```

## Frontend Integration Guide

### Admin Builder Flow

1. **Create Template**
   ```javascript
   POST /api/questionnaires/
   {
     position_key: "Painter",
     title: "Safety Knowledge Test",
     version: 1,
     is_active: false  // Don't activate until complete
   }
   ```

2. **Add Questions**
   ```javascript
   POST /api/questions/
   {
     template_id: templateId,
     question_text: "Which PPE items are mandatory?",
     question_type: "multi_select",
     order: 1,
     points: 5.0,
     scoring_mode: "all_or_nothing"
   }
   ```

3. **Add Options**
   ```javascript
   POST /api/question-options/
   {
     question_id: questionId,
     option_text: "Helmet",
     is_correct: true,
     order: 1
   }
   ```

4. **Activate Template**
   ```javascript
   POST /api/questionnaires/{templateId}/activate/
   ```

### Candidate Form Flow

1. **Fetch Active Template**
   ```javascript
   const response = await fetch(
     `/api/questionnaires/active/?position_key=${position}`
   );
   const template = await response.json();
   ```

2. **Render Questions**
   ```jsx
   {template.questions.map(question => (
     <div key={question.id}>
       <h3>{question.question_text}</h3>
       {question.options.map(option => (
         <label key={option.id}>
           <input
             type={question.question_type === 'multi_select' ? 'checkbox' : 'radio'}
             name={`question_${question.id}`}
             value={option.id}
           />
           {option.option_text}
         </label>
       ))}
     </div>
   ))}
   ```

3. **Submit Answers**
   ```javascript
   const answers = questions.map(question => ({
     question_id: question.id,
     selected_option_ids: getSelectedOptions(question.id)
   }));

   const response = await fetch('/api/questionnaire-responses/submit/', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       candidate_id: candidateId,
       template_id: template.id,
       answers
     })
   });

   const result = await response.json();
   console.log(`Score: ${result.score}/${result.max_score} (${result.percentage}%)`);
   ```

### Analytics Dashboard

```javascript
// Get stats by position
const stats = await fetch(
  '/api/questionnaire-responses/analytics/by-position/?position_key=Painter'
).then(r => r.json());

// Get option distribution for a question
const distribution = await fetch(
  '/api/questionnaire-responses/analytics/option-distribution/?question_id=1'
).then(r => r.json());
```

## Django Admin Interface

All models are registered in the Django admin with:
- Inline editing for questions and options
- Read-only views for responses (created via API only)
- Bulk actions for activating/deactivating templates
- Visual indicators for correct/incorrect answers

Access at: `/admin/candidate/`

## Permissions

- **Admin users**: Full CRUD access to templates, questions, options
- **Public/Authenticated**: Can fetch active templates (without correct answers) and submit responses
- **Responses**: Read-only in admin; created only via API

## Validation

The system validates:
- All selected option IDs belong to the specified question
- Question IDs belong to the specified template
- Template exists and is active (optional)
- Answer structure is correct

## Future Enhancements

1. **Partial Scoring Mode**: Award proportional credit
2. **Question Types**: Single-select, text input, rating scales
3. **Conditional Logic**: Show questions based on previous answers
4. **Time Limits**: Track time spent on questionnaire
5. **Randomization**: Randomize question/option order
6. **Versioning**: Track changes to templates over time
7. **Export**: Export responses to CSV/Excel

## Example: Complete Workflow

```python
# 1. Admin creates template
template = QuestionnaireTemplate.objects.create(
    position_key="Painter",
    title="Safety Knowledge Test",
    version=1,
    is_active=False
)

# 2. Admin adds question
question = Question.objects.create(
    template=template,
    question_text="Which PPE items are mandatory?",
    question_type="multi_select",
    order=1,
    points=5.0,
    scoring_mode="all_or_nothing"
)

# 3. Admin adds options
QuestionOption.objects.create(
    question=question,
    option_text="Helmet",
    is_correct=True,
    order=1
)
QuestionOption.objects.create(
    question=question,
    option_text="Gloves",
    is_correct=True,
    order=2
)
QuestionOption.objects.create(
    question=question,
    option_text="Sandals",
    is_correct=False,
    order=3
)

# 4. Admin activates template
template.is_active = True
template.save()

# 5. Candidate submits (via API)
# POST /api/questionnaire-responses/submit/
# {
#   "candidate_id": 123,
#   "template_id": template.id,
#   "answers": [
#     {"question_id": question.id, "selected_option_ids": [1, 2]}
#   ]
# }

# 6. System computes score automatically
# Correct answer: [1, 2] (Helmet, Gloves)
# Candidate selected: [1, 2]
# Result: 5.0 / 5.0 points (100%)
```

## Troubleshooting

### Template not found
- Ensure `is_active=True` for the template
- Verify `position_key` matches exactly

### Score is zero
- Check that selected options match correct options exactly (all-or-nothing)
- Verify `is_correct` is set properly on options

### Validation errors
- Ensure all option IDs belong to the question
- Verify answer structure matches expected format

## Support

For issues or questions, contact the development team or check the main project documentation.
