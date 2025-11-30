# URL Structure Changes

## New URL Structure (Production)

The application has been reorganized for a cleaner URL structure:

### Public Pages (Main Website)
- **`/`** - Main application form (was `/candidate/apply/`)
- **`/success/`** - Application success page
- **`/login/`** - Candidate login
- **`/status/`** - Check application status
- **`/logout/`** - Candidate logout

### Admin Dashboard (Private)
- **`/painel`** - React admin dashboard (requires authentication)

### Backend Admin
- **`/admin/`** - Django admin panel

### API Endpoints
- **`/api/`** - REST API endpoints
- **`/api/token/`** - JWT authentication
- **`/api/token/refresh/`** - JWT token refresh
- **`/api/user/`** - Current user info

### Static Files
- **`/static/`** - Django static files
- **`/media/`** - User uploaded files

## Migration Notes

### Old URLs → New URLs
- `http://yourdomain.com.br/candidate/apply/` → `http://yourdomain.com.br/`
- `http://yourdomain.com.br/candidate/success/` → `http://yourdomain.com.br/success/`
- `http://yourdomain.com.br/candidate/login/` → `http://yourdomain.com.br/login/`
- `http://yourdomain.com.br/candidate/status/` → `http://yourdomain.com.br/status/`
- `http://yourdomain.com.br/candidate/logout/` → `http://yourdomain.com.br/logout/`

### What Changed

1. **Removed `/candidate/` prefix** - The main application form is now at the root
2. **Cleaner URLs** - Simpler and more professional URL structure
3. **Better SEO** - Root domain is better for search engines

### Development vs Production

**Development (Local):**
- Backend: `http://0.0.0.0:8000/`
- Frontend Dashboard: `http://0.0.0.0:5173/`

**Production (EC2):**
- Main Form: `https://yourdomain.com.br/`
- Admin Dashboard: `https://yourdomain.com.br/painel`
- Django Admin: `https://yourdomain.com.br/admin/`

## Testing Locally

After making these changes, test locally:

```bash
# Start backend
cd ficha-backend
python manage.py runserver

# Visit in browser
http://0.0.0.0:8000/  # Should show application form
```

## Deployment

The Nginx configuration has been updated to handle the new URL structure. After deploying:

1. The root domain (`yourdomain.com.br/`) will show the application form
2. The admin dashboard will be at `/painel`
3. All other pages will work with their new simplified URLs

No additional configuration needed - just deploy as normal!
