# Candidate Application Module

This Django app manages job candidate applications for the Ficha Backend project.

## Features

### For Candidates
- **Application Form**: Comprehensive form for candidates to submit their job applications
- **File Upload**: Support for resume/CV uploads (PDF, DOC, DOCX)
- **Validation**: Form validation for email, phone numbers, and required fields
- **Success Confirmation**: User-friendly success page after submission

### For Employers (Admin)
- **Admin Interface**: Full-featured Django admin interface for reviewing applications
- **Filtering & Search**: Filter by status, position, education level, and search by name, email, skills
- **Bulk Actions**: Mark multiple candidates as reviewing, interviewed, accepted, or rejected
- **Status Management**: Track application status (Pending, Under Review, Interviewed, Accepted, Rejected)
- **Internal Notes**: Add private notes for each candidate

## Model Fields

The `Candidate` model includes:

### Personal Information
- First Name, Last Name
- Email (unique)
- Phone Number (validated format)
- Date of Birth

### Address
- Street Address, City, State, Postal Code, Country

### Professional Information
- Position Applied For
- Current Company & Position
- Years of Experience

### Education
- Highest Education Level
- Field of Study

### Additional Information
- LinkedIn Profile URL
- Portfolio/Website URL
- Resume/CV Upload
- Cover Letter

### Skills & Qualifications
- Skills (comma-separated)
- Certifications

### Availability
- Available Start Date
- Expected Salary

### Application Status
- Status (Pending, Reviewing, Interviewed, Accepted, Rejected)
- Applied Date (auto-generated)
- Last Updated (auto-updated)
- Internal Notes (employer only)

## URLs

- `/candidate/apply/` - Application form for candidates
- `/candidate/success/` - Success page after submission
- `/admin/` - Admin interface for employers

## Usage

### For Candidates
1. Navigate to `/candidate/apply/`
2. Fill out the application form
3. Upload resume (optional)
4. Submit the application
5. Receive confirmation on success page

### For Employers
1. Log in to Django admin at `/admin/`
2. Navigate to "Candidate Management" > "Candidates"
3. View all applications with filtering and search
4. Click on a candidate to view full details
5. Update status and add internal notes
6. Use bulk actions to manage multiple candidates

## Admin Features

### List View
- Displays: Full Name, Email, Phone, Position, Status, Experience, Applied Date
- Filters: Status, Position, Education Level, Applied Date, Years of Experience
- Search: Name, Email, Phone, Position, Skills

### Detail View
Organized into collapsible sections:
- Personal Information
- Address (collapsible)
- Professional Information
- Education
- Additional Information
- Skills & Qualifications
- Availability
- Application Status
- Metadata (collapsible)

### Bulk Actions
- Mark as Under Review
- Mark as Interviewed
- Mark as Accepted
- Mark as Rejected

## File Uploads

Resumes are stored in the `media/resumes/` directory. Make sure to:
1. Configure `MEDIA_ROOT` and `MEDIA_URL` in settings
2. Serve media files during development (already configured)
3. Configure proper file storage for production

## Future Enhancements

Potential improvements:
- Email notifications to candidates on status changes
- API endpoints for programmatic access
- Advanced filtering and analytics dashboard
- Interview scheduling system
- Candidate portal for tracking application status
