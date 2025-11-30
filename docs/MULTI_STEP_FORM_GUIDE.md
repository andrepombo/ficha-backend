# Multi-Step Form Guide

## Overview

The candidate application form now supports a dynamic multi-step flow where:
1. **Step 0 (Always first)**: Job position selection ONLY ("Cargo Pretendido")
2. **Step 1 (Always second)**: Basic personal information (Dados Pessoais)
3. **Steps 2+ (Dynamic)**: Position-specific questionnaires loaded based on the selected job

## How It Works

### Form Flow

**Step 0: Position Selection (Always First)**
- Shows ONLY "Cargo Pretendido" dropdown
- User selects their desired position
- Triggers API call to fetch questionnaires for that position
- Calculates total steps needed

**Step 1: Basic Information (Always Second)**
- Shows all personal data fields (name, CPF, email, etc.)
- Position is already selected and stored
- User fills in their information

**Steps 2+: Position-Specific Questionnaires (Dynamic)**
- Only shown if the selected position has active questionnaires
- Each questionnaire is a separate step
- Ordered by `step_number` field

### Backend Architecture

#### 1. QuestionnaireTemplate Model Updates

The `QuestionnaireTemplate` model now includes:
- `step_number`: Integer field defining the order of questionnaires (1, 2, 3, etc.)
- `description`: Optional text shown to candidates explaining the questionnaire

```python
# Example: Pintor position with 4 questionnaire steps
QuestionnaireTemplate.objects.create(
    position_key="Pintor",
    title="Conhecimentos Técnicos",
    step_number=1,
    description="Avalie seus conhecimentos técnicos em pintura",
    is_active=True
)

QuestionnaireTemplate.objects.create(
    position_key="Pintor",
    title="Experiência com Ferramentas",
    step_number=2,
    description="Informe sua experiência com ferramentas de pintura",
    is_active=True
)
```

#### 2. New API Endpoint

**GET** `/api/questionnaires/steps-for-position/?position_key={position}`

Returns all active questionnaire steps for a position, ordered by `step_number`.

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
      "description": "Avalie seus conhecimentos técnicos",
      "version": 1,
      "questions": [...]
    },
    {
      "id": 2,
      "position_key": "Pintor",
      "title": "Experiência com Ferramentas",
      "step_number": 2,
      "description": "Informe sua experiência com ferramentas",
      "version": 1,
      "questions": [...]
    }
  ]
}
```

### Frontend Implementation Flow

#### Step 0: Position Selection (Always Shown)
- Display ONLY **Cargo Pretendido** (position selection) dropdown
- When position is selected, fetch questionnaire steps
- Show "Próximo" button to proceed to step 1

#### Step 1: Basic Information (Always Shown)
- Display all personal information fields
- Position is already selected and stored
- Show navigation buttons

#### Steps 2+: Dynamic Questionnaire Steps

```typescript
// 1. User selects position
const handlePositionChange = async (positionKey: string) => {
  const response = await fetch(
    `/api/questionnaires/steps-for-position/?position_key=${positionKey}`
  );
  const data = await response.json();
  
  // data.total_steps tells you how many questionnaire steps
  // data.steps contains all questionnaire templates
  // Total = 1 (position) + 1 (basic info) + N (questionnaires)
  setTotalSteps(1 + 1 + data.total_steps);
  setQuestionnaireSteps(data.steps);
};

// 2. Render steps dynamically
const renderStep = (currentStep: number) => {
  if (currentStep === 0) {
    // Step 0: Position selection only
    return <PositionSelectionForm onPositionChange={handlePositionChange} />;
  } else if (currentStep === 1) {
    // Step 1: Basic information
    return <BasicInfoForm positionApplied={selectedPosition} />;
  } else {
    // Steps 2+: Questionnaires
    const questionnaireIndex = currentStep - 2; // -2 for position and basic info
    const questionnaire = questionnaireSteps[questionnaireIndex];
    return <QuestionnaireForm questionnaire={questionnaire} />;
  }
};
```

### Example Scenarios

#### Scenario 1: Pintor (4 questionnaire steps)
- **Step 0**: Position selection → User selects "Pintor"
- **Step 1**: Basic information (Dados Pessoais)
- **Step 2**: Conhecimentos Técnicos questionnaire
- **Step 3**: Experiência com Ferramentas questionnaire
- **Step 4**: Segurança no Trabalho questionnaire
- **Step 5**: Disponibilidade questionnaire
- **Total**: 6 steps (1 position + 1 basic + 4 questionnaires)

#### Scenario 2: Auxiliar de Pintor (no questionnaires)
- **Step 0**: Position selection → User selects "Auxiliar de Pintor"
- **Step 1**: Basic information (Dados Pessoais)
- **No additional steps** (API returns `total_steps: 0`)
- Form submits after basic info
- **Total**: 2 steps (1 position + 1 basic)

#### Scenario 3: Encarregado (2 questionnaire steps)
- **Step 0**: Position selection → User selects "Encarregado"
- **Step 1**: Basic information (Dados Pessoais)
- **Step 2**: Liderança questionnaire
- **Step 3**: Gestão de Equipe questionnaire
- **Total**: 4 steps (1 position + 1 basic + 2 questionnaires)

## Admin Configuration

### Creating Multi-Step Questionnaires

1. Go to Django Admin → Questionnaire Templates
2. Create templates for a position with different `step_number` values:

```python
# Step 1
QuestionnaireTemplate(
    position_key="Pintor",
    title="Conhecimentos Técnicos",
    step_number=1,
    is_active=True
)

# Step 2
QuestionnaireTemplate(
    position_key="Pintor",
    title="Experiência Prática",
    step_number=2,
    is_active=True
)
```

3. Ensure `is_active=True` for all templates you want to show
4. The system automatically orders by `step_number`

### Best Practices

1. **Step numbering**: Start from 1 (step 0 is reserved for basic info)
2. **Consistent numbering**: Use sequential numbers (1, 2, 3...) for clarity
3. **Position consistency**: All templates for a position should have unique step numbers
4. **Descriptions**: Add helpful descriptions to guide candidates
5. **Question count**: Keep each step focused (5-10 questions per step recommended)

## Migration

The migration `0033_add_step_number_to_questionnaire.py` adds:
- `step_number` field (default: 1)
- `description` field (optional)
- Database index on `(position_key, step_number)` for performance
- Updated model ordering

To apply:
```bash
python manage.py migrate candidate
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/questionnaires/steps-for-position/` | GET | Get all steps for a position |
| `/api/questionnaires/active/` | GET | Get single active questionnaire (legacy) |
| `/api/questionnaire-responses/submit/` | POST | Submit questionnaire answers |
| `/api/positions/` | GET | Get available positions |

## Testing

### Test Case 1: Position with Multiple Steps
```bash
# Create test data
curl -X POST http://localhost:8000/api/questionnaires/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "position_key": "Pintor",
    "title": "Step 1",
    "step_number": 1,
    "is_active": true
  }'

# Fetch steps
curl http://localhost:8000/api/questionnaires/steps-for-position/?position_key=Pintor
```

### Test Case 2: Position with No Steps
```bash
# Fetch steps for position without questionnaires
curl http://localhost:8000/api/questionnaires/steps-for-position/?position_key=Auxiliar
# Expected: {"position_key": "Auxiliar", "total_steps": 0, "steps": []}
```

## Troubleshooting

### Issue: No steps returned for position
- Check that questionnaires have `is_active=True`
- Verify `position_key` matches exactly (case-sensitive)
- Check database: `QuestionnaireTemplate.objects.filter(position_key="Pintor", is_active=True)`

### Issue: Steps in wrong order
- Verify `step_number` values are set correctly
- Check for duplicate step numbers for the same position
- The system orders by `step_number` ascending

### Issue: Old questionnaires still showing
- Deactivate old templates: `template.is_active = False; template.save()`
- Only one template per position+step should be active

## Future Enhancements

Potential improvements:
1. **Conditional steps**: Show/hide steps based on previous answers
2. **Progress saving**: Allow candidates to save and resume later
3. **Step validation**: Validate each step before proceeding
4. **Dynamic step titles**: Customize step titles per position
5. **Step dependencies**: Define prerequisite steps
