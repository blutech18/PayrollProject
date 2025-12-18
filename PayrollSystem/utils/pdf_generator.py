"""
PDF Generation utility for Proly Payroll Management System.
Uses reportlab for PDF generation.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import List, Dict, Optional
import os
import logging


logger = logging.getLogger(__name__)


class PDFGenerator:
    """Base class for PDF generation with common utilities."""
    
    def __init__(self, filename: str, title: str = "Report"):
        self.filename = filename
        self.title = title
        self.doc = SimpleDocTemplate(filename, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.elements = []
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#333333'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#444444'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
        ))
    
    def add_header(self, company_name: str, address: str, contact: str):
        """Add company header to PDF."""
        # Company info
        header_data = [
            [Paragraph(f"<b>{company_name}</b>", self.styles['CustomTitle'])],
            [Paragraph(address, self.styles['CustomBody'])],
            [Paragraph(contact, self.styles['CustomBody'])],
        ]
        
        header_table = Table(header_data, colWidths=[6*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.elements.append(header_table)
        self.elements.append(Spacer(1, 20))
    
    def add_title(self, title: str):
        """Add document title."""
        self.elements.append(Paragraph(title, self.styles['CustomTitle']))
        self.elements.append(Spacer(1, 10))
    
    def add_text(self, text: str, style='CustomBody'):
        """Add text paragraph."""
        self.elements.append(Paragraph(text, self.styles[style]))
        self.elements.append(Spacer(1, 10))
    
    def add_table(self, data: List[List], col_widths: Optional[List] = None, 
                  with_header: bool = True, header_color: str = '#F0D095'):
        """Add table to PDF."""
        if not data:
            return
        
        table = Table(data, colWidths=col_widths)
        
        style_commands = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]
        
        if with_header:
            style_commands.extend([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
            ])
        
        table.setStyle(TableStyle(style_commands))
        self.elements.append(table)
        self.elements.append(Spacer(1, 15))
    
    def add_spacer(self, height: float):
        """Add vertical spacer."""
        self.elements.append(Spacer(1, height * inch))
    
    def add_footer_info(self, footer_text: str):
        """Add footer information."""
        self.elements.append(Spacer(1, 20))
        self.elements.append(Paragraph(f"<i>{footer_text}</i>", self.styles['CustomBody']))
    
    def build(self):
        """Build and save the PDF."""
        self.doc.build(self.elements)


class PayslipPDFGenerator:
    """Specialized PDF generator for payslips."""
    
    @staticmethod
    def generate(filename: str, company_data: Dict, employee_data: Dict, 
                 payslip_data: Dict, period: str) -> bool:
        """Generate a payslip PDF."""
        try:
            pdf = PDFGenerator(filename, "Payslip")
            
            # Add company header
            pdf.add_header(
                company_data.get('name', 'COMPANY NAME'),
                company_data.get('address', 'Address'),
                company_data.get('contact', 'Contact Info')
            )
            
            # Title
            pdf.add_title("P A Y S L I P")
            
            # Period
            pdf.add_text(f"<b>Period Covered:</b> {period}")
            pdf.add_spacer(0.2)
            
            # Employee Info
            employee_info = [
                ['Employee Name:', employee_data.get('name', 'N/A')],
                ['Employee Code:', employee_data.get('employee_code', 'N/A')],
                ['Position:', employee_data.get('position', 'N/A')],
            ]
            pdf.add_table(employee_info, col_widths=[2*inch, 4*inch], with_header=False)
            
            # Earnings
            pdf.add_text("<b>EARNINGS</b>", style='CustomHeading')
            earnings_data = [['Type', 'Amount']]
            for key, value in payslip_data.get('earnings', {}).items():
                if value > 0:
                    earnings_data.append([key, f"PHP {value:,.2f}"])
            pdf.add_table(earnings_data, col_widths=[3*inch, 2*inch])
            
            # Deductions
            pdf.add_text("<b>DEDUCTIONS</b>", style='CustomHeading')
            deductions_data = [['Type', 'Amount']]
            for key, value in payslip_data.get('deductions', {}).items():
                if value > 0:
                    deductions_data.append([key, f"PHP {value:,.2f}"])
            pdf.add_table(deductions_data, col_widths=[3*inch, 2*inch])
            
            # Summary
            summary_data = [
                ['Gross Pay:', f"PHP {payslip_data.get('gross_pay', 0):,.2f}"],
                ['Total Deductions:', f"PHP {payslip_data.get('total_deductions', 0):,.2f}"],
                ['Net Pay:', f"<b>PHP {payslip_data.get('net_pay', 0):,.2f}</b>"],
            ]
            pdf.add_table(summary_data, col_widths=[3*inch, 2*inch], with_header=False)
            
            # Footer
            pdf.add_footer_info(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
            
            pdf.build()
            return True
        except Exception as e:
            logger.exception("Error generating payslip PDF: %s", e)
            return False


def generate_employee_list_pdf(filename: str, employees: List[Dict], department: str = "All Departments") -> bool:
    """Generate employee list PDF."""
    try:
        pdf = PDFGenerator(filename, "Employee List")
        
        # Get company settings
        try:
            from models.company_model import get_company_settings
            company_settings = get_company_settings()
            if company_settings:
                pdf.add_header(
                    company_settings.get('company_name', 'COMPANY NAME'),
                    f"{company_settings.get('address_line1', '')}, {company_settings.get('address_line2', '')}",
                    f"{company_settings.get('phone', '')} | {company_settings.get('email', '')}"
                )
        except:
            pass
        
        # Title
        pdf.add_title(f"Employee List - {department}")
        pdf.add_text(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        pdf.add_spacer(0.3)
        
        # Prepare table data
        headers = ['Employee Code', 'Full Name', 'Position', 'Department', 'Date Hired', 'Base Salary']
        table_data = [headers]
        
        for emp in employees:
            table_data.append([
                emp.get('employee_code', 'N/A'),
                f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip(),
                emp.get('position', 'N/A'),
                emp.get('department_name', 'N/A'),
                str(emp.get('date_hired', 'N/A')),
                f"PHP {emp.get('base_salary', 0):,.2f}"
            ])
        
        # Add table
        pdf.add_table(table_data, col_widths=[1*inch, 2*inch, 1.5*inch, 1.5*inch, 1*inch, 1.5*inch])
        
        # Add summary
        pdf.add_text(f"<b>Total Employees:</b> {len(employees)}")
        
        # Add footer
        pdf.add_footer_info("PROLY HR System")
        
        # Build PDF
        pdf.build()
        return True
        
    except Exception as e:
        logger.exception("Error generating employee list PDF: %s", e)
        return False


def generate_payroll_report_pdf(filename: str, payroll_data: List[Dict], period_name: str) -> bool:
    """Generate payroll report PDF."""
    try:
        pdf = PDFGenerator(filename, "Payroll Report")
        
        # Get company settings
        try:
            from models.company_model import get_company_settings
            company_settings = get_company_settings()
            if company_settings:
                pdf.add_header(
                    company_settings.get('company_name', 'COMPANY NAME'),
                    f"{company_settings.get('address_line1', '')}, {company_settings.get('address_line2', '')}",
                    f"{company_settings.get('phone', '')} | {company_settings.get('email', '')}"
                )
        except:
            pass
        
        # Title
        pdf.add_title(f"Payroll Report - {period_name}")
        pdf.add_text(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        pdf.add_spacer(0.3)
        
        # Prepare table data
        headers = ['Employee Code', 'Employee Name', 'Gross Pay', 'Deductions', 'Net Pay', 'Status']
        table_data = [headers]
        
        total_gross = 0.0
        total_deductions = 0.0
        total_net = 0.0
        
        for entry in payroll_data:
            gross = float(entry.get('gross_pay', 0))
            deductions = float(entry.get('total_deductions', 0))
            net = float(entry.get('net_pay', 0))
            
            total_gross += gross
            total_deductions += deductions
            total_net += net
            
            table_data.append([
                entry.get('employee_code', 'N/A'),
                f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip(),
                f"PHP {gross:,.2f}",
                f"PHP {deductions:,.2f}",
                f"PHP {net:,.2f}",
                entry.get('status', 'N/A')
            ])
        
        # Add table
        pdf.add_table(table_data, col_widths=[1*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
        
        # Add summary
        summary_data = [
            ['Total Employees:', str(len(payroll_data))],
            ['Total Gross Pay:', f"PHP {total_gross:,.2f}"],
            ['Total Deductions:', f"PHP {total_deductions:,.2f}"],
            ['Total Net Pay:', f"<b>PHP {total_net:,.2f}</b>"],
        ]
        pdf.add_table(summary_data, col_widths=[2*inch, 2*inch], with_header=False)
        
        # Add footer
        pdf.add_footer_info("PROLY Payroll System")
        
        # Build PDF
        pdf.build()
        return True
        
    except Exception as e:
        logger.exception("Error generating payroll report PDF: %s", e)
        return False


def generate_audit_log_pdf(filename: str, audit_logs: List[Dict], filters: Optional[Dict] = None) -> bool:
    """Generate audit log PDF."""
    try:
        pdf = PDFGenerator(filename, "Audit Log Report")
        
        # Get company settings
        try:
            from models.company_model import get_company_settings
            company_settings = get_company_settings()
            if company_settings:
                pdf.add_header(
                    company_settings.get('company_name', 'COMPANY NAME'),
                    f"{company_settings.get('address_line1', '')}, {company_settings.get('address_line2', '')}",
                    f"{company_settings.get('phone', '')} | {company_settings.get('email', '')}"
                )
        except:
            pass
        
        # Title
        pdf.add_title("Audit Log Report")
        
        # Add filters if any
        if filters:
            filter_text = "<b>Filters Applied:</b> "
            filter_parts = []
            if filters.get('user') and filters['user'] != 'ALL':
                filter_parts.append(f"User: {filters['user']}")
            if filters.get('action') and filters['action'] != 'ALL':
                filter_parts.append(f"Action: {filters['action']}")
            if filters.get('date'):
                filter_parts.append(f"Date: {filters['date']}")
            
            if filter_parts:
                filter_text += ", ".join(filter_parts)
                pdf.add_text(filter_text)
        
        # Add generation info
        pdf.add_text(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        pdf.add_spacer(0.3)
        
        # Prepare table data
        headers = ['Date/Time', 'User', 'Action', 'Details']
        table_data = [headers]
        
        for log in audit_logs:
            created_at = log.get('created_at', '')
            if hasattr(created_at, 'strftime'):
                created_at = created_at.strftime('%Y-%m-%d %H:%M')
            
            table_data.append([
                str(created_at),
                log.get('user', 'N/A'),
                log.get('action', ''),
                log.get('details', '')[:50] + '...' if len(log.get('details', '')) > 50 else log.get('details', '')
            ])
        
        # Add table
        pdf.add_table(table_data, col_widths=[1.3*inch, 1*inch, 1*inch, 3.2*inch])
        
        # Add summary
        pdf.add_text(f"<b>Total Log Entries:</b> {len(audit_logs)}")
        
        # Add footer
        pdf.add_footer_info("PROLY System Administrator")
        
        # Build PDF
        pdf.build()
        return True
        
    except Exception as e:
        logger.exception("Error generating audit log PDF: %s", e)
        return False


def generate_hr_report_pdf(filename: str, report_type: str, report_data: List[Dict], 
                          company_name: str, department: str, start_date, end_date) -> bool:
    """Generate HR report PDF (Attendance, Payroll, or Performance)."""
    try:
        pdf = PDFGenerator(filename, f"{report_type} Report")
        
        # Add company header
        pdf.add_header(company_name, "", "")
        
        # Title
        pdf.add_title(f"{report_type} Report")
        pdf.add_text(f"Department: {department}")
        pdf.add_text(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        pdf.add_text(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        pdf.add_spacer(0.3)
        
        # Prepare table data based on report type
        if report_type == "Attendance":
            headers = ["Employee Code", "Name", "Department", "Date", "Time In", "Time Out", "Hours", "Status"]
            table_data = [headers]
            
            for record in report_data:
                att_date = record.get('attendance_date')
                if isinstance(att_date, str):
                    from datetime import datetime as dt
                    try:
                        att_date = dt.strptime(att_date, '%Y-%m-%d').date()
                    except:
                        pass
                
                table_data.append([
                    record.get('employee_code', 'N/A'),
                    f"{record.get('first_name', '')} {record.get('last_name', '')}".strip(),
                    record.get('department_name', 'N/A'),
                    str(att_date) if att_date else 'N/A',
                    str(record.get('time_in', 'N/A')),
                    str(record.get('time_out', 'N/A')),
                    f"{float(record.get('hours_worked', 0)):.2f}",
                    record.get('status', 'N/A')
                ])
            
            col_widths = [1*inch, 2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1*inch]
            
        elif report_type == "Payroll":
            headers = ["Employee Code", "Name", "Department", "Period", "Gross Pay", "Deductions", "Net Pay", "Status"]
            table_data = [headers]
            
            total_gross = 0.0
            total_deductions = 0.0
            total_net = 0.0
            
            for record in report_data:
                gross = float(record.get('gross_pay', 0))
                deductions = float(record.get('total_deductions', 0))
                net = float(record.get('net_pay', 0))
                
                total_gross += gross
                total_deductions += deductions
                total_net += net
                
                table_data.append([
                    record.get('employee_code', 'N/A'),
                    f"{record.get('first_name', '')} {record.get('last_name', '')}".strip(),
                    record.get('department_name', 'N/A'),
                    record.get('period_name', 'N/A'),
                    f"PHP {gross:,.2f}",
                    f"PHP {deductions:,.2f}",
                    f"PHP {net:,.2f}",
                    record.get('payroll_status', 'N/A')
                ])
            
            col_widths = [1*inch, 2*inch, 1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch]
            
            # Add summary
            pdf.add_spacer(0.2)
            summary_data = [
                ['Total Records:', str(len(report_data))],
                ['Total Gross Pay:', f"PHP {total_gross:,.2f}"],
                ['Total Deductions:', f"PHP {total_deductions:,.2f}"],
                ['Total Net Pay:', f"<b>PHP {total_net:,.2f}</b>"],
            ]
            pdf.add_table(summary_data, col_widths=[2*inch, 2*inch], with_header=False)
            
        elif report_type == "Performance":
            headers = ["Employee Code", "Name", "Department", "Periods", "Total Gross", "Avg Gross", "Overtime", "Incentives", "Late Count", "Undertime Count"]
            table_data = [headers]
            
            for record in report_data:
                table_data.append([
                    record.get('employee_code', 'N/A'),
                    f"{record.get('first_name', '')} {record.get('last_name', '')}".strip(),
                    record.get('department_name', 'N/A'),
                    str(record.get('payroll_periods_count', 0)),
                    f"PHP {float(record.get('total_gross_pay', 0)):,.2f}",
                    f"PHP {float(record.get('avg_gross_pay', 0)):,.2f}",
                    f"PHP {float(record.get('total_overtime', 0)):,.2f}",
                    f"PHP {float(record.get('total_incentives', 0)):,.2f}",
                    str(record.get('late_occurrences', 0)),
                    str(record.get('undertime_occurrences', 0))
                ])
            
            col_widths = [1*inch, 2*inch, 1.5*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch, 0.8*inch, 1*inch]
        else:
            return False
        
        # Add table
        pdf.add_table(table_data, col_widths=col_widths)
        
        # Add summary
        pdf.add_text(f"<b>Total Records:</b> {len(report_data)}")
        
        # Add footer
        pdf.add_footer_info("PROLY HR System")
        
        # Build PDF
        pdf.build()
        return True
        
    except Exception as e:
        logger.exception("Error generating HR report PDF: %s", e)
        return False
