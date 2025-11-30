# Frontend Multi-Step Form Implementation Guide

## Quick Start

This guide shows how to implement the dynamic multi-step form on the frontend.

## Step-by-Step Implementation

### 1. State Management

```typescript
interface FormState {
  currentStep: number;
  totalSteps: number;
  selectedPosition: string | null;
  questionnaireSteps: QuestionnaireTemplate[];
  formData: {
    basicInfo: any;
    questionnaireAnswers: Record<number, any[]>; // templateId -> answers
  };
}

const [formState, setFormState] = useState<FormState>({
  currentStep: 0,
  totalSteps: 1, // Initially just basic info
  selectedPosition: null,
  questionnaireSteps: [],
  formData: {
    basicInfo: {},
    questionnaireAnswers: {}
  }
});
```

### 2. Position Selection Handler

```typescript
const handlePositionChange = async (positionKey: string) => {
  try {
    // Fetch questionnaire steps for this position
    const response = await fetch(
      `/api/questionnaires/steps-for-position/?position_key=${encodeURIComponent(positionKey)}`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch questionnaire steps');
    }
    
    const data = await response.json();
    
    setFormState(prev => ({
      ...prev,
      selectedPosition: positionKey,
      questionnaireSteps: data.steps || [],
      totalSteps: 1 + (data.total_steps || 0) // 1 for basic info + questionnaire steps
    }));
    
    console.log(`Position: ${positionKey}, Total steps: ${1 + data.total_steps}`);
  } catch (error) {
    console.error('Error fetching questionnaire steps:', error);
    // Fallback: just basic info step
    setFormState(prev => ({
      ...prev,
      selectedPosition: positionKey,
      questionnaireSteps: [],
      totalSteps: 1
    }));
  }
};
```

### 3. Step Rendering

```typescript
const renderCurrentStep = () => {
  const { currentStep, questionnaireSteps } = formState;
  
  // Step 0: Basic Information + Position Selection
  if (currentStep === 0) {
    return (
      <BasicInfoForm
        onPositionChange={handlePositionChange}
        onSubmit={handleBasicInfoSubmit}
        initialData={formState.formData.basicInfo}
      />
    );
  }
  
  // Steps 1+: Questionnaire steps
  const questionnaireIndex = currentStep - 1;
  const questionnaire = questionnaireSteps[questionnaireIndex];
  
  if (!questionnaire) {
    return <div>Error: Questionnaire not found</div>;
  }
  
  return (
    <QuestionnaireStepForm
      questionnaire={questionnaire}
      onSubmit={handleQuestionnaireSubmit}
      initialAnswers={formState.formData.questionnaireAnswers[questionnaire.id]}
    />
  );
};
```

### 4. Navigation Controls

```typescript
const handleNext = () => {
  if (formState.currentStep < formState.totalSteps - 1) {
    setFormState(prev => ({
      ...prev,
      currentStep: prev.currentStep + 1
    }));
  }
};

const handlePrevious = () => {
  if (formState.currentStep > 0) {
    setFormState(prev => ({
      ...prev,
      currentStep: prev.currentStep - 1
    }));
  }
};

const isLastStep = () => {
  return formState.currentStep === formState.totalSteps - 1;
};

const isFirstStep = () => {
  return formState.currentStep === 0;
};
```

### 5. Progress Indicator

```typescript
const ProgressIndicator = () => {
  const { currentStep, totalSteps, questionnaireSteps } = formState;
  
  return (
    <div className="progress-indicator">
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
        />
      </div>
      
      <div className="step-info">
        <span>Passo {currentStep + 1} de {totalSteps}</span>
        {currentStep === 0 ? (
          <span>Dados Pessoais</span>
        ) : (
          <span>{questionnaireSteps[currentStep - 1]?.title}</span>
        )}
      </div>
    </div>
  );
};
```

### 6. Form Submission

```typescript
const handleBasicInfoSubmit = (data: any) => {
  // Save basic info
  setFormState(prev => ({
    ...prev,
    formData: {
      ...prev.formData,
      basicInfo: data
    }
  }));
  
  // If no questionnaire steps, submit immediately
  if (formState.totalSteps === 1) {
    submitCompleteForm();
  } else {
    // Otherwise, go to next step
    handleNext();
  }
};

const handleQuestionnaireSubmit = (templateId: number, answers: any[]) => {
  // Save questionnaire answers
  setFormState(prev => ({
    ...prev,
    formData: {
      ...prev.formData,
      questionnaireAnswers: {
        ...prev.formData.questionnaireAnswers,
        [templateId]: answers
      }
    }
  }));
  
  // If last step, submit complete form
  if (isLastStep()) {
    submitCompleteForm();
  } else {
    handleNext();
  }
};

const submitCompleteForm = async () => {
  try {
    // 1. Submit candidate basic info
    const candidateResponse = await fetch('/api/candidates/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formState.formData.basicInfo)
    });
    
    if (!candidateResponse.ok) {
      throw new Error('Failed to submit candidate');
    }
    
    const candidate = await candidateResponse.json();
    
    // 2. Submit each questionnaire response
    for (const [templateId, answers] of Object.entries(formState.formData.questionnaireAnswers)) {
      await fetch('/api/questionnaire-responses/submit/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: candidate.id,
          template_id: parseInt(templateId),
          answers: answers
        })
      });
    }
    
    // 3. Redirect to success page
    window.location.href = '/success/';
  } catch (error) {
    console.error('Error submitting form:', error);
    alert('Erro ao enviar formulário. Por favor, tente novamente.');
  }
};
```

### 7. Complete Component Example

```typescript
const MultiStepCandidateForm = () => {
  const [formState, setFormState] = useState<FormState>({
    currentStep: 0,
    totalSteps: 1,
    selectedPosition: null,
    questionnaireSteps: [],
    formData: {
      basicInfo: {},
      questionnaireAnswers: {}
    }
  });
  
  return (
    <div className="multi-step-form">
      <ProgressIndicator />
      
      <div className="form-content">
        {renderCurrentStep()}
      </div>
      
      <div className="form-navigation">
        {!isFirstStep() && (
          <button onClick={handlePrevious} className="btn-secondary">
            Voltar
          </button>
        )}
        
        {!isLastStep() && (
          <button onClick={handleNext} className="btn-primary">
            Próximo
          </button>
        )}
        
        {isLastStep() && (
          <button onClick={submitCompleteForm} className="btn-success">
            Enviar Candidatura
          </button>
        )}
      </div>
    </div>
  );
};
```

## Key Points

### 1. Dynamic Step Count
- **Always start with 1 step** (basic info)
- **Add questionnaire steps** when position is selected
- **Update totalSteps** = 1 + number of questionnaires

### 2. Position Selection Timing
- Position can be selected in Step 0
- When selected, immediately fetch questionnaire steps
- Update UI to show new total step count

### 3. Data Persistence
- Store all form data in state
- Allow going back to previous steps
- Pre-fill forms with saved data

### 4. Error Handling
- Handle API failures gracefully
- Fallback to basic info only if questionnaires fail to load
- Show user-friendly error messages

### 5. Validation
- Validate each step before allowing next
- Show validation errors inline
- Prevent submission with incomplete data

## Example API Responses

### Position with Questionnaires
```json
GET /api/questionnaires/steps-for-position/?position_key=Pintor

{
  "position_key": "Pintor",
  "total_steps": 3,
  "steps": [
    {
      "id": 1,
      "title": "Conhecimentos Técnicos",
      "step_number": 1,
      "description": "Avalie seus conhecimentos",
      "questions": [
        {
          "id": 1,
          "question_text": "Você tem experiência com pintura em altura?",
          "question_type": "single_select",
          "options": [
            {"id": 1, "option_text": "Sim"},
            {"id": 2, "option_text": "Não"}
          ]
        }
      ]
    },
    {
      "id": 2,
      "title": "Ferramentas",
      "step_number": 2,
      "questions": [...]
    }
  ]
}
```

### Position without Questionnaires
```json
GET /api/questionnaires/steps-for-position/?position_key=Auxiliar

{
  "position_key": "Auxiliar",
  "total_steps": 0,
  "steps": []
}
```

## Styling Recommendations

```css
.progress-indicator {
  margin-bottom: 2rem;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #45a049);
  transition: width 0.3s ease;
}

.step-info {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.form-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  gap: 1rem;
}
```

## Testing Checklist

- [ ] Position selection triggers step loading
- [ ] Correct number of steps shown for each position
- [ ] Navigation between steps works
- [ ] Form data persists when going back
- [ ] Validation works on each step
- [ ] Final submission includes all data
- [ ] Error handling works for API failures
- [ ] Progress indicator updates correctly
- [ ] Works with positions that have no questionnaires
- [ ] Works with positions that have multiple questionnaires
