# Frontend: Split Cargo Pretendido to Separate Page

## What to Change

You already have a working form. You just need to **split it into steps**:

### Current Flow (Single Page)
```
┌─────────────────────────────────────┐
│ • Cargo Pretendido (dropdown)       │
│ • Nome Completo                     │
│ • CPF                               │
│ • Email                             │
│ • ... (all other fields)            │
│                                     │
│           [Enviar]                  │
└─────────────────────────────────────┘
```

### New Flow (Multi-Step)
```
┌─────────────────────────────────────┐
│ Step 0: Position Selection          │
│                                     │
│ • Cargo Pretendido (dropdown)       │
│                                     │
│           [Próximo →]               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Step 1: Dados Pessoais              │
│                                     │
│ • Nome Completo                     │
│ • CPF                               │
│ • Email                             │
│ • ... (all other fields)            │
│                                     │
│ [← Voltar]      [Próximo →]        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Steps 2+: Questionnaires (if any)   │
│                                     │
│ [← Voltar]      [Enviar]            │
└─────────────────────────────────────┘
```

## Implementation Steps

### 1. Add Step State

```typescript
const [currentStep, setCurrentStep] = useState(0);
const [selectedPosition, setSelectedPosition] = useState('');
const [totalSteps, setTotalSteps] = useState(1); // Will update when position selected
```

### 2. Handle Position Selection

```typescript
const handlePositionChange = async (position: string) => {
  setSelectedPosition(position);
  
  // Fetch questionnaires for this position
  try {
    const response = await fetch(
      `/api/questionnaires/steps-for-position/?position_key=${position}`
    );
    const data = await response.json();
    
    // Calculate total steps: 1 (position) + 1 (basic info) + N (questionnaires)
    setTotalSteps(1 + 1 + (data.total_steps || 0));
  } catch (error) {
    console.error('Error fetching questionnaires:', error);
    setTotalSteps(2); // Fallback: just position + basic info
  }
};
```

### 3. Render Based on Current Step

```typescript
const renderCurrentStep = () => {
  // Step 0: Show ONLY Cargo Pretendido
  if (currentStep === 0) {
    return (
      <div className="position-selection-step">
        <h2>Selecione o Cargo Pretendido</h2>
        <p>Escolha a posição para a qual você deseja se candidatar</p>
        
        <select 
          value={selectedPosition} 
          onChange={(e) => handlePositionChange(e.target.value)}
          required
        >
          <option value="">Selecione...</option>
          <option value="Pintor">Pintor</option>
          <option value="Auxiliar de Pintor">Auxiliar de Pintor</option>
          <option value="Encarregado de Pintura">Encarregado de Pintura</option>
        </select>
        
        {selectedPosition && (
          <button onClick={() => setCurrentStep(1)}>
            Próximo →
          </button>
        )}
      </div>
    );
  }
  
  // Step 1: Show existing Dados Pessoais form (without Cargo Pretendido)
  if (currentStep === 1) {
    return (
      <div className="basic-info-step">
        <h2>Dados Pessoais</h2>
        
        {/* Remove the Cargo Pretendido dropdown from here */}
        {/* Keep all other fields: Nome, CPF, Email, etc. */}
        
        <input type="text" name="nome" placeholder="Nome Completo" />
        <input type="text" name="cpf" placeholder="CPF" />
        <input type="email" name="email" placeholder="Email" />
        {/* ... all other existing fields ... */}
        
        <div className="navigation">
          <button onClick={() => setCurrentStep(0)}>
            ← Voltar
          </button>
          <button onClick={handleBasicInfoNext}>
            Próximo →
          </button>
        </div>
      </div>
    );
  }
  
  // Steps 2+: Questionnaires (if any)
  // Your existing questionnaire rendering logic
  const questionnaireIndex = currentStep - 2;
  return renderQuestionnaire(questionnaireIndex);
};
```

### 4. Update Form Submission

When submitting the final form, include the `selectedPosition`:

```typescript
const submitForm = async () => {
  const formData = {
    position_applied: selectedPosition, // From step 0
    full_name: formValues.nome,         // From step 1
    cpf: formValues.cpf,                // From step 1
    // ... all other fields from step 1
  };
  
  // Submit to backend
  await fetch('/api/candidates/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
};
```

## Key Changes Summary

### What to Remove
- ❌ Remove "Cargo Pretendido" dropdown from the main Dados Pessoais form

### What to Add
- ✅ Add step state management (`currentStep`)
- ✅ Add new Step 0 component with ONLY Cargo Pretendido
- ✅ Add navigation buttons (Voltar/Próximo)
- ✅ Add step rendering logic based on `currentStep`

### What to Keep
- ✅ All existing form fields (just move them to Step 1)
- ✅ All existing validation logic
- ✅ All existing questionnaire logic
- ✅ All existing submission logic

## Visual Example

### Step 0 Component
```jsx
<div className="step-container">
  <div className="progress-bar">
    <div className="progress" style={{ width: '16.67%' }}></div>
  </div>
  
  <h1>Passo 1 de 6</h1>
  <h2>Cargo Pretendido</h2>
  
  <div className="form-group">
    <label>Selecione o cargo desejado:</label>
    <select 
      value={selectedPosition}
      onChange={(e) => handlePositionChange(e.target.value)}
      className="form-control"
    >
      <option value="">-- Selecione --</option>
      <option value="Pintor">Pintor</option>
      <option value="Auxiliar de Pintor">Auxiliar de Pintor</option>
      <option value="Encarregado de Pintura">Encarregado de Pintura</option>
    </select>
  </div>
  
  {selectedPosition && (
    <div className="form-actions">
      <button 
        className="btn btn-primary"
        onClick={() => setCurrentStep(1)}
      >
        Próximo →
      </button>
    </div>
  )}
</div>
```

### Step 1 Component (Existing Form)
```jsx
<div className="step-container">
  <div className="progress-bar">
    <div className="progress" style={{ width: '33.33%' }}></div>
  </div>
  
  <h1>Passo 2 de 6</h1>
  <h2>Dados Pessoais</h2>
  <p className="text-muted">Cargo selecionado: {selectedPosition}</p>
  
  {/* Your existing form fields here */}
  <div className="form-group">
    <label>Nome Completo</label>
    <input type="text" className="form-control" />
  </div>
  
  {/* ... all other fields ... */}
  
  <div className="form-actions">
    <button 
      className="btn btn-secondary"
      onClick={() => setCurrentStep(0)}
    >
      ← Voltar
    </button>
    <button 
      className="btn btn-primary"
      onClick={handleNext}
    >
      Próximo →
    </button>
  </div>
</div>
```

## No Backend Changes Needed!

The backend already supports this flow:
- ✅ `/api/positions/` - Returns available positions
- ✅ `/api/questionnaires/steps-for-position/?position_key=X` - Returns questionnaires for position
- ✅ `/api/candidates/` - Accepts `position_applied` field
- ✅ `/api/questionnaire-responses/submit/` - Submits questionnaire answers

You just need to update the **frontend UI** to split the form into steps!
