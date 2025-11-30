# Simple Frontend Change: Split Form into Steps

## TL;DR

**Move the "Cargo Pretendido" dropdown to its own page before "Dados Pessoais".**

No backend changes needed - just frontend UI restructuring.

---

## Current Situation

Your form currently shows everything on one page:
- Cargo Pretendido dropdown
- All personal info fields (Nome, CPF, Email, etc.)
- Questionnaires (if any)

## What You Want

**Step 0**: Show ONLY "Cargo Pretendido" dropdown  
**Step 1**: Show all personal info fields  
**Steps 2+**: Show questionnaires (already working)

---

## Minimal Code Changes

### 1. Add State (3 lines)
```typescript
const [currentStep, setCurrentStep] = useState(0);
const [selectedPosition, setSelectedPosition] = useState('');
const [questionnaireSteps, setQuestionnaireSteps] = useState([]);
```

### 2. When Position Selected (fetch questionnaires)
```typescript
const handlePositionSelect = async (position) => {
  setSelectedPosition(position);
  
  // Fetch questionnaires for this position
  const response = await fetch(
    `/api/questionnaires/steps-for-position/?position_key=${position}`
  );
  const data = await response.json();
  setQuestionnaireSteps(data.steps || []);
};
```

### 3. Render Logic
```typescript
// Step 0: ONLY position dropdown
if (currentStep === 0) {
  return (
    <>
      <h2>Cargo Pretendido</h2>
      <select onChange={(e) => handlePositionSelect(e.target.value)}>
        <option value="">Selecione...</option>
        <option value="Pintor">Pintor</option>
        <option value="Auxiliar de Pintor">Auxiliar de Pintor</option>
      </select>
      
      {selectedPosition && (
        <button onClick={() => setCurrentStep(1)}>Próximo</button>
      )}
    </>
  );
}

// Step 1: Your existing form (remove Cargo Pretendido from it)
if (currentStep === 1) {
  return (
    <>
      <button onClick={() => setCurrentStep(0)}>Voltar</button>
      {/* Your existing Dados Pessoais form */}
      <button onClick={() => setCurrentStep(2)}>Próximo</button>
    </>
  );
}

// Steps 2+: Your existing questionnaire logic
```

---

## That's It!

**3 simple changes:**
1. Add step state
2. Split the form into conditional renders based on `currentStep`
3. Remove "Cargo Pretendido" from the main form (it's now in Step 0)

The backend already supports everything - you just need to reorganize the frontend UI.
