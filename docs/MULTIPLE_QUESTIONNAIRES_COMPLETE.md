# Multiple Questionnaires - Complete Implementation

## Overview
The questionnaire system now fully supports **multiple active questionnaires per position** with customizable ordering in both the admin panel and the candidate application form.

## What Changed

### Backend
1. **Removed single-active constraint** from `QuestionnaireTemplate` model
2. **Added `update_step` API endpoint** for reordering questionnaires
3. **Fixed `active` endpoint** to return first questionnaire instead of throwing error
4. **`steps-for-position` endpoint** returns all active questionnaires ordered by `step_number`

### Frontend Admin Panel
1. **QuestionnaireBuilder**: Added "Ordem (após Dados Pessoais)" field
2. **Questionnaires Page**: 
   - Displays step_number in stats grid
   - Inline editable number input for quick reordering
   - Updated description

### Candidate Application Form
1. **Dynamic questionnaire steps**: Creates one step per active questionnaire
2. **Step indicator**: Shows all questionnaire steps with their titles
3. **Navigation**: Properly handles multiple questionnaire steps
4. **Answer tracking**: Stores answers per template: `{ templateId: { questionId: [optionIds] } }`
5. **Validation**: Validates each questionnaire step independently
6. **Review page**: Shows summary for each questionnaire

## How It Works

### For Admins

#### Creating Multiple Questionnaires
1. Go to **Questionários** page (`/painel/questionnaires`)
2. Click **Novo Questionário**
3. Fill in:
   - **Título**: e.g., "Teste de Segurança"
   - **Posição**: Select job position (e.g., "Pintor")
   - **Ordem**: Set order (1, 2, 3, etc.)
4. Add questions and options
5. Click **Salvar**
6. Click **Ativar** to make it active

#### Reordering Questionnaires
- On the Questionnaires page, change the number in the "Ordem" field
- The order updates automatically
- Lower numbers appear first in the candidate form

#### Example Setup
For position "Pintor", you could have:
- **Step 1**: "Teste de Segurança" (ordem: 1)
- **Step 2**: "Conhecimentos Técnicos" (ordem: 2)
- **Step 3**: "Experiência Prática" (ordem: 3)

### For Candidates

#### Application Flow
1. **Step 1**: Dados Pessoais (Personal Data)
2. **Step 2**: First Questionnaire (if any)
3. **Step 3**: Second Questionnaire (if any)
4. **Step N**: Additional Questionnaires...
5. **Last Step**: Revisão (Review)

#### Step Indicator
The step indicator dynamically shows:
```
1. Dados Pessoais → 2. Teste de Segurança → 3. Conhecimentos Técnicos → 4. Revisão
```

#### Navigation
- Each questionnaire has "← Voltar" and "Próximo →" buttons
- Validation ensures all questions are answered before proceeding
- Review page shows summary of all questionnaires

## API Endpoints

### Get All Active Questionnaires for Position
```http
GET /api/questionnaires/steps-for-position/?position_key=Pintor
```

**Response:**
```json
{
  "position_key": "Pintor",
  "total_steps": 3,
  "steps": [
    {
      "id": 1,
      "title": "Teste de Segurança",
      "step_number": 1,
      "description": "",
      "is_active": true,
      "questions": [
        {
          "id": 1,
          "question_text": "Você possui treinamento em segurança?",
          "question_type": "single_select",
          "options": [...]
        }
      ]
    },
    {
      "id": 2,
      "title": "Conhecimentos Técnicos",
      "step_number": 2,
      "is_active": true,
      "questions": [...]
    }
  ]
}
```

### Update Questionnaire Order
```http
POST /api/questionnaires/{id}/update_step/
Content-Type: application/json

{
  "step_number": 2
}
```

## Data Format

### Candidate Answers Submission
The hidden field `questionnaire_answers` now contains:
```json
[
  {
    "template_id": 1,
    "answers": [
      {
        "question_id": 1,
        "selected_option_ids": [1, 3]
      },
      {
        "question_id": 2,
        "selected_option_ids": [5]
      }
    ]
  },
  {
    "template_id": 2,
    "answers": [
      {
        "question_id": 3,
        "selected_option_ids": [7]
      }
    ]
  }
]
```

## Testing

### Test Multiple Questionnaires
1. Create 2-3 questionnaires for the same position
2. Set different `step_number` values (1, 2, 3)
3. Activate all of them
4. Go to the candidate form
5. Select that position
6. Verify all questionnaires appear in correct order

### Test Reordering
1. Change the "Ordem" field on a questionnaire
2. Refresh the candidate form
3. Verify the questionnaires appear in the new order

### Test Validation
1. Try to proceed without answering all questions
2. Verify validation message appears
3. Answer all questions and proceed
4. Verify review page shows all questionnaires

## Migration Status
- ✅ Migration 0033: Added `step_number` field
- ✅ Migration 0034: Updated `is_active` help text

## Files Modified

### Backend
- `apps/candidate/models/questionnaire.py`
- `apps/candidate/api_views/questionnaire_views.py`
- `apps/candidate/migrations/0034_update_questionnaire_is_active_help_text.py`

### Frontend Admin
- `src/services/api.ts`
- `src/components/questionnaires/QuestionnaireBuilder.tsx`
- `src/pages/Questionnaires.tsx`

### Candidate Form
- `apps/candidate/static/candidate/js/questionnaire-integration.js`

## Notes
- All questionnaires for a position must have unique `step_number` values for best UX
- The system handles duplicate step numbers by sorting alphabetically by title
- Deactivating a questionnaire removes it from the candidate form immediately
- The review page shows a summary for each questionnaire answered
