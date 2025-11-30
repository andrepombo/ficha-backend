# Multiple Active Questionnaires Feature

## Overview
Updated the questionnaire system to support **multiple active questionnaires per position** with customizable ordering. Previously, only one questionnaire could be active per position at a time.

## Changes Made

### Backend Changes

#### 1. Model Updates (`apps/candidate/models/questionnaire.py`)
- **Removed single-active constraint**: The `save()` method no longer deactivates other templates when activating one
- **Updated help text**: Changed `is_active` field help text to reflect that multiple templates can be active
- **Existing `step_number` field**: Already present (added in migration 0033), controls the order questionnaires appear after "Dados Pessoais"

#### 2. API Endpoints (`apps/candidate/api_views/questionnaire_views.py`)
- **Updated `activate` endpoint**: Removed comment about deactivating others
- **Added `update_step` endpoint**: New POST endpoint at `/questionnaires/{id}/update_step/` to change step_number
  - Accepts: `{"step_number": <integer>}`
  - Validates: step_number must be >= 1
- **Existing `steps_for_position` endpoint**: Already available at `/questionnaires/steps-for-position/?position_key=<key>`
  - Returns all active questionnaires for a position, ordered by `step_number`

#### 3. Database Migration
- **Migration 0034**: Updates `is_active` field help text
- **Migration 0033**: Already existed, added `step_number` field and indexes

### Frontend Changes

#### 1. API Service (`src/services/api.ts`)
- **Added `getStepsForPosition(positionKey)`**: Fetches all active questionnaires for a position
- **Added `updateTemplateStep(id, stepNumber)`**: Updates the step_number of a questionnaire

#### 2. QuestionnaireBuilder Component (`src/components/questionnaires/QuestionnaireBuilder.tsx`)
- **Added `step_number` field**: New input field in the template info section
- **Label**: "Ordem (após Dados Pessoais)"
- **Validation**: Minimum value of 1
- **Saves step_number**: Included when creating/updating templates

#### 3. Questionnaires Page (`src/pages/Questionnaires.tsx`)
- **Added step_number display**: Shows in the stats grid for each questionnaire card
- **Inline editing**: Step number can be changed directly from the card via number input
- **Auto-save**: Changes are saved immediately on blur/change
- **Updated description**: "Gerencie múltiplos questionários por posição e defina a ordem de exibição"

## Usage

### Creating Multiple Questionnaires
1. Navigate to **Questionários** page
2. Click **Novo Questionário**
3. Fill in:
   - **Título**: Name of the questionnaire
   - **Posição**: Select the job position
   - **Ordem**: Set the order (1 = first after personal data, 2 = second, etc.)
4. Add questions and options
5. Click **Salvar**
6. Click **Ativar** to make it active

### Reordering Questionnaires
1. On the **Questionários** page, find the questionnaire card
2. In the "Ordem" field (stats section), change the number
3. The order updates automatically

### Activating Multiple Questionnaires
- You can now activate multiple questionnaires for the same position
- Each will appear in the candidate form based on its `step_number`
- Order: Dados Pessoais → Questionnaire (step 1) → Questionnaire (step 2) → etc.

## API Endpoints

### Get All Active Questionnaires for Position
```
GET /api/questionnaires/steps-for-position/?position_key=Pintor
```

Response:
```json
{
  "position_key": "Pintor",
  "total_steps": 3,
  "steps": [
    {
      "id": 1,
      "title": "Teste de Segurança",
      "step_number": 1,
      "is_active": true,
      "questions": [...]
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

### Update Step Number
```
POST /api/questionnaires/{id}/update_step/
Content-Type: application/json

{
  "step_number": 3
}
```

Response:
```json
{
  "status": "updated",
  "step_number": 3
}
```

## Migration Commands

```bash
# Already applied
python manage.py migrate candidate
```

## Notes
- The `step_number` field was already present in the database (migration 0033)
- Only the constraint logic and UI were updated
- Backward compatible: existing single questionnaires continue to work
- The ordering is enforced by `step_number`, not by activation order
- **Both admin panel and candidate form fully support multiple questionnaires**
- See `MULTIPLE_QUESTIONNAIRES_COMPLETE.md` for full implementation details
