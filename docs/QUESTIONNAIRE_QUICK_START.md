# Questionnaire System - Quick Start Guide

## What Was Implemented

A complete **per-position questionnaire system** with:
- ✅ Dynamic questions created on the frontend
- ✅ Multiple-choice (multi-select) questions
- ✅ Server-side scoring (all-or-nothing mode)
- ✅ Analytics endpoints for reporting
- ✅ Admin-only template management
- ✅ Public API for candidates to submit answers

## Key Features

1. **Relational Database Design** - Optimized for analytics and filtering
2. **Admin Builder** - Create questionnaires via API or Django admin
3. **Automatic Scoring** - Server validates and computes scores
4. **Analytics** - Track performance by position, question, and option
5. **Versioning** - Track template versions over time

## Quick Test

### 1. Access Django Admin
```
http://localhost:8000/admin/candidate/
```

Create a questionnaire template:
- **QuestionnaireTemplate** → Add new
  - Position key: `Painter`
  - Title: `Safety Test`
  - Is active: ✓

Add questions inline or separately.

### 2. API Endpoints

**Get active template for a position:**
```bash
curl http://localhost:8000/api/questionnaires/active/?position_key=Painter
```

**Submit answers:**
```bash
curl -X POST http://localhost:8000/api/questionnaire-responses/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 1,
    "template_id": 1,
    "answers": [
      {"question_id": 1, "selected_option_ids": [1, 2]}
    ]
  }'
```

**Get analytics:**
```bash
curl http://localhost:8000/api/questionnaire-responses/analytics/by-position/
```

## Frontend Integration

### Admin Builder Page (New Sidebar Item)

Create a new page in your frontend at `/questionnaires` with:

1. **Template List** - Show all templates, filter by position
2. **Template Builder**:
   - Form to create template (position, title)
   - Add questions (text, type, points)
   - Add options per question (text, is_correct, order)
   - Activate/deactivate button

Example React component structure:
```
/src/pages/Questionnaires.tsx
  ├─ TemplateList
  ├─ TemplateBuilder
  │   ├─ QuestionForm
  │   └─ OptionForm
  └─ TemplateAnalytics
```

### Candidate Form Integration

In your existing candidate application form:

1. **Fetch template** when form loads (based on position)
2. **Render questions** dynamically
3. **Submit answers** along with candidate data (or separately)

```typescript
// Fetch template
const template = await fetch(
  `/api/questionnaires/active/?position_key=${position}`
).then(r => r.json());

// Render
{template.questions.map(q => (
  <QuestionCard key={q.id} question={q} />
))}

// Submit
await fetch('/api/questionnaire-responses/submit/', {
  method: 'POST',
  body: JSON.stringify({ candidate_id, template_id, answers })
});
```

## Files Created

### Backend
- `apps/candidate/models/questionnaire.py` - 5 models
- `apps/candidate/serializers.py` - Added questionnaire serializers
- `apps/candidate/api_views/questionnaire_views.py` - 4 ViewSets
- `apps/candidate/admin.py` - Added 5 admin classes
- `apps/candidate/api_urls.py` - Added 4 routes
- `apps/candidate/migrations/0032_*.py` - Database migration
- `docs/QUESTIONNAIRE_SYSTEM.md` - Full documentation

### Frontend (To Do)
- Create `/src/pages/Questionnaires.tsx` - Admin builder
- Update sidebar to include "Questionnaires" link
- Integrate questionnaire fetching in candidate form

## API Routes Summary

| Endpoint | Method | Permission | Description |
|----------|--------|------------|-------------|
| `/api/questionnaires/` | GET, POST | Admin | List/create templates |
| `/api/questionnaires/{id}/` | GET, PUT, DELETE | Admin | Manage template |
| `/api/questionnaires/active/` | GET | Public | Get active template by position |
| `/api/questionnaires/{id}/activate/` | POST | Admin | Activate template |
| `/api/questionnaires/{id}/stats/` | GET | Admin | Template statistics |
| `/api/questions/` | GET, POST | Admin | List/create questions |
| `/api/questions/{id}/` | GET, PUT, DELETE | Admin | Manage question |
| `/api/question-options/` | GET, POST | Admin | List/create options |
| `/api/question-options/{id}/` | GET, PUT, DELETE | Admin | Manage option |
| `/api/questionnaire-responses/` | GET | Admin | List responses |
| `/api/questionnaire-responses/submit/` | POST | Public | Submit answers |
| `/api/questionnaire-responses/analytics/by-position/` | GET | Admin | Position analytics |
| `/api/questionnaire-responses/analytics/option-distribution/` | GET | Admin | Option stats |

## Database Schema

```
QuestionnaireTemplate (per position)
  ├─ Question (multiple)
  │   └─ QuestionOption (multiple)
  │       └─ is_correct (boolean)
  └─ CandidateQuestionnaireResponse (multiple)
      └─ CandidateSelectedOption (multiple)
          └─ links to QuestionOption
```

## Scoring Logic

**All-or-Nothing (default):**
- Candidate must select **exactly** the correct options
- Correct = full points, incorrect = 0 points

Example:
- Question: "Which PPE is mandatory?" (5 points)
- Correct: [Helmet, Gloves]
- Candidate selects: [Helmet, Gloves] → 5 points ✓
- Candidate selects: [Helmet] → 0 points ✗
- Candidate selects: [Helmet, Gloves, Sandals] → 0 points ✗

## Next Steps

1. **Frontend Builder** - Create admin UI to build questionnaires
2. **Form Integration** - Add questionnaire to candidate application form
3. **Analytics Dashboard** - Visualize questionnaire performance
4. **Testing** - Create sample questionnaires and test submissions
5. **Documentation** - Add user guide for admins

## Support

See `docs/QUESTIONNAIRE_SYSTEM.md` for complete API documentation and examples.

For questions, contact the development team.
