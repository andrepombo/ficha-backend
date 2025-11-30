# Multi-Step Form - Quick Reference

## Form Flow (Correct Order)

```
┌──────────────────────────────────────┐
│ STEP 0: Position Selection          │
│ • Shows ONLY "Cargo Pretendido"     │
│ • User selects position              │
│ • Fetches questionnaires for job    │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ STEP 1: Basic Information            │
│ • Shows all personal data fields     │
│ • Position already selected          │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ STEPS 2+: Questionnaires (Dynamic)   │
│ • Only if position has them          │
│ • Ordered by step_number             │
└──────────────────────────────────────┘
```

## Step Count Formula

```
Total Steps = 1 (position) + 1 (basic info) + N (questionnaires)
```

### Examples:
- **Pintor with 4 questionnaires**: 1 + 1 + 4 = **6 steps**
- **Auxiliar with 0 questionnaires**: 1 + 1 + 0 = **2 steps**
- **Encarregado with 2 questionnaires**: 1 + 1 + 2 = **4 steps**

## API Endpoint

```
GET /api/questionnaires/steps-for-position/?position_key={position}
```

**Response:**
```json
{
  "position_key": "Pintor",
  "total_steps": 4,  // Number of questionnaires only
  "steps": [...]     // Array of questionnaire templates
}
```

## Frontend State

```typescript
{
  currentStep: 0,           // 0 = position, 1 = basic, 2+ = questionnaires
  totalSteps: 6,            // 1 + 1 + 4
  selectedPosition: "Pintor",
  questionnaireSteps: [...],
  formData: {
    position: "Pintor",     // From step 0
    basicInfo: {...},       // From step 1
    questionnaireAnswers: {...} // From steps 2+
  }
}
```

## Step Rendering Logic

```typescript
if (currentStep === 0) {
  // Position selection ONLY
  return <PositionSelectionForm />;
}
else if (currentStep === 1) {
  // Basic information
  return <BasicInfoForm />;
}
else {
  // Questionnaires (index = currentStep - 2)
  const questionnaire = questionnaireSteps[currentStep - 2];
  return <QuestionnaireForm questionnaire={questionnaire} />;
}
```

## Database Fields

**QuestionnaireTemplate:**
- `step_number` - Order of questionnaire (1, 2, 3...)
- `description` - Optional description for candidates
- `position_key` - Which job position this is for
- `is_active` - Must be true to show

## Migration

```bash
python manage.py migrate candidate
```

**File:** `0033_add_step_number_to_questionnaire.py`

## Key Points

✅ **Step 0 is ONLY position selection**  
✅ **Step 1 is ALWAYS basic info**  
✅ **Steps 2+ are dynamic questionnaires**  
✅ **Total steps = 1 + 1 + questionnaire count**  
✅ **Position cannot change after step 0 (must go back)**  

## Documentation Files

1. `FORM_FLOW_SPECIFICATION.md` - Detailed flow with code examples
2. `MULTI_STEP_FORM_GUIDE.md` - Complete backend guide
3. `FRONTEND_MULTI_STEP_IMPLEMENTATION.md` - Frontend implementation
4. `MULTI_STEP_SUMMARY.md` - Implementation summary
5. `QUICK_REFERENCE.md` - This file
