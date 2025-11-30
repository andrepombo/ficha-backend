# Export Reports Feature - User Guide

## Overview

The export reports feature allows you to download candidate and analytics data in **PDF** and **Excel** formats. This is useful for:
- Sharing reports with stakeholders
- Offline analysis
- Record keeping and compliance
- Creating presentations

## Features

### 1. Dashboard Export (Candidates Report)
Export the current filtered view of candidates from the Dashboard page.

**What's Included:**
- **Statistics Summary**: Total candidates by status with percentages
- **Candidate List**: Detailed table with name, email, position, status, and application date
- **Demographics Analysis** (Excel only): Gender and disability distribution
- **Applied Filters**: Shows which filters were active when exporting

**How to Use:**
1. Navigate to the Dashboard page
2. Apply any desired filters (status, position, month, year, search)
3. Click the **PDF** or **Excel** button in the header
4. The file will automatically download

**File Naming:**
- PDF: `candidatos_YYYY-MM-DD.pdf`
- Excel: `candidatos_YYYY-MM-DD.xlsx`

### 2. Analytics Export
Export monthly analytics data with charts and statistics.

**What's Included:**
- **Overall Statistics**: Total candidates by status
- **Monthly Breakdown**: Applications, accepted, and rejected per month
- **Acceptance Rates**: Calculated for each month
- **Year Filtering**: Export data for a specific year or all years

**How to Use:**
1. Navigate to the Analytics page
2. Select the desired year from the dropdown
3. Click the **PDF** or **Excel** button
4. The file will automatically download

**File Naming:**
- PDF: `analytics_YYYY_YYYY-MM-DD.pdf`
- Excel: `analytics_YYYY_YYYY-MM-DD.xlsx`

## Export Formats

### PDF Reports
- **Professional Layout**: Clean, branded design with purple/indigo theme
- **Tables**: Well-formatted tables with alternating row colors
- **Headers**: Clear section headers and titles
- **Metadata**: Generation date and applied filters
- **Portable**: Can be easily shared via email or printed

### Excel Reports
- **Multiple Sheets**: Organized data across multiple worksheets
  - Statistics sheet
  - Candidates list
  - Demographics (Dashboard export)
  - Monthly data (Analytics export)
- **Formatted Headers**: Bold, colored headers for easy reading
- **Editable**: Can be further analyzed or modified in Excel
- **Charts Ready**: Data is structured for creating charts

## Excel Sheet Structure

### Dashboard Export Sheets:
1. **Estatísticas**: Overall statistics with counts and percentages
2. **Candidatos**: Full candidate list with all details
3. **Demografia**: Gender and disability distribution

### Analytics Export Sheets:
1. **Resumo**: Summary statistics for the selected period
2. **Dados Mensais**: Month-by-month breakdown with acceptance rates

## Technical Details

### Backend Implementation
- **PDF Generation**: ReportLab library (Python)
- **Excel Generation**: openpyxl library (Python)
- **Endpoints**:
  - `GET /api/candidates/export_pdf/` - Dashboard PDF export
  - `GET /api/candidates/export_excel/` - Dashboard Excel export
  - `GET /api/candidates/export_analytics_pdf/` - Analytics PDF export
  - `GET /api/candidates/export_analytics_excel/` - Analytics Excel export

### Frontend Implementation
- Export buttons integrated into Dashboard and Analytics pages
- Automatic file download using Blob API
- Error handling with user-friendly messages
- Respects current filter state

## Filter Support

The Dashboard export respects the following filters:
- **Status**: Filter by candidate status (pending, reviewing, etc.)
- **Position**: Filter by job position
- **Month**: Filter by application month
- **Year**: Filter by application year
- **Search**: Text search across name, email, and position

The Analytics export respects:
- **Year**: Filter by specific year or export all years

## Troubleshooting

### Export Button Not Working
- Check your internet connection
- Ensure you're logged in
- Try refreshing the page
- Check browser console for errors

### File Not Downloading
- Check browser download settings
- Ensure pop-ups are not blocked
- Try a different browser
- Check available disk space

### Empty or Incomplete Reports
- Verify that data exists for the selected filters
- Try removing some filters to broaden the results
- Check that candidates have the required data fields

### PDF Formatting Issues
- PDFs are optimized for A4 paper size
- Large datasets may span multiple pages
- Use landscape orientation for printing if needed

### Excel File Won't Open
- Ensure you have Excel or a compatible spreadsheet application
- Try opening with Google Sheets or LibreOffice Calc
- Check that the file downloaded completely

## Best Practices

1. **Regular Exports**: Export reports regularly for record-keeping
2. **Descriptive Filters**: Use specific filters to create focused reports
3. **File Organization**: Organize exported files by date and purpose
4. **Data Validation**: Review exported data for accuracy
5. **Backup**: Keep important reports backed up

## Security & Privacy

- Exports contain sensitive candidate information
- Only authenticated users can export reports
- Exports respect user permissions
- Store exported files securely
- Follow data protection regulations (LGPD, GDPR)

## Future Enhancements

Potential improvements for future versions:
- Custom date ranges
- Interview reports export
- Scheduled automatic exports
- Email delivery of reports
- Custom report templates
- Chart/graph inclusion in PDFs

## Support

If you encounter any issues with the export feature:
1. Check this documentation
2. Review the troubleshooting section
3. Contact your system administrator
4. Check application logs for detailed error messages

---

**Last Updated**: October 2025  
**Version**: 1.0
