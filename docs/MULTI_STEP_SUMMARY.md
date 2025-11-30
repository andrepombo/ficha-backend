# Multi-Step Form Implementation Summary

## Overview

The candidate application form has been enhanced to support dynamic multi-step flows based on job position selection.

## What Changed

### Backend Changes

#### 1. Database Model (`QuestionnaireTemplate`)
**New fields:**
- `step_number` (PositiveIntegerField): Order of questionnaire in multi-step form
- `description` (TextField): Optional description shown to candidates

**Updated:**
- Model ordering: Now orders by `position_key`, `step_number`, `-created_at`
- New database index on `(position_key, step_number)` for performance

#### 2. API Endpoints
**New endpoint:**
- `GET /api/questionnaires/steps-for-position/?position_key={position}`
  - Returns all active questionnaires for a position, ordered by step
  - Response includes `total_steps` count and array of `steps`

**Existing endpoints (unchanged):**
- `GET /api/questionnaires/active/?position_key={position}` (legacy, still works)
- `POST /api/questionnaire-responses/submit/` (submission endpoint)

#### 3. Serializers
**Updated:**
- `QuestionnaireTemplateSerializer`: Added `step_number` and `description` fields
- `QuestionnaireTemplatePublicSerializer`: Added `step_number` and `description` fields

#### 4. Migration
**File:** `0033_add_step_number_to_questionnaire.py`
- Adds `step_number` field (default: 1)
- Adds `description` field (blank=True)
- Creates index on `(position_key, step_number)`
- Updates model Meta ordering

### How It Works

#### Flow Diagram
```
Step 0: Position Selection ONLY
   ↓
   User selects "Pintor"
   ↓
   API call: /api/questionnaires/steps-for-position/?position_key=Pintor
   ↓
   Response: 4 questionnaire steps
   ↓
Step 1: Basic Info (Dados Pessoais)
Step 2: Conhecimentos Técnicos (step_number=1)
Step 3: Experiência Prática (step_number=2)
Step 4: Segurança (step_number=3)
Step 5: Disponibilidade (step_number=4)
   ↓
   Submit all data
```

#### Example Scenarios

**Scenario A: Pintor (4 questionnaires)**
- Total steps: 6 (1 position + 1 basic + 4 questionnaires)
- User sees: Cargo Pretendido → Dados Pessoais → Q1 → Q2 → Q3 → Q4 → Submit

**Scenario B: Auxiliar (0 questionnaires)**
- Total steps: 2 (1 position + 1 basic)
- User sees: Cargo Pretendido → Dados Pessoais → Submit

**Scenario C: Encarregado (2 questionnaires)**
- Total steps: 4 (1 position + 1 basic + 2 questionnaires)
- User sees: Cargo Pretendido → Dados Pessoais → Q1 → Q2 → Submit

## Files Modified

### Backend
1. `/apps/candidate/models/questionnaire.py` - Added fields to model
2. `/apps/candidate/serializers/questionnaire_serializers.py` - Updated serializers
3. `/apps/candidate/serializers.py` - Updated serializers (duplicate)
4. `/apps/candidate/api_views/questionnaire_views.py` - Added new endpoint
5. `/apps/candidate/migrations/0033_add_step_number_to_questionnaire.py` - New migration

### Documentation
1. `/docs/MULTI_STEP_FORM_GUIDE.md` - Complete backend guide
2. `/docs/FRONTEND_MULTI_STEP_IMPLEMENTATION.md` - Frontend implementation guide
3. `/docs/MULTI_STEP_SUMMARY.md` - This summary

## Next Steps

### 1. Run Migration
```bash
cd /home/lock221/pinte_fichas/ficha-backend
source venv/bin/activate
python manage.py migrate candidate
```

### 2. Configure Questionnaires in Admin
For each position that needs multiple steps:
1. Go to Django Admin → Questionnaire Templates
2. Create templates with different `step_number` values
3. Set `is_active=True` for all templates you want to use

Example:
```python
# In Django shell or admin
from apps.candidate.models import QuestionnaireTemplate

# Create step 1
QuestionnaireTemplate.objects.create(
    position_key="Pintor",
    title="Conhecimentos Técnicos",
    step_number=1,
    description="Avalie seus conhecimentos técnicos em pintura",
    is_active=True
)

# Create step 2
QuestionnaireTemplate.objects.create(
    position_key="Pintor",
    title="Experiência com Ferramentas",
    step_number=2,
    description="Informe sua experiência com ferramentas",
    is_active=True
)
```

### 3. Update Frontend
Implement the multi-step form UI following the guide in:
`/docs/FRONTEND_MULTI_STEP_IMPLEMENTATION.md`

Key frontend changes needed:
- Add state management for current step and total steps
- Fetch questionnaire steps when position is selected
- Render steps dynamically based on API response
- Add navigation controls (Previous/Next buttons)
- Add progress indicator
- Handle submission of all steps together

### 4. Test the Flow
1. **Test with questionnaires:**
   - Select "Pintor" position
   - Verify correct number of steps load
   - Navigate through all steps
   - Submit and verify data saved

2. **Test without questionnaires:**
   - Select "Auxiliar" position
   - Verify only basic info step shows
   - Submit immediately

3. **Test navigation:**
   - Go back to previous steps
   - Verify data persists
   - Change position and verify steps update

## API Usage Examples

### Fetch Steps for Position
```bash
curl http://localhost:8000/api/questionnaires/steps-for-position/?position_key=Pintor
```

**Response:**
```json
{
  "position_key": "Pintor",
  "total_steps": 4,
  "steps": [
    {
      "id": 1,
      "position_key": "Pintor",
      "title": "Conhecimentos Técnicos",
      "step_number": 1,
      "description": "Avalie seus conhecimentos",
      "version": 1,
      "questions": [...]
    }
  ]
}
```

### Submit Questionnaire (unchanged)
```bash
curl -X POST http://localhost:8000/api/questionnaire-responses/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 123,
    "template_id": 1,
    "answers": [
      {"question_id": 1, "selected_option_ids": [1]},
      {"question_id": 2, "selected_option_ids": [3, 4]}
    ]
  }'
```

## Benefits

1. **Flexibility**: Each position can have 0 to N questionnaire steps
2. **Better UX**: Candidates see relevant questions for their position
3. **Scalability**: Easy to add/remove questionnaires per position
4. **Maintainability**: Clear separation of concerns
5. **Performance**: Indexed queries for fast step loading

## Backward Compatibility

- Existing questionnaires get `step_number=1` by default
- Old API endpoint still works: `/api/questionnaires/active/`
- Submission endpoint unchanged
- No breaking changes to existing functionality

## Troubleshooting

### Issue: Migration fails
```bash
# Check current migration status
python manage.py showmigrations candidate

# If needed, fake the migration (if already applied manually)
python manage.py migrate candidate 0033 --fake
```

### Issue: Steps not loading
- Verify questionnaires have `is_active=True`
- Check `position_key` matches exactly (case-sensitive)
- Verify API endpoint is accessible

### Issue: Wrong step order
- Check `step_number` values in database
- Ensure no duplicate step numbers for same position
- Verify ordering in queryset

## Contact

For questions or issues, refer to:
- `/docs/MULTI_STEP_FORM_GUIDE.md` - Detailed backend guide
- `/docs/FRONTEND_MULTI_STEP_IMPLEMENTATION.md` - Frontend implementation
- `/docs/QUESTIONNAIRE_SYSTEM.md` - Original questionnaire system docs
