# Form Flow Specification

## Correct Multi-Step Flow

### Step 0: Position Selection ONLY
**Fields shown:**
- Cargo Pretendido (Job Position) - Dropdown

**Behavior:**
- User selects position from dropdown
- On selection, fetch questionnaire steps for that position
- Calculate total steps: 1 (basic info) + N (questionnaires)
- Show "Próximo" button to proceed

### Step 1: Basic Personal Information (Dados Pessoais)
**Fields shown:**
- Nome Completo
- CPF
- Email
- Telefone
- Data de Nascimento
- Sexo
- Endereço
- Cidade/Estado
- All other basic candidate fields

**Behavior:**
- This is always shown as step 1 after position selection
- User fills in personal information
- Click "Próximo" to continue

### Steps 2+: Position-Specific Questionnaires (if any)
**Fields shown:**
- Questions from questionnaire templates (ordered by step_number)

**Behavior:**
- Only shown if position has active questionnaires
- Each questionnaire is a separate step
- User answers questions
- Click "Próximo" to continue or "Enviar" on last step

## Flow Examples

### Example 1: Pintor with 4 Questionnaires
```
Step 0: [Cargo Pretendido: Pintor ▼] → Próximo
Step 1: [Dados Pessoais Form] → Próximo
Step 2: [Conhecimentos Técnicos Questionnaire] → Próximo
Step 3: [Experiência com Ferramentas Questionnaire] → Próximo
Step 4: [Segurança no Trabalho Questionnaire] → Próximo
Step 5: [Disponibilidade Questionnaire] → Enviar
```
**Total: 6 steps** (1 position + 1 basic info + 4 questionnaires)

### Example 2: Auxiliar with No Questionnaires
```
Step 0: [Cargo Pretendido: Auxiliar ▼] → Próximo
Step 1: [Dados Pessoais Form] → Enviar
```
**Total: 2 steps** (1 position + 1 basic info + 0 questionnaires)

### Example 3: Encarregado with 2 Questionnaires
```
Step 0: [Cargo Pretendido: Encarregado ▼] → Próximo
Step 1: [Dados Pessoais Form] → Próximo
Step 2: [Liderança Questionnaire] → Próximo
Step 3: [Gestão de Equipe Questionnaire] → Enviar
```
**Total: 4 steps** (1 position + 1 basic info + 2 questionnaires)

## Frontend State Management

```typescript
interface FormState {
  currentStep: number;
  totalSteps: number;
  selectedPosition: string | null;
  questionnaireSteps: QuestionnaireTemplate[];
  formData: {
    position: string;           // From step 0
    basicInfo: any;            // From step 1
    questionnaireAnswers: Record<number, any[]>; // From steps 2+
  };
}

// Initial state
const initialState = {
  currentStep: 0,
  totalSteps: 1, // Just position selection initially
  selectedPosition: null,
  questionnaireSteps: [],
  formData: {
    position: '',
    basicInfo: {},
    questionnaireAnswers: {}
  }
};
```

## Step Rendering Logic

```typescript
const renderCurrentStep = () => {
  const { currentStep, selectedPosition, questionnaireSteps } = formState;
  
  // Step 0: Position Selection ONLY
  if (currentStep === 0) {
    return (
      <div className="position-selection-step">
        <h2>Selecione o Cargo Pretendido</h2>
        <select 
          value={selectedPosition || ''} 
          onChange={handlePositionChange}
          required
        >
          <option value="">Selecione...</option>
          <option value="Pintor">Pintor</option>
          <option value="Auxiliar de Pintor">Auxiliar de Pintor</option>
          <option value="Encarregado de Pintura">Encarregado de Pintura</option>
        </select>
        
        {selectedPosition && (
          <button onClick={handleNext}>Próximo</button>
        )}
      </div>
    );
  }
  
  // Step 1: Basic Personal Information
  if (currentStep === 1) {
    return (
      <BasicInfoForm
        positionApplied={selectedPosition}
        onSubmit={handleBasicInfoSubmit}
        initialData={formState.formData.basicInfo}
      />
    );
  }
  
  // Steps 2+: Questionnaires
  const questionnaireIndex = currentStep - 2; // -2 because step 0 is position, step 1 is basic info
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

## Position Change Handler

```typescript
const handlePositionChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
  const positionKey = event.target.value;
  
  if (!positionKey) {
    // Reset if no position selected
    setFormState(prev => ({
      ...prev,
      selectedPosition: null,
      questionnaireSteps: [],
      totalSteps: 1
    }));
    return;
  }
  
  try {
    // Fetch questionnaire steps for this position
    const response = await fetch(
      `/api/questionnaires/steps-for-position/?position_key=${encodeURIComponent(positionKey)}`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch questionnaire steps');
    }
    
    const data = await response.json();
    
    // Calculate total steps:
    // 1 (position selection) + 1 (basic info) + N (questionnaires)
    const totalSteps = 1 + 1 + (data.total_steps || 0);
    
    setFormState(prev => ({
      ...prev,
      selectedPosition: positionKey,
      questionnaireSteps: data.steps || [],
      totalSteps: totalSteps,
      formData: {
        ...prev.formData,
        position: positionKey
      }
    }));
    
    console.log(`Position: ${positionKey}`);
    console.log(`Total steps: ${totalSteps} (1 position + 1 basic info + ${data.total_steps} questionnaires)`);
    
  } catch (error) {
    console.error('Error fetching questionnaire steps:', error);
    // Fallback: position + basic info only
    setFormState(prev => ({
      ...prev,
      selectedPosition: positionKey,
      questionnaireSteps: [],
      totalSteps: 2, // position + basic info
      formData: {
        ...prev.formData,
        position: positionKey
      }
    }));
  }
};
```

## Progress Indicator

```typescript
const ProgressIndicator = () => {
  const { currentStep, totalSteps, selectedPosition, questionnaireSteps } = formState;
  
  const getStepLabel = () => {
    if (currentStep === 0) {
      return 'Cargo Pretendido';
    } else if (currentStep === 1) {
      return 'Dados Pessoais';
    } else {
      const questionnaireIndex = currentStep - 2;
      return questionnaireSteps[questionnaireIndex]?.title || 'Questionário';
    }
  };
  
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
        <span className="step-label">{getStepLabel()}</span>
      </div>
      
      {selectedPosition && (
        <div className="position-badge">
          Cargo: {selectedPosition}
        </div>
      )}
    </div>
  );
};
```

## Navigation Logic

```typescript
const handleNext = () => {
  // Validate current step before proceeding
  if (currentStep === 0 && !formState.selectedPosition) {
    alert('Por favor, selecione um cargo.');
    return;
  }
  
  if (currentStep < formState.totalSteps - 1) {
    setFormState(prev => ({
      ...prev,
      currentStep: prev.currentStep + 1
    }));
  }
};

const handlePrevious = () => {
  if (currentStep > 0) {
    setFormState(prev => ({
      ...prev,
      currentStep: prev.currentStep - 1
    }));
  }
};

const canProceed = () => {
  if (currentStep === 0) {
    return formState.selectedPosition !== null;
  }
  return true; // Other steps handle their own validation
};
```

## Complete Flow Visualization

```
┌─────────────────────────────────────────┐
│  Step 0: Position Selection             │
│  ┌────────────────────────────────────┐ │
│  │ Cargo Pretendido: [Pintor      ▼] │ │
│  └────────────────────────────────────┘ │
│              [Próximo →]                 │
└─────────────────────────────────────────┘
                    ↓
         API: /api/questionnaires/steps-for-position/
                    ↓
         Response: 4 questionnaires found
                    ↓
         totalSteps = 1 + 1 + 4 = 6
                    ↓
┌─────────────────────────────────────────┐
│  Step 1: Basic Information              │
│  ┌────────────────────────────────────┐ │
│  │ Nome: [________________]           │ │
│  │ CPF: [___.___.___-__]              │ │
│  │ Email: [________________]          │ │
│  │ ... (all basic fields)             │ │
│  └────────────────────────────────────┘ │
│  [← Voltar]           [Próximo →]       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Step 2: Conhecimentos Técnicos         │
│  [Questionnaire questions...]           │
│  [← Voltar]           [Próximo →]       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Step 3: Experiência com Ferramentas    │
│  [Questionnaire questions...]           │
│  [← Voltar]           [Próximo →]       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Step 4: Segurança no Trabalho          │
│  [Questionnaire questions...]           │
│  [← Voltar]           [Próximo →]       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Step 5: Disponibilidade (LAST)         │
│  [Questionnaire questions...]           │
│  [← Voltar]           [Enviar ✓]        │
└─────────────────────────────────────────┘
```

## Key Points

1. **Step 0 is ONLY position selection** - no other fields
2. **Step 1 is ALWAYS basic info** - shown after position is selected
3. **Steps 2+ are questionnaires** - only if position has them
4. **Total steps** = 1 (position) + 1 (basic info) + N (questionnaires)
5. **Position cannot be changed** after step 0 without going back
6. **Progress shows** which step and what content (Cargo → Dados Pessoais → Questionnaires)

## Validation Rules

- **Step 0**: Must select a position to proceed
- **Step 1**: Must fill required basic info fields
- **Steps 2+**: Must answer all required questions
- **Navigation**: Can go back to any previous step
- **Data persistence**: All entered data is preserved when navigating

## Submission

Final submission happens on the last step and includes:
1. Position (from step 0)
2. Basic candidate info (from step 1)
3. All questionnaire responses (from steps 2+)

All data is submitted together as one complete candidate application.
