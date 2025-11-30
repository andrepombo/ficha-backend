# Position Selection Page Implementation - COMPLETE

## What Was Done

Created a **separate first page** for "Cargo Pretendido" selection that loads as the main URL.

## Changes Made

### 1. New Template Created
**File:** `/apps/candidate/templates/candidate/position_selection.html`
- Clean, focused page showing ONLY "Cargo Pretendido" dropdown
- Loads positions dynamically from `/api/positions/`
- "Próximo" button to proceed to Step 1
- Progress indicator showing "Passo 1 de X"

### 2. New View Added
**File:** `/apps/candidate/views.py`
- Added `position_selection_view()` function
- Stores selected position in session
- Calculates total steps based on questionnaires
- Redirects to main form after selection

### 3. URL Routing Updated
**File:** `/core/urls.py`
- **Changed:** Root URL `/` now points to `position_selection_view` (Step 0)
- **Changed:** Main form moved to `/form/` (Step 1)
- Position selection is now the **first page users see**

### 4. Main Form Updated
**File:** `/apps/candidate/templates/candidate/application_form.html`
- **Removed:** "Cargo Pretendido" dropdown from main form
- **Added:** Hidden input with selected position
- **Added:** Info banner showing selected position with "Alterar" link
- **Added:** Progress indicator showing current step

### 5. Form View Updated
**File:** `/apps/candidate/views.py` - `application_form_view()`
- Added session check - redirects to position selection if not set
- Passes `selected_position` to template
- Passes step information for progress display

## How It Works Now

### User Flow:
```
1. User visits: http://yoursite.com/
   → Sees: Position Selection Page (Step 0)
   → Selects: "Pintor" from dropdown
   → Clicks: "Próximo" button

2. User redirected to: http://yoursite.com/form/
   → Sees: "Cargo Selecionado: Pintor" banner
   → Sees: "Passo 2 de 6" progress
   → Fills: All personal information fields
   → Submits: Form as before

3. Rest of flow continues as before
```

### Session Management:
- `selected_position`: Stores chosen position
- `total_steps`: Calculated as 1 + 1 + questionnaire_count
- Session persists across page navigation

## Testing

### Test Step 0 (Position Selection):
1. Visit: `http://localhost:8000/`
2. Should see: Clean page with only "Cargo Pretendido" dropdown
3. Select a position
4. Click "Próximo"
5. Should redirect to `/form/`

### Test Step 1 (Dados Pessoais):
1. After selecting position, should see main form
2. Should see: "Cargo Selecionado: [Position]" banner at top
3. Should see: Progress indicator
4. Should NOT see: Position dropdown in form
5. Can click "Alterar" to go back and change position

### Test Direct Access Protection:
1. Try visiting `/form/` directly without selecting position
2. Should redirect back to `/` with warning message

## Files Modified

1. ✅ `/apps/candidate/views.py` - Added position_selection_view
2. ✅ `/apps/candidate/templates/candidate/position_selection.html` - NEW FILE
3. ✅ `/apps/candidate/templates/candidate/application_form.html` - Updated
4. ✅ `/core/urls.py` - Changed root URL routing

## No Database Changes

✅ No migrations needed
✅ No model changes
✅ Uses existing session framework
✅ Uses existing API endpoints

## Rollback (if needed)

To revert to single-page form:

```python
# In core/urls.py, change back to:
path('', views.application_form_view, name='application_form'),
```

That's it! The position selection is now on its own page as the main entry point.
