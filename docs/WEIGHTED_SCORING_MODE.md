# Weighted Scoring Mode for Questionnaires

## Overview

A new scoring mode called **"Weighted"** has been added to the questionnaire system. This mode allows questions where all options have value, but different amounts of points.

## Use Case

In traditional scoring:
- **All-or-nothing**: Candidate must select ALL correct answers to get points
- **Partial**: Candidate gets points only for selecting correct answers (marked with `is_correct=True`)

In **weighted scoring**:
- Each option has a point value (`option_points`)
- The candidate gets credit based on the point value of their selection
- The score is normalized against the maximum option points
- **No options need to be marked as "correct"** - all options have value

## Example

Question: "Você percebe que o material enviado para a obra veio com cor diferente da solicitada. O encarregado não está no local. Você:"

Options:
- Option A: 1 point - "Interrompe o trabalho e espera o retorno do encarregado para decidir"
- Option B: 2 points - "Verifica se a cor pode ser ajustada com mistura, testa uma pequena"
- Option C: 3 points - "Continua o serviço com o material incorreto para não atrasar a obra"

If the question is worth 1 point total and the candidate selects Option A (1 pt):
- Score = (1 / 3) × 1.0 = 0.33 points

## Backend Changes

### Model Update
Added new scoring mode choice in `apps/candidate/models/questionnaire.py`:
```python
SCORING_MODE_CHOICES = [
    ('all_or_nothing', 'All or Nothing'),
    ('partial', 'Partial Credit'),
    ('weighted', 'Weighted (by option points)'),  # NEW
]
```

### Scoring Logic
Added weighted scoring logic in `apps/candidate/api_views/questionnaire_views.py`:

**For single-select questions:**
```python
elif question.scoring_mode == 'weighted':
    if question.question_type == 'single_select':
        selected_id = next(iter(selected_option_ids), None)
        if selected_id:
            all_options = list(question.options.all())
            max_points = max((opt.option_points or Decimal('0')) for opt in all_options)
            selected_option = next((opt for opt in all_options if opt.id == selected_id), None)
            selected_points = (selected_option.option_points or Decimal('0')) if selected_option else Decimal('0')
            if max_points and max_points > 0:
                fraction = Decimal(selected_points) / Decimal(max_points)
                total_score += (fraction * question.points)
```

**For multi-select questions:**
```python
else:
    all_options = list(question.options.all())
    total_option_points = sum((opt.option_points or Decimal('0')) for opt in all_options)
    if total_option_points and total_option_points > 0:
        selected_option_points = sum(
            (opt.option_points or Decimal('0'))
            for opt in all_options
            if opt.id in selected_option_ids
        )
        fraction = Decimal(selected_option_points) / Decimal(total_option_points)
        total_score += (fraction * question.points)
```

### Migration
Created migration `0036_add_weighted_scoring_mode.py` to add the new choice to the database.

### Automatic Score Recalculation
Added Django signal in `apps/candidate/signals.py` that automatically recalculates all response scores when a question is updated. This ensures:
- Scores stay accurate when question points change
- Scores update when scoring mode changes
- Selected options are preserved (not deleted)
- No manual recalculation needed

## Frontend Changes

### Questionnaire Builder
Updated `src/components/questionnaires/QuestionnaireBuilder.tsx`:

**Dropdown Options:**
- Added "Ponderado (por pontos)" option to the scoring mode dropdown
- Shows option_points input field for both "Parcial" and "Ponderado" modes

**Validation:**
- For weighted mode: doesn't require any option to be marked as correct
- For weighted mode: requires at least one option to have points > 0
- For partial/all-or-nothing: still requires at least one correct answer

### Candidate Detail Page
Updated `src/pages/CandidateDetail.tsx` to display weighted scoring with color-coded feedback:

**Visual Indicators:**
- **Green**: Best answer (selected option has maximum points)
- **Yellow**: Partial answer (selected option has points but not the maximum)
- **Red**: Zero points answer (selected option has 0 points)
- Shows point values next to each option
- No "Correta/Incorreta" badge (since all options have value)
- "Resposta do candidato" badge matches the quality color

**Display Logic:**
```typescript
const isWeightedScoring = question.scoring_mode === 'weighted';
if (isWeightedScoring && hasAnswer) {
  const selectedOption = question.options?.find((opt: any) => selectedOptionIds.has(opt.id));
  const selectedPoints = selectedOption?.option_points || 0;
  
  if (selectedPoints === 0) {
    weightedColor = 'red'; // Zero points
  } else if (selectedPoints === maxOptionPoints) {
    weightedColor = 'green'; // Best answer
  } else {
    weightedColor = 'yellow'; // Partial answer
  }
}
```

## How to Use

### Creating a Weighted Question

1. Go to Django Admin → Questions
2. Create or edit a question
3. Set **Scoring Mode** to "Weighted (by option points)"
4. For each option, set the `option_points` field (e.g., 1, 2, 3)
5. You can optionally mark one as `is_correct=True` for reference, but it's not required for scoring

### Scoring Calculation

The formula is:
```
question_score = (selected_option_points / max_option_points) × question.points
```

Example:
- Question worth: 1.0 points
- Options: 1 pt, 2 pts, 3 pts (max = 3)
- Candidate selects: 1 pt option
- Score: (1/3) × 1.0 = 0.33 points

## Migration Instructions

```bash
cd /home/lock221/pinte_fichas/ficha-backend
python manage.py migrate candidate
```

The migration has already been applied.

## Testing

To test the weighted scoring:
1. Create a questionnaire with weighted scoring mode
2. Set different `option_points` values for each option
3. Have a candidate submit the questionnaire
4. Check the candidate detail page - it should show the weighted score
5. Verify the score calculation matches the formula above

## Notes

- The `is_correct` field is ignored in weighted scoring mode
- All options should have `option_points` set for proper scoring
- If `option_points` is 0 or not set, that option contributes 0 to the score
- The frontend displays point values to make it clear this is a weighted question
