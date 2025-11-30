"""
Export service for generating PDF and Excel reports.
"""
from io import BytesIO
from datetime import datetime
from django.db.models import Count, Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .models import Candidate, Interview
import logging

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting reports to PDF and Excel formats."""
    
    # Color scheme
    PRIMARY_COLOR = colors.HexColor('#7c3aed')  # Purple
    HEADER_COLOR = colors.HexColor('#f3e8ff')   # Light purple
    ACCENT_COLOR = colors.HexColor('#10b981')   # Green
    
    @staticmethod
    def generate_candidates_pdf(candidates, filters=None):
        """
        Generate a PDF report of candidates.
        
        Args:
            candidates: QuerySet or list of Candidate objects
            filters: Dictionary of applied filters (optional)
            
        Returns:
            BytesIO object containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=ExportService.PRIMARY_COLOR,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=ExportService.PRIMARY_COLOR,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Title
        elements.append(Paragraph("Relatório de Candidatos", title_style))
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
        
        # Filter information
        if filters:
            filter_text = ExportService._format_filters(filters)
            if filter_text:
                elements.append(Paragraph(f"<b>Filtros aplicados:</b> {filter_text}", styles['Normal']))
                elements.append(Spacer(1, 12))
        
        # Statistics
        elements.append(Paragraph("Estatísticas Gerais", heading_style))
        stats_data = ExportService._calculate_candidate_stats(candidates)
        stats_table = ExportService._create_stats_table(stats_data)
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Candidates list
        elements.append(Paragraph("Lista de Candidatos", heading_style))
        
        # Create table data
        table_data = [['Nome', 'Telefone', 'CPF', 'Status', 'Data']]
        
        for candidate in candidates:
            table_data.append([
                candidate.full_name[:30],
                candidate.phone_number if candidate.phone_number else 'N/A',
                candidate.cpf if candidate.cpf else 'N/A',
                ExportService._translate_status(candidate.status),
                candidate.applied_date.strftime('%d/%m/%Y') if candidate.applied_date else 'N/A'
            ])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), ExportService.HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), ExportService.PRIMARY_COLOR),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#faf5ff')]),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_candidates_excel(candidates, filters=None):
        """
        Generate an Excel report of candidates.
        
        Args:
            candidates: QuerySet or list of Candidate objects
            filters: Dictionary of applied filters (optional)
            
        Returns:
            BytesIO object containing the Excel file
        """
        wb = Workbook()
        
        # Statistics sheet
        ws_stats = wb.active
        ws_stats.title = "Estatísticas"
        ExportService._create_excel_stats_sheet(ws_stats, candidates, filters)
        
        # Candidates sheet
        ws_candidates = wb.create_sheet("Candidatos")
        ExportService._create_excel_candidates_sheet(ws_candidates, candidates)
        
        # Demographics sheet (if data available)
        ws_demographics = wb.create_sheet("Demografia")
        ExportService._create_excel_demographics_sheet(ws_demographics, candidates)
        
        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_analytics_pdf(candidates, year=None):
        """
        Generate a PDF analytics report with monthly data.
        
        Args:
            candidates: QuerySet or list of Candidate objects
            year: Year to filter by (optional)
            
        Returns:
            BytesIO object containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=ExportService.PRIMARY_COLOR,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=ExportService.PRIMARY_COLOR,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Title
        year_text = f" - {year}" if year else ""
        elements.append(Paragraph(f"Relatório Analítico{year_text}", title_style))
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
        
        # Overall statistics
        elements.append(Paragraph("Estatísticas Gerais", heading_style))
        stats_data = ExportService._calculate_candidate_stats(candidates)
        stats_table = ExportService._create_stats_table(stats_data)
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Monthly breakdown
        elements.append(Paragraph("Análise Mensal", heading_style))
        monthly_data = ExportService._calculate_monthly_data(candidates, year)
        monthly_table = ExportService._create_monthly_table(monthly_data)
        elements.append(monthly_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_analytics_excel(candidates, year=None):
        """
        Generate an Excel analytics report with monthly data.
        
        Args:
            candidates: QuerySet or list of Candidate objects
            year: Year to filter by (optional)
            
        Returns:
            BytesIO object containing the Excel file
        """
        wb = Workbook()
        
        # Summary sheet
        ws_summary = wb.active
        ws_summary.title = "Resumo"
        ExportService._create_excel_analytics_summary(ws_summary, candidates, year)
        
        # Monthly data sheet
        ws_monthly = wb.create_sheet("Dados Mensais")
        ExportService._create_excel_monthly_sheet(ws_monthly, candidates, year)
        
        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    # Helper methods
    
    @staticmethod
    def _format_filters(filters):
        """Format filters dictionary into readable text."""
        parts = []
        
        if filters.get('status') and filters['status'] != 'all':
            parts.append(f"Status: {ExportService._translate_status(filters['status'])}")
        
        if filters.get('position') and filters['position'] != 'all':
            parts.append(f"Cargo: {filters['position']}")
        
        if filters.get('month') and filters['month'] != 'all':
            month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                          'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            month_idx = int(filters['month']) - 1
            parts.append(f"Mês: {month_names[month_idx]}")
        
        if filters.get('year') and filters['year'] != 'all':
            parts.append(f"Ano: {filters['year']}")
        
        if filters.get('search'):
            parts.append(f"Busca: {filters['search']}")
        
        return ', '.join(parts) if parts else 'Nenhum'
    
    @staticmethod
    def _translate_status(status):
        """Translate status to Portuguese."""
        translations = {
            'pending': 'Pendente',
            'reviewing': 'Em Análise',
            'shortlisted': 'Pré-selecionado',
            'interviewed': 'Entrevistado',
            'accepted': 'Aceito',
            'rejected': 'Rejeitado',
        }
        return translations.get(status, status)
    
    @staticmethod
    def _calculate_candidate_stats(candidates):
        """Calculate statistics from candidates."""
        total = len(candidates)
        
        stats = {
            'total': total,
            'pending': sum(1 for c in candidates if c.status == 'pending'),
            'reviewing': sum(1 for c in candidates if c.status == 'reviewing'),
            'shortlisted': sum(1 for c in candidates if c.status == 'shortlisted'),
            'interviewed': sum(1 for c in candidates if c.status == 'interviewed'),
            'accepted': sum(1 for c in candidates if c.status == 'accepted'),
            'rejected': sum(1 for c in candidates if c.status == 'rejected'),
        }
        
        return stats
    
    @staticmethod
    def _create_stats_table(stats):
        """Create a statistics table for PDF."""
        data = [
            ['Métrica', 'Quantidade', 'Percentual'],
            ['Total de Candidatos', str(stats['total']), '100%'],
            ['Pendentes', str(stats['pending']), f"{(stats['pending']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'],
            ['Em Análise', str(stats['reviewing']), f"{(stats['reviewing']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'],
            ['Pré-selecionados', str(stats['shortlisted']), f"{(stats['shortlisted']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'],
            ['Entrevistados', str(stats['interviewed']), f"{(stats['interviewed']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'],
            ['Aceitos', str(stats['accepted']), f"{(stats['accepted']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'],
            ['Rejeitados', str(stats['rejected']), f"{(stats['rejected']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'],
        ]
        
        table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ExportService.HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), ExportService.PRIMARY_COLOR),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#faf5ff')]),
        ]))
        
        return table
    
    @staticmethod
    def _calculate_monthly_data(candidates, year=None):
        """Calculate monthly statistics."""
        month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        monthly_stats = {month: {'applications': 0, 'accepted': 0, 'rejected': 0} 
                        for month in month_names}
        
        for candidate in candidates:
            if not candidate.applied_date:
                continue
                
            date = candidate.applied_date
            
            # Filter by year if specified
            if year and date.year != int(year):
                continue
            
            month = month_names[date.month - 1]
            monthly_stats[month]['applications'] += 1
            
            if candidate.status == 'accepted':
                monthly_stats[month]['accepted'] += 1
            elif candidate.status == 'rejected':
                monthly_stats[month]['rejected'] += 1
        
        return monthly_stats
    
    @staticmethod
    def _create_monthly_table(monthly_data):
        """Create monthly data table for PDF."""
        data = [['Mês', 'Total', 'Aceitos', 'Rejeitados', 'Taxa de Aceitação']]
        
        for month, stats in monthly_data.items():
            acceptance_rate = (stats['accepted'] / stats['applications'] * 100) if stats['applications'] > 0 else 0
            data.append([
                month,
                str(stats['applications']),
                str(stats['accepted']),
                str(stats['rejected']),
                f"{acceptance_rate:.1f}%"
            ])
        
        table = Table(data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ExportService.HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), ExportService.PRIMARY_COLOR),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#faf5ff')]),
        ]))
        
        return table
    
    @staticmethod
    def _create_excel_stats_sheet(ws, candidates, filters):
        """Create statistics sheet in Excel."""
        # Title
        ws['A1'] = 'Relatório de Candidatos'
        ws['A1'].font = Font(size=18, bold=True, color='7c3aed')
        ws.merge_cells('A1:D1')
        
        ws['A2'] = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ws['A2'].font = Font(size=10, color='666666')
        ws.merge_cells('A2:D2')
        
        # Filters
        if filters:
            filter_text = ExportService._format_filters(filters)
            ws['A3'] = f"Filtros: {filter_text}"
            ws['A3'].font = Font(size=10)
            ws.merge_cells('A3:D3')
        
        # Statistics
        stats = ExportService._calculate_candidate_stats(candidates)
        
        row = 5
        ws[f'A{row}'] = 'Estatísticas Gerais'
        ws[f'A{row}'].font = Font(size=14, bold=True, color='7c3aed')
        
        row += 2
        headers = ['Métrica', 'Quantidade', 'Percentual']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='7c3aed', end_color='7c3aed', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
        
        stats_data = [
            ('Total de Candidatos', stats['total'], '100%'),
            ('Pendentes', stats['pending'], f"{(stats['pending']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'),
            ('Em Análise', stats['reviewing'], f"{(stats['reviewing']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'),
            ('Pré-selecionados', stats['shortlisted'], f"{(stats['shortlisted']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'),
            ('Entrevistados', stats['interviewed'], f"{(stats['interviewed']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'),
            ('Aceitos', stats['accepted'], f"{(stats['accepted']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'),
            ('Rejeitados', stats['rejected'], f"{(stats['rejected']/stats['total']*100):.1f}%" if stats['total'] > 0 else '0%'),
        ]
        
        for stat_row in stats_data:
            row += 1
            for col, value in enumerate(stat_row, 1):
                cell = ws.cell(row=row, column=col, value=value)
                if col > 1:
                    cell.alignment = Alignment(horizontal='center')
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
    
    @staticmethod
    def _create_excel_candidates_sheet(ws, candidates):
        """Create candidates list sheet in Excel."""
        # Headers
        headers = ['Nome', 'Telefone', 'CPF', 'Status', 'Data de Aplicação']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='7c3aed', end_color='7c3aed', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
        
        # Data
        for row, candidate in enumerate(candidates, 2):
            ws.cell(row=row, column=1, value=candidate.full_name)
            ws.cell(row=row, column=2, value=candidate.phone_number or 'N/A')
            ws.cell(row=row, column=3, value=candidate.cpf or 'N/A')
            ws.cell(row=row, column=4, value=ExportService._translate_status(candidate.status))
            ws.cell(row=row, column=5, value=candidate.applied_date.strftime('%d/%m/%Y') if candidate.applied_date else 'N/A')
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 18
        ws.column_dimensions['E'].width = 18
    
    @staticmethod
    def _create_excel_demographics_sheet(ws, candidates):
        """Create demographics sheet in Excel."""
        ws['A1'] = 'Análise Demográfica'
        ws['A1'].font = Font(size=14, bold=True, color='7c3aed')
        ws.merge_cells('A1:C1')
        
        row = 3
        
        # Gender distribution
        ws[f'A{row}'] = 'Distribuição por Gênero'
        ws[f'A{row}'].font = Font(bold=True)
        row += 1
        
        gender_counts = {}
        for candidate in candidates:
            gender = candidate.gender or 'Não informado'
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        for gender, count in gender_counts.items():
            ws.cell(row=row, column=1, value=gender)
            ws.cell(row=row, column=2, value=count)
            row += 1
        
        row += 2
        
        # Disability distribution
        ws[f'A{row}'] = 'Distribuição por Deficiência (PCD)'
        ws[f'A{row}'].font = Font(bold=True)
        row += 1
        
        disability_counts = {}
        for candidate in candidates:
            disability = candidate.disability or 'Não informado'
            disability_counts[disability] = disability_counts.get(disability, 0) + 1
        
        for disability, count in disability_counts.items():
            ws.cell(row=row, column=1, value=disability)
            ws.cell(row=row, column=2, value=count)
            row += 1
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 15
    
    @staticmethod
    def _create_excel_analytics_summary(ws, candidates, year):
        """Create analytics summary sheet in Excel."""
        # Title
        year_text = f" - {year}" if year else ""
        ws['A1'] = f'Relatório Analítico{year_text}'
        ws['A1'].font = Font(size=18, bold=True, color='7c3aed')
        ws.merge_cells('A1:D1')
        
        ws['A2'] = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ws['A2'].font = Font(size=10, color='666666')
        ws.merge_cells('A2:D2')
        
        # Statistics
        stats = ExportService._calculate_candidate_stats(candidates)
        
        row = 4
        ws[f'A{row}'] = 'Estatísticas Gerais'
        ws[f'A{row}'].font = Font(size=14, bold=True, color='7c3aed')
        
        row += 2
        stats_data = [
            ('Total de Candidatos', stats['total']),
            ('Pendentes', stats['pending']),
            ('Em Análise', stats['reviewing']),
            ('Pré-selecionados', stats['shortlisted']),
            ('Entrevistados', stats['interviewed']),
            ('Aceitos', stats['accepted']),
            ('Rejeitados', stats['rejected']),
        ]
        
        for label, value in stats_data:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            row += 1
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 15
    
    @staticmethod
    def _create_excel_monthly_sheet(ws, candidates, year):
        """Create monthly data sheet in Excel."""
        # Headers
        headers = ['Mês', 'Total', 'Aceitos', 'Rejeitados', 'Taxa de Aceitação']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='7c3aed', end_color='7c3aed', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
        
        # Data
        monthly_data = ExportService._calculate_monthly_data(candidates, year)
        
        row = 2
        for month, stats in monthly_data.items():
            acceptance_rate = (stats['accepted'] / stats['applications'] * 100) if stats['applications'] > 0 else 0
            
            ws.cell(row=row, column=1, value=month)
            ws.cell(row=row, column=2, value=stats['applications'])
            ws.cell(row=row, column=3, value=stats['accepted'])
            ws.cell(row=row, column=4, value=stats['rejected'])
            ws.cell(row=row, column=5, value=f"{acceptance_rate:.1f}%")
            
            row += 1
        
        # Adjust column widths
        for col in range(1, 6):
            ws.column_dimensions[get_column_letter(col)].width = 18


# Create a singleton instance
export_service = ExportService()
