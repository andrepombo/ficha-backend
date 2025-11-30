# Questionnaire Integration in Candidate Application Form

## Overview

The questionnaire system has been integrated into the existing candidate application form as a **multi-step process**:

1. **Page 1**: Personal Information (existing form fields)
2. **Page 2**: Questionnaire (dynamically loaded based on position)
3. **Page 3**: Review and Submit

## How It Works

### Frontend (JavaScript)

The file `apps/candidate/static/candidate/js/questionnaire-integration.js` automatically converts the single-page form into a multi-step wizard:

1. **On page load**, it wraps the existing form content into "Step 1"
2. **Creates Step 2** with a questionnaire container
3. **Creates Step 3** with a review page
4. **Adds step indicator** at the top showing progress
5. **Replaces submit button** with navigation buttons

### Backend (Django View)

The `application_form_view` in `apps/candidate/views.py` has been updated to:

1. **Accept questionnaire answers** via hidden field `questionnaire_answers`
2. **Submit answers to API** after candidate is created
3. **Handle errors gracefully** - questionnaire errors don't block candidate submission

## User Flow

### Step 1: Personal Information
- Candidate fills out all existing form fields
- Clicks "Próximo: Questionário →"
- Form validates required fields before proceeding

### Step 2: Questionnaire
- **Automatically loads** questionnaire for selected position via API
- **If no questionnaire exists**: Shows message and allows skipping
- **If questionnaire exists**: Renders questions with options
- Candidate selects answers (checkbox for multi-select, radio for single-select)
- Clicks "Próximo: Revisão →"
- Validates all questions are answered

### Step 3: Review
- Shows summary of personal info
- Shows questionnaire completion status
- Candidate clicks "Enviar Candidatura ✓"
- Form submits with both candidate data and questionnaire answers

## Technical Details

### Hidden Fields Added

```html
<input type="hidden" name="template_id" id="template_id" value="">
<input type="hidden" name="questionnaire_answers" id="questionnaire_answers" value="">
```

### Questionnaire Answers Format

```json
[
  {
    "question_id": 1,
    "selected_option_ids": [1, 2]
  },
  {
    "question_id": 2,
    "selected_option_ids": [5]
  }
]
```

### API Endpoint Used

```
GET /api/questionnaires/active/?position_key={position}
```

Returns questionnaire with questions and options (without correct answers).

### Submission Flow

1. Form submits to existing `application_form_view`
2. Candidate is created/saved normally
3. If `questionnaire_answers` field has data:
   - Parse JSON
   - Submit to questionnaire API
   - Score is calculated automatically
4. Redirect to success page

## Features

### Responsive Design
- Mobile-friendly step indicator
- Stacks on small screens
- Touch-friendly option buttons

### Validation
- **Step 1**: Validates required fields
- **Step 2**: Validates all questions answered (if questionnaire exists)
- **Step 3**: Final confirmation

### Error Handling
- **No questionnaire**: Shows friendly message, allows continuing
- **API error**: Shows error message, allows skipping
- **Submission error**: Logs error but doesn't block candidate creation

### User Experience
- **Progress indicator**: Shows current step
- **Navigation**: Back/Next buttons
- **Visual feedback**: Hover effects on options
- **Loading states**: Spinner while loading questionnaire
- **Smooth scrolling**: Auto-scroll to top on step change

## Configuration

### Enable/Disable Questionnaire

To disable the questionnaire integration, simply remove or comment out the script include:

```django
<!-- Questionnaire Integration -->
<!-- <script src="{% static 'candidate/js/questionnaire-integration.js' %}"></script> -->
```

### Customize Steps

Edit `questionnaire-integration.js` to:
- Change step labels
- Modify validation rules
- Customize styling
- Add/remove steps

## Styling

All styles are included in the JavaScript file and injected dynamically. Key classes:

- `.step-indicator` - Progress bar at top
- `.step` - Individual step circle
- `.form-step` - Each page container
- `.question-card` - Question container
- `.option-label` - Answer option button
- `.step-navigation` - Back/Next button container

## Testing

### Test Without Questionnaire
1. Select a position that has no questionnaire
2. Form should show message and allow skipping Step 2

### Test With Questionnaire
1. Create a questionnaire in admin for a position
2. Activate the questionnaire
3. Fill form and select that position
4. Step 2 should load questions
5. Answer all questions
6. Review and submit
7. Check admin for candidate and questionnaire response

### Test Validation
1. Try to proceed from Step 1 without filling required fields
2. Try to proceed from Step 2 without answering all questions
3. Should show validation errors

## Troubleshooting

### Questionnaire Not Loading
- Check position is selected in Step 1
- Check questionnaire exists and is active for that position
- Check browser console for API errors
- Verify `/api/questionnaires/active/` endpoint is accessible

### Form Not Submitting
- Check browser console for JavaScript errors
- Verify `questionnaire_answers` hidden field has data
- Check Django logs for backend errors

### Styling Issues
- Ensure Bootstrap CSS is loaded
- Check for CSS conflicts with existing styles
- Verify JavaScript is not blocked

## Files Modified

1. **`apps/candidate/views.py`**
   - Added questionnaire submission handling
   - Added imports for JSON and API calls

2. **`apps/candidate/templates/candidate/application_form.html`**
   - Added `{% load static %}`
   - Added script include for questionnaire integration

3. **`apps/candidate/static/candidate/js/questionnaire-integration.js`** (NEW)
   - Complete multi-step form logic
   - Questionnaire loading and rendering
   - Answer tracking and submission

## Future Enhancements

- [ ] Save progress (allow returning to complete later)
- [ ] Show score to candidate after submission
- [ ] Add question types (text input, rating, etc.)
- [ ] Add conditional logic (show questions based on previous answers)
- [ ] Add time limits per questionnaire
- [ ] Add question randomization
- [ ] Add "Save as draft" functionality

## Support

For issues or questions:
1. Check browser console for errors
2. Check Django logs for backend errors
3. Verify questionnaire exists and is active
4. Test API endpoint directly: `/api/questionnaires/active/?position_key=YourPosition`

## Summary

✅ **Multi-step form** - 3 pages with progress indicator  
✅ **Dynamic loading** - Fetches questionnaire based on position  
✅ **Graceful fallback** - Works without questionnaire  
✅ **Automatic submission** - Scores calculated server-side  
✅ **No breaking changes** - Existing form still works  
✅ **Mobile responsive** - Works on all devices  

The integration is **production-ready** and requires no changes to existing form fields or validation logic!
