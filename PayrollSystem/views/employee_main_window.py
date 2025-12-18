from __future__ import annotations

from typing import Optional
import logging

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# --- STYLE CONSTANTS ---
STYLE_LABEL_INFO = "font-size:14px; color:#555;"
STYLE_COLOR_555 = "color:#555;"
STYLE_BOLD_RIGHT_ALIGN = "font-weight:bold; qproperty-alignment: AlignRight;"
STYLE_RIGHT_ALIGN = "qproperty-alignment: AlignRight;"
STYLE_SIGNATURE_LABEL = "font-weight:bold; font-size:11px; qproperty-alignment:AlignCenter;"

# --- GLOBAL STYLES ---
STYLESHEET = """
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        color: #4A4A4A;
    }
    
    /* BACKGROUNDS */
    QWidget#MainContentArea { background-color: #F2EBE9; }
    QWidget#Sidebar, QWidget#TopBar { background-color: #F5E6D3; }

    /* CARDS */
    QFrame.Card {
        background-color: #FDF8F2;
        border-radius: 15px;
        border: 1px solid #EBE0D6;
    }

    /* INPUTS */
    QLineEdit {
        background-color: #EFEBE6; 
        border: 1px solid #D6CDC6;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 13px;
        color: #555;
    }

    /* BUTTONS */
    QPushButton.NavBtn {
        text-align: left;
        padding: 15px 25px;
        border: none;
        background-color: transparent;
        font-weight: 600;
        font-size: 14px;
        color: #5A5A5A;
        border-left: 4px solid transparent;
    }
    QPushButton.NavBtn:checked {
        background-color: #E6D6C4;
        color: #333333;
        border-left: 4px solid #333;
    }
    
    QPushButton.PrimaryBtn {
        background-color: #F0D095;
        border: 1px solid #C0A065;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 12px;
    }
    QPushButton.PrimaryBtn:hover { background-color: #F5DCA0; }
    
    /* Table Headers */
    QHeaderView::section {
        background-color: #C0A065;
        padding: 10px;
        border: none;
        font-weight: bold;
        color: #FFFFFF;
        font-size: 13px;
    }
    
    /* Dialogs and MessageBoxes */
    QDialog {
        background-color: #FFFFFF;
    }
    QDialog QLabel {
        color: #333333;
        background-color: transparent;
    }
    QMessageBox {
        background-color: #FFFFFF;
    }
    QMessageBox QLabel {
        color: #333333;
        background-color: transparent;
    }
    
    /* Top Bar Search */
    QLineEdit#SearchInput {
        background-color: #FFFFFF;
        border-radius: 4px;
        border: none;
        padding-left: 10px;
        color: #888;
    }
"""


class ShadowCard(QFrame):
    """Standard card with shadow used across all views."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


logger = logging.getLogger(__name__)


class EmployeeDashboardView(QWidget):
    """Employee Dashboard matching Wireframe_page-0008.jpg."""

    def __init__(self, employee_id: Optional[int] = None):
        super().__init__()
        self.employee_id = employee_id
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        card = ShadowCard()
        card.setFixedSize(650, 450)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(50, 40, 50, 40)

        # Header Section
        cl.addWidget(QLabel("EMPLOYEE PROFILE", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        cl.addSpacing(20)

        # Profile Grid
        prof_layout = QHBoxLayout()

        # Info
        info_l = QVBoxLayout()
        info_l.setSpacing(10)
        self.name_label = QLabel("Name :", styleSheet=STYLE_LABEL_INFO)
        self.position_label = QLabel("Position :", styleSheet=STYLE_LABEL_INFO)
        self.department_label = QLabel("Department :", styleSheet=STYLE_LABEL_INFO)
        self.employee_id_label = QLabel("Employee ID :", styleSheet=STYLE_LABEL_INFO)
        info_l.addWidget(self.name_label)
        info_l.addWidget(self.position_label)
        info_l.addWidget(self.department_label)
        info_l.addWidget(self.employee_id_label)
        prof_layout.addLayout(info_l)

        prof_layout.addStretch()

        # Photo Placeholder
        self.photo_placeholder = QLabel()
        self.photo_placeholder.setFixedSize(120, 120)
        self.photo_placeholder.setStyleSheet("background-color: #EEE; border: 1px solid #CCC; border-radius: 4px;")
        prof_layout.addWidget(self.photo_placeholder)

        cl.addLayout(prof_layout)
        cl.addSpacing(30)

        # Latest Payslip Section
        cl.addWidget(QLabel("LATEST PAYSLIP", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        cl.addSpacing(10)
        self.period_label = QLabel("Period :", styleSheet="font-size:14px; font-weight:500; color:#555;")
        self.net_pay_label = QLabel("Net Pay : PHP 0.00", styleSheet="font-size:14px; font-weight:500; color:#555;")
        cl.addWidget(self.period_label)
        cl.addWidget(self.net_pay_label)
        
        # Load employee data
        if self.employee_id:
            self._load_employee_data()

        cl.addSpacing(30)

        # Button
        self.view_detailed_payslip_btn = QPushButton("View Detailed Payslip")
        self.view_detailed_payslip_btn.setProperty("class", "PrimaryBtn")
        self.view_detailed_payslip_btn.setFixedWidth(250)
        self.view_detailed_payslip_btn.clicked.connect(self._navigate_to_payslip)

        btn_cont = QHBoxLayout()
        btn_cont.addStretch()
        btn_cont.addWidget(self.view_detailed_payslip_btn)
        btn_cont.addStretch()
        cl.addLayout(btn_cont)

        cl.addStretch()
        layout.addWidget(card)
    
    def _load_employee_data(self):
        """Load employee data from database."""
        if not self.employee_id:
            self.name_label.setText("Name : Not available")
            self.position_label.setText("Position : Not available")
            self.department_label.setText("Department : Not available")
            self.employee_id_label.setText("Employee ID : Not available")
            self.period_label.setText("Period : No payslip available")
            self.net_pay_label.setText("Net Pay : PHP 0.00")
            return
        
        try:
            from models.employee_model import get_employee_by_id, get_latest_payslip_for_employee
            from datetime import datetime
            
            employee = get_employee_by_id(self.employee_id)
            if employee:
                self.name_label.setText(f"Name : {employee.first_name} {employee.last_name}")
                self.position_label.setText(f"Position : {employee.position or 'N/A'}")
                self.department_label.setText(f"Department : {employee.department_name or 'N/A'}")
                self.employee_id_label.setText(f"Employee ID : {employee.employee_code}")
            else:
                self.name_label.setText("Name : Employee not found")
                self.position_label.setText("Position : N/A")
                self.department_label.setText("Department : N/A")
                self.employee_id_label.setText("Employee ID : N/A")
            
            # Load latest payslip
            payslip = get_latest_payslip_for_employee(self.employee_id)
            if payslip:
                start_date = payslip.get('start_date')
                end_date = payslip.get('end_date')
                
                # Handle different date formats
                try:
                    if isinstance(start_date, str):
                        # Try multiple date formats
                        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                            try:
                                start_date = datetime.strptime(start_date.split()[0], '%Y-%m-%d').date()
                                break
                            except:
                                continue
                    elif hasattr(start_date, 'date'):
                        start_date = start_date.date()
                    
                    if isinstance(end_date, str):
                        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                            try:
                                end_date = datetime.strptime(end_date.split()[0], '%Y-%m-%d').date()
                                break
                            except:
                                continue
                    elif hasattr(end_date, 'date'):
                        end_date = end_date.date()
                    
                    if start_date and end_date:
                        period_str = f"{start_date.strftime('%B')} {start_date.day}-{end_date.day}, {start_date.year}"
                        self.period_label.setText(f"Period : {period_str}")
                    else:
                        self.period_label.setText("Period : Invalid date")
                except Exception as date_error:
                    logger.exception("Error parsing dates for employee dashboard: %s", date_error)
                    self.period_label.setText("Period : Date error")
                
                net_pay = payslip.get('net_pay', 0)
                if isinstance(net_pay, (int, float)):
                    self.net_pay_label.setText(f"Net Pay : PHP {net_pay:,.2f}")
                else:
                    self.net_pay_label.setText("Net Pay : PHP 0.00")
            else:
                self.period_label.setText("Period : No payslip available")
                self.net_pay_label.setText("Net Pay : PHP 0.00")
        except Exception as e:
            logger.exception("Error loading employee data: %s", e)
            # Set default values on error
            if not hasattr(self, 'name_label') or not self.name_label.text():
                self.period_label.setText("Period : Error loading data")
                self.net_pay_label.setText("Net Pay : PHP 0.00")
    
    def set_employee_id(self, employee_id: Optional[int]):
        """Update employee ID and refresh data."""
        self.employee_id = employee_id
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh employee data from database."""
        if self.employee_id:
            self._load_employee_data()
        else:
            # Show default/empty state
            self.name_label.setText("Name : Not available")
            self.position_label.setText("Position : Not available")
            self.department_label.setText("Department : Not available")
            self.employee_id_label.setText("Employee ID : Not available")
            self.period_label.setText("Period : No payslip available")
            self.net_pay_label.setText("Net Pay : PHP 0.00")
    
    def _navigate_to_payslip(self):
        """Navigate to payslip view. This will be handled by the main window."""
        # Use the callback if available
        if hasattr(self, 'navigate_to_payslip'):
            self.navigate_to_payslip()


class EmployeePayslipView(QWidget):
    """Detailed Payslip view matching the provided template."""

    def __init__(self, employee_id: Optional[int] = None):
        super().__init__()
        self.employee_id = employee_id
        
        # Scroll Area to allow seeing the full long receipt if screen is small
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(0, 20, 0, 40)

        # THE PAPER SHEET
        paper = QFrame()
        paper.setFixedSize(700, 850)  # A4-ish ratio
        paper.setStyleSheet("background-color: white; border: 1px solid #CCC;")
        
        pl = QVBoxLayout(paper)
        pl.setContentsMargins(40, 40, 40, 40)
        pl.setSpacing(5)

        # 1. HEADER
        header = QHBoxLayout()
        
        # Logo Placeholder
        logo = QLabel()
        logo.setFixedSize(60, 60)
        logo.setStyleSheet("background-color: #EEE; color: #888; font-weight: bold; qproperty-alignment: AlignCenter;")
        try:
            pix = QPixmap("assets/images/logo.png")
            if not pix.isNull():
                logo.setPixmap(pix.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                logo.setText("LOGO")
        except Exception:
            logo.setText("LOGO")
        
        # Company Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.company_name_label = QLabel("UNICARE MEDICAL CLINIC", styleSheet="font-weight:900; font-size:16px; color:#333;")
        self.company_address_label = QLabel("Address Line 1, City Name", styleSheet="font-size:11px; color:#555;")
        self.company_contact_label = QLabel("(02) 123-4567 | unicare@gmail.com", styleSheet="font-size:11px; color:#555;")
        info_layout.addWidget(self.company_name_label)
        info_layout.addWidget(self.company_address_label)
        info_layout.addWidget(self.company_contact_label)
        
        header.addWidget(logo)
        header.addSpacing(15)
        header.addLayout(info_layout)
        header.addStretch()
        
        # Period Covered (Right aligned in header area)
        self.period_lbl = QLabel("")
        self.period_lbl.setStyleSheet("font-weight:bold; font-size:14px; color:#333;")
        
        top_row = QHBoxLayout()
        top_row.addLayout(header)
        top_row.addWidget(QLabel("Period Covered:", styleSheet="color:#666; margin-right:5px;"))
        top_row.addWidget(self.period_lbl)
        
        pl.addLayout(top_row)
        pl.addSpacing(20)

        # 2. TITLE
        title = QLabel("P A Y S L I P")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 900; color: #333; letter-spacing: 2px;")
        pl.addWidget(title)
        pl.addSpacing(20)

        # 3. EMPLOYEE DETAILS GRID
        grid_info = QGridLayout()
        grid_info.setHorizontalSpacing(20)
        grid_info.setVerticalSpacing(5)
        
        # Left Side
        grid_info.addWidget(QLabel("Name of Employee:", styleSheet=STYLE_COLOR_555), 0, 0)
        self.name_label = QLabel("", styleSheet="font-weight:bold; border-bottom:1px solid #CCC;")
        grid_info.addWidget(self.name_label, 0, 1)
        
        grid_info.addWidget(QLabel("Designation:", styleSheet=STYLE_COLOR_555), 1, 0)
        self.designation_label = QLabel("", styleSheet="font-weight:bold; border-bottom:1px solid #CCC;")
        grid_info.addWidget(self.designation_label, 1, 1)
        
        grid_info.addWidget(QLabel("Status:", styleSheet=STYLE_COLOR_555), 2, 0)
        self.status_label = QLabel("", styleSheet="border-bottom:1px solid #CCC;")
        grid_info.addWidget(self.status_label, 2, 1)
        
        # Right Side (Rates)
        grid_info.addWidget(QLabel("Rate/ day", styleSheet=STYLE_COLOR_555), 2, 2)
        self.rate_per_day_label = QLabel("0.00", styleSheet=f"font-weight:bold; border-bottom:1px solid #CCC; {STYLE_RIGHT_ALIGN}")
        grid_info.addWidget(self.rate_per_day_label, 2, 3)
        
        grid_info.addWidget(QLabel("No of days", styleSheet=STYLE_COLOR_555), 3, 2)
        self.days_label = QLabel("0.00", styleSheet=f"font-weight:bold; border-bottom:1px solid #CCC; {STYLE_RIGHT_ALIGN}")
        grid_info.addWidget(self.days_label, 3, 3)

        pl.addLayout(grid_info)
        pl.addSpacing(15)

        # 4. EARNINGS SECTION
        grid_earn = QGridLayout()
        grid_earn.setHorizontalSpacing(30)
        
        # Row 1
        grid_earn.addWidget(QLabel("Basic Pay"), 0, 0)
        self.basic_pay_label = QLabel("0.00", styleSheet=STYLE_BOLD_RIGHT_ALIGN)
        grid_earn.addWidget(self.basic_pay_label, 0, 1)
        grid_earn.addWidget(QLabel("Holiday"), 0, 2)
        self.holiday_label = QLabel("-", styleSheet=STYLE_RIGHT_ALIGN)
        grid_earn.addWidget(self.holiday_label, 0, 3)
        
        # Row 2
        grid_earn.addWidget(QLabel("Overtime Pay"), 1, 0)
        self.overtime_pay_label = QLabel("0.00", styleSheet=STYLE_BOLD_RIGHT_ALIGN)
        grid_earn.addWidget(self.overtime_pay_label, 1, 1)
        grid_earn.addWidget(QLabel("Salary Adjustment"), 1, 2)
        self.salary_adjustment_label = QLabel("0.00", styleSheet=STYLE_RIGHT_ALIGN)
        grid_earn.addWidget(self.salary_adjustment_label, 1, 3)
        
        # Row 3
        grid_earn.addWidget(QLabel("Vacation/Sickleave"), 2, 0)
        self.vacation_sickleave_label = QLabel("0.00", styleSheet=STYLE_BOLD_RIGHT_ALIGN)
        grid_earn.addWidget(self.vacation_sickleave_label, 2, 1)
        grid_earn.addWidget(QLabel("Incentive Pay"), 2, 2)
        self.incentive_pay_label = QLabel("", styleSheet=STYLE_RIGHT_ALIGN)
        grid_earn.addWidget(self.incentive_pay_label, 2, 3)

        pl.addLayout(grid_earn)
        
        # Gross Pay Row
        gross_layout = QHBoxLayout()
        gross_layout.addStretch()
        gross_layout.addWidget(QLabel("Gross Pay", styleSheet="font-weight:bold; font-size:14px;"))
        gross_layout.addSpacing(20)
        self.gross_pay_label = QLabel("0.00", styleSheet="font-weight:900; font-size:14px;")
        gross_layout.addWidget(self.gross_pay_label)
        pl.addLayout(gross_layout)
        pl.addSpacing(5)

        # 5. DEDUCTIONS HEADER (GREEN BAR)
        ded_header = QLabel("Less: Deduction")
        ded_header.setStyleSheet("background-color: #6B8E23; color: white; font-weight: bold; padding: 4px; font-style: italic;")
        pl.addWidget(ded_header)

        # 6. DEDUCTIONS GRID
        grid_ded = QGridLayout()
        grid_ded.setHorizontalSpacing(30)
        
        # Row 1
        grid_ded.addWidget(QLabel("SSS Contribution"), 0, 0)
        self.sss_contrib_label = QLabel("0.00", styleSheet=STYLE_RIGHT_ALIGN)
        grid_ded.addWidget(self.sss_contrib_label, 0, 1)
        grid_ded.addWidget(QLabel("Late"), 0, 2)
        self.late_label = QLabel("0.00", styleSheet=STYLE_RIGHT_ALIGN)
        grid_ded.addWidget(self.late_label, 0, 3)
        
        # Row 2
        grid_ded.addWidget(QLabel("TAX"), 1, 0)
        self.tax_label = QLabel("0.00", styleSheet=STYLE_RIGHT_ALIGN)
        grid_ded.addWidget(self.tax_label, 1, 1)
        grid_ded.addWidget(QLabel("Cash Advance"), 1, 2)
        self.cash_advance_label = QLabel("0.00", styleSheet=STYLE_RIGHT_ALIGN)
        grid_ded.addWidget(self.cash_advance_label, 1, 3)
        
        # Row 3
        grid_ded.addWidget(QLabel("Pag-ibig Contribution"), 2, 0)
        self.pagibig_contrib_label = QLabel("0.00", styleSheet=STYLE_RIGHT_ALIGN)
        grid_ded.addWidget(self.pagibig_contrib_label, 2, 1)
        grid_ded.addWidget(QLabel("Others"), 2, 2)
        self.others_label = QLabel("", styleSheet=STYLE_RIGHT_ALIGN)
        grid_ded.addWidget(self.others_label, 2, 3)
        
        # Row 4
        grid_ded.addWidget(QLabel("UNDER TIME"), 3, 0)
        self.undertime_label = QLabel("0.00", styleSheet=STYLE_RIGHT_ALIGN)
        grid_ded.addWidget(self.undertime_label, 3, 1)
        
        # Row 5
        grid_ded.addWidget(QLabel("PHIC"), 4, 0)
        self.phic_label = QLabel("0.00", styleSheet=STYLE_RIGHT_ALIGN)
        grid_ded.addWidget(self.phic_label, 4, 1)
        
        # Total Deduction Row (Inline)
        grid_ded.addWidget(QLabel("Total Deduction", styleSheet="font-weight:bold;"), 4, 2)
        self.total_deduction_label = QLabel("0.00", styleSheet=f"font-weight:bold; {STYLE_RIGHT_ALIGN} text-decoration: underline;")
        grid_ded.addWidget(self.total_deduction_label, 4, 3)

        pl.addLayout(grid_ded)
        pl.addSpacing(10)

        # 7. NET PAY (GREEN BAR)
        net_lbl = QLabel("Net Pay")
        net_lbl.setStyleSheet("font-weight:bold; font-size:14px; font-style: italic;")
        
        self.net_pay_label = QLabel("0.00")
        self.net_pay_label.setStyleSheet("font-weight:900; font-size:16px; qproperty-alignment: AlignRight;")
        
        net_container = QFrame()
        net_container.setStyleSheet("background-color: #6B8E23; color: white;")  # Olive Green
        nc_layout = QHBoxLayout(net_container)
        nc_layout.setContentsMargins(10, 5, 10, 5)
        nc_layout.addWidget(net_lbl)
        nc_layout.addStretch()
        nc_layout.addWidget(self.net_pay_label)
        
        pl.addWidget(net_container)
        pl.addSpacing(40)

        # 8. FOOTER (SIGNATURES)
        sig_layout = QHBoxLayout()
        sig_layout.setSpacing(20)
        
        def create_sig_block(title, name_label):
            v = QVBoxLayout()
            v.addWidget(QLabel(title + ":", styleSheet="font-style:italic; font-size:11px;"))
            v.addSpacing(20)  # Space for signature
            line = QFrame()
            line.setStyleSheet("background-color:black; max-height:1px;")
            v.addWidget(line)
            v.addWidget(name_label)
            return v

        self.received_by_name_label = QLabel("", styleSheet=STYLE_SIGNATURE_LABEL)
        
        sig_layout.addLayout(create_sig_block("Prepared by", QLabel("Ara", styleSheet=STYLE_SIGNATURE_LABEL)))
        sig_layout.addLayout(create_sig_block("Received by", self.received_by_name_label))
        sig_layout.addLayout(create_sig_block("Noted By", QLabel("", styleSheet=STYLE_SIGNATURE_LABEL)))
        
        pl.addLayout(sig_layout)
        pl.addStretch()

        layout.addWidget(paper)
        
        # Add PDF Export Button below the payslip
        export_btn_layout = QHBoxLayout()
        export_btn_layout.addStretch()
        self.export_pdf_btn = QPushButton("📄 Download as PDF")
        self.export_pdf_btn.setProperty("class", "PrimaryBtn")
        self.export_pdf_btn.setFixedWidth(200)
        self.export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0D095;
                border: 1px solid #C0A065;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: 700;
                font-size: 13px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #F5DCA0;
            }
            QPushButton:pressed {
                background-color: #E6C885;
            }
        """)
        self.export_pdf_btn.clicked.connect(self._export_to_pdf)
        export_btn_layout.addWidget(self.export_pdf_btn)
        export_btn_layout.addStretch()
        layout.addLayout(export_btn_layout)
        layout.addSpacing(20)
        
        scroll.setWidget(content_widget)
        
        # Main layout for this view
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Load payslip data after all widgets are created
        if self.employee_id:
            self._load_payslip_data()
    
    def set_employee_id(self, employee_id: Optional[int]):
        """Update employee ID and refresh data."""
        self.employee_id = employee_id
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh payslip data from database."""
        if self.employee_id:
            self._load_payslip_data()
        else:
            self._show_empty_payslip()
    
    def _load_payslip_data(self):
        """Load payslip data from database."""
        if not self.employee_id:
            self._show_empty_payslip()
            return
        
        try:
            from models.company_model import get_company_settings
            from models.employee_model import get_employee_by_id, get_latest_payslip_for_employee
            
            # Load company settings
            company_settings = get_company_settings()
            self._load_company_settings(company_settings)
            
            # Load employee data
            employee = get_employee_by_id(self.employee_id)
            if employee:
                self._load_employee_details(employee)
            else:
                # Show empty employee details if not found
                self.name_label.setText("")
                self.designation_label.setText("")
                self.status_label.setText("")
                self.rate_per_day_label.setText("0.00")
                self.days_label.setText("0.00")
                self.received_by_name_label.setText("")
            
            # Load payslip data
            payslip = get_latest_payslip_for_employee(self.employee_id)
            if payslip:
                self._load_payslip_details(payslip)
            else:
                # Show empty state if no payslip
                self._show_empty_payslip()
        except Exception as e:
            logger.exception("Error loading payslip data: %s", e)
            self._show_empty_payslip()
    
    def _show_empty_payslip(self):
        """Show empty state when no payslip is available."""
        self.name_label.setText("")
        self.designation_label.setText("")
        self.status_label.setText("")
        self.rate_per_day_label.setText("0.00")
        self.days_label.setText("0.00")
        self.period_lbl.setText("No payslip available")
        
        # Clear all earnings
        self.basic_pay_label.setText("0.00")
        self.overtime_pay_label.setText("0.00")
        self.holiday_label.setText("-")
        self.salary_adjustment_label.setText("0.00")
        self.vacation_sickleave_label.setText("0.00")
        self.incentive_pay_label.setText("")
        self.gross_pay_label.setText("0.00")
        
        # Clear all deductions
        self.sss_contrib_label.setText("0.00")
        self.phic_label.setText("0.00")
        self.pagibig_contrib_label.setText("0.00")
        self.tax_label.setText("0.00")
        self.late_label.setText("0.00")
        self.cash_advance_label.setText("0.00")
        self.others_label.setText("")
        self.undertime_label.setText("0.00")
        self.total_deduction_label.setText("0.00")
        self.net_pay_label.setText("0.00")
    
    def _load_company_settings(self, company):
        """Load and display company settings."""
        if company:
            self.company_name_label.setText(company.get('company_name', 'UNICARE MEDICAL CLINIC'))
            self.company_address_label.setText(company.get('address_line1', 'Address Line 1, City Name'))
            phone = company.get('phone', '(02) 123-4567')
            email = company.get('email', 'unicare@gmail.com')
            self.company_contact_label.setText(f"{phone} | {email}")
    
    def _load_employee_details(self, employee):
        """Load and display employee details."""
        self.name_label.setText(f"{employee.first_name.upper()} {employee.last_name.upper()}")
        self.designation_label.setText((employee.position or "N/A").upper())
        self.status_label.setText("ACTIVE" if employee.is_active else "INACTIVE")
        
        # Calculate rate per day (assuming monthly salary / 22 working days)
        if employee.base_salary > 0:
            rate_per_day = employee.base_salary / 22
            self.rate_per_day_label.setText(f"{rate_per_day:,.2f}")
        else:
            self.rate_per_day_label.setText("0.00")
        
        # Number of days (simplified - could be calculated from period)
        self.days_label.setText("13.00")
        
        # Update received by signature
        self.received_by_name_label.setText(f"{employee.first_name.upper()} {employee.last_name.upper()}")
    
    def _load_payslip_details(self, payslip):
        """Load and display payslip details."""
        from datetime import datetime
        
        start_date = payslip.get('start_date')
        end_date = payslip.get('end_date')
        
        # Handle different date formats
        try:
            if isinstance(start_date, str):
                # Try to parse date, handling different formats
                start_date = datetime.strptime(start_date.split()[0], '%Y-%m-%d').date()
            elif hasattr(start_date, 'date'):
                start_date = start_date.date()
            
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date.split()[0], '%Y-%m-%d').date()
            elif hasattr(end_date, 'date'):
                end_date = end_date.date()
            
            if start_date and end_date:
                # Period covered
                period_str = f"{start_date.strftime('%B')} {start_date.day}-{end_date.day}, {start_date.year}"
                self.period_lbl.setText(period_str)
            else:
                self.period_lbl.setText("Period: Not available")
        except Exception as date_error:
            logger.exception("Error parsing payslip dates: %s", date_error)
            self.period_lbl.setText("Period: Date error")
        
        self._load_earnings(payslip)
        self._load_deductions(payslip)
        
        # Net Pay
        net_pay = payslip.get('net_pay', 0)
        if isinstance(net_pay, (int, float)):
            self.net_pay_label.setText(f"{net_pay:,.2f}")
        else:
            self.net_pay_label.setText("0.00")
    
    def _load_earnings(self, payslip):
        """Load and display earnings section."""
        self.basic_pay_label.setText(f"{payslip.get('basic_pay', 0):,.2f}")
        self.overtime_pay_label.setText(f"{payslip.get('overtime_pay', 0):,.2f}")
        holiday_pay = payslip.get('holiday_pay', 0)
        self.holiday_label.setText(f"{holiday_pay:,.2f}" if holiday_pay > 0 else "-")
        self.salary_adjustment_label.setText(f"{payslip.get('salary_adjustment', 0):,.2f}")
        self.vacation_sickleave_label.setText(f"{payslip.get('vacation_sickleave', 0):,.2f}")
        incentive_pay = payslip.get('incentive_pay', 0)
        self.incentive_pay_label.setText(f"{incentive_pay:,.2f}" if incentive_pay > 0 else "")
        self.gross_pay_label.setText(f"{payslip.get('gross_pay', 0):,.2f}")
    
    def _load_deductions(self, payslip):
        """Load and display deductions section."""
        self.sss_contrib_label.setText(f"{payslip.get('sss_contribution', 0):,.2f}")
        self.phic_label.setText(f"{payslip.get('philhealth_contribution', 0):,.2f}")
        self.pagibig_contrib_label.setText(f"{payslip.get('pagibig_contribution', 0):,.2f}")
        self.tax_label.setText(f"{payslip.get('withholding_tax', 0):,.2f}")
        self.late_label.setText(f"{payslip.get('late_deduction', 0):,.2f}")
        self.cash_advance_label.setText(f"{payslip.get('cash_advance', 0):,.2f}")
        other_deductions = payslip.get('other_deductions', 0)
        self.others_label.setText(f"{other_deductions:,.2f}" if other_deductions > 0 else "")
        self.undertime_label.setText(f"{payslip.get('undertime_deduction', 0):,.2f}")
        self.total_deduction_label.setText(f"{payslip.get('total_deductions', 0):,.2f}")
    
    def _export_to_pdf(self):
        """Export current payslip to PDF."""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            from utils.pdf_generator import PayslipPDFGenerator
            from models.company_model import get_company_settings
            from models.employee_model import get_employee_by_id, get_latest_payslip_for_employee
            from datetime import datetime
            
            if not self.employee_id:
                QMessageBox.warning(self, "No Data", "No payslip data available to export.")
                return
            
            # Get default filename
            employee = get_employee_by_id(self.employee_id)
            if not employee:
                QMessageBox.warning(self, "Error", "Employee data not found.")
                return
            
            default_filename = f"Payslip_{employee.employee_code}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            # Show save dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Payslip as PDF",
                default_filename,
                "PDF Files (*.pdf)"
            )
            
            if not filename:
                return  # User cancelled
            
            # Get data for PDF
            company_settings = get_company_settings()
            payslip = get_latest_payslip_for_employee(self.employee_id)
            
            if not payslip:
                QMessageBox.warning(self, "No Data", "No payslip data available for this employee.")
                return
            
            # Prepare company data
            company_data = {
                'name': company_settings.get('company_name', 'COMPANY NAME'),
                'address': company_settings.get('address', 'Address not available'),
                'contact': f"{company_settings.get('contact_number', 'N/A')} | {company_settings.get('email', 'N/A')}"
            }
            
            # Prepare employee data
            employee_data = {
                'name': f"{employee.first_name} {employee.last_name}",
                'position': employee.position or 'N/A',
                'employee_code': employee.employee_code
            }
            
            # Prepare payslip data
            payslip_pdf_data = {
                'earnings': {
                    'Basic Pay': float(payslip.get('basic_pay', 0)),
                    'Overtime Pay': float(payslip.get('overtime_pay', 0)),
                    'Holiday Pay': float(payslip.get('holiday_pay', 0)),
                    'Vacation/Sick Leave': float(payslip.get('vacation_sickleave', 0)),
                    'Salary Adjustment': float(payslip.get('salary_adjustment', 0)),
                    'Incentive Pay': float(payslip.get('incentive_pay', 0)),
                },
                'deductions': {
                    'SSS Contribution': float(payslip.get('sss_contribution', 0)),
                    'PhilHealth Contribution': float(payslip.get('philhealth_contribution', 0)),
                    'Pag-IBIG Contribution': float(payslip.get('pagibig_contribution', 0)),
                    'Withholding Tax': float(payslip.get('withholding_tax', 0)),
                    'Late Deduction': float(payslip.get('late_deduction', 0)),
                    'Cash Advance': float(payslip.get('cash_advance', 0)),
                    'Undertime Deduction': float(payslip.get('undertime_deduction', 0)),
                    'Other Deductions': float(payslip.get('other_deductions', 0)),
                },
                'gross_pay': float(payslip.get('gross_pay', 0)),
                'total_deductions': float(payslip.get('total_deductions', 0)),
                'net_pay': float(payslip.get('net_pay', 0))
            }
            
            # Get period
            start_date = payslip.get('start_date')
            end_date = payslip.get('end_date')
            
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date.split()[0], '%Y-%m-%d').date()
            elif hasattr(start_date, 'date'):
                start_date = start_date.date()
            
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date.split()[0], '%Y-%m-%d').date()
            elif hasattr(end_date, 'date'):
                end_date = end_date.date()
            
            period = f"{start_date.strftime('%B %d')}-{end_date.strftime('%d, %Y')}"
            
            # Generate PDF
            success = PayslipPDFGenerator.generate(
                filename,
                company_data,
                employee_data,
                payslip_pdf_data,
                period
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Payslip has been exported to PDF successfully!\n\nSaved to: {filename}"
                )
                
                # Log the action
                from models.audit_model import log_audit
                try:
                    # Get user ID from employee code (assuming username = employee_code)
                    from models.database import get_connection
                    with get_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("SELECT id FROM users WHERE username = %s", (employee.employee_code,))
                            row = cur.fetchone()
                            if row:
                                log_audit(row[0], "Export PDF", f"Exported payslip to PDF: {filename}")
                except:
                    pass
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF. Please try again.")
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to export payslip: {str(e)}")
            import traceback
            traceback.print_exc()


class EmployeeMainWindow(QMainWindow):
    """
    Employee - Restricted, end-user level access for workforce transparency.
    Read-only, self-service interface per Figure 4.
    
    Primary Function:
    - Payslip Viewing - Retrieve personal compensation records
    
    Additional Self-Service Features:
    - Time In/Out - Track personal attendance
    - Contributions & Deductions - View SSS, PhilHealth, Pag-IBIG, tax details
    - Leave & Benefits - Manage personal leave requests
    
    Access Restrictions:
    - Limited to own records only (no system-wide access)
    - Read-only interface (no data alteration privileges)
    - No system-wide reports generation
    - No user management capabilities
    
    Ensures workforce can verify income details securely without risking unauthorized changes.
    """

    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.employee_id = None
        if user:
            from models.user_model import get_employee_id_for_user
            self.employee_id = get_employee_id_for_user(user.id)
        
        self.setWindowTitle("Proly System - Employee")
        self.resize(1280, 800)
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        main_hlayout = QHBoxLayout(central)
        main_hlayout.setContentsMargins(0, 0, 0, 0)
        main_hlayout.setSpacing(0)

        # Left sidebar
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 40, 0, 20)
        sb_layout.setSpacing(10)

        # Logo row with logo image
        logo_lbl = QLabel("  Proly")
        logo_lbl.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #333; margin-left: 20px; margin-bottom: 20px;"
        )
        logo_icon = QLabel()
        logo_icon.setFixedSize(30, 30)
        pix = QPixmap("assets/images/logo.png")
        if not pix.isNull():
            logo_icon.setPixmap(
                pix.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )

        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(25, 0, 0, 0)
        logo_row.addWidget(logo_icon)
        logo_row.addWidget(logo_lbl)
        logo_row.addStretch()

        sb_layout.addLayout(logo_row)
        sb_layout.addSpacing(30)

        menu_lbl = QLabel("MENU")
        menu_lbl.setStyleSheet(
            "color: #888; font-size: 11px; margin-left: 30px; letter-spacing: 1px;"
        )
        sb_layout.addWidget(menu_lbl)

        self.btn_dashboard = self._create_nav_btn("Dashboard", "assets/images/dashboardIcon.png")
        self.btn_timekeeping = self._create_nav_btn("Time In/Out", None)
        self.btn_payslip = self._create_nav_btn("Payslip\nViewing", "assets/images/payslipViewingIcon.png")
        self.btn_contributions = self._create_nav_btn("Contributions\n& Deductions", None)
        self.btn_leave_benefits = self._create_nav_btn("Leave & Benefits", None)

        sb_layout.addWidget(self.btn_dashboard)
        sb_layout.addWidget(self.btn_timekeeping)
        sb_layout.addWidget(self.btn_payslip)
        sb_layout.addWidget(self.btn_contributions)
        sb_layout.addWidget(self.btn_leave_benefits)
        sb_layout.addStretch()

        main_hlayout.addWidget(sidebar)

        # Right content area
        content_container = QWidget()
        content_container.setObjectName("MainContentArea")
        cc_layout = QVBoxLayout(content_container)
        cc_layout.setContentsMargins(0, 0, 0, 0)
        cc_layout.setSpacing(0)

        top_bar = QWidget()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(80)
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(30, 0, 30, 0)

        search = QLineEdit()
        search.setObjectName("SearchInput")
        search.setPlaceholderText("Search")
        search.setFixedWidth(400)
        search.setFixedHeight(40)

        profile_lbl = QLabel("Employee")
        profile_lbl.setStyleSheet("font-weight: bold; color: #333;")

        logout_btn = QPushButton()
        logout_btn.setFixedSize(50, 50)
        
        # Load logout icon with proper path resolution
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "..", "assets", "images", "logoutIcon.png")
        icon_path = os.path.normpath(icon_path)
        
        # Try to load icon, fallback to text if it fails
        if os.path.exists(icon_path):
            logout_icon = QIcon(icon_path)
            if not logout_icon.isNull():
                logout_btn.setIcon(logout_icon)
                logout_btn.setIconSize(QSize(32, 32))
            else:
                logout_btn.setText("⎋")  # Fallback text
        else:
            logout_btn.setText("⎋")  # Fallback text if icon not found
        
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                border-radius: 6px;
                border: none;
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #222;
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setToolTip("Logout")
        logout_btn.clicked.connect(self._handle_logout)

        tb_layout.addWidget(search)
        tb_layout.addStretch()
        tb_layout.addWidget(profile_lbl)
        tb_layout.addSpacing(15)
        tb_layout.addWidget(logout_btn)

        cc_layout.addWidget(top_bar)

        self.stack = QStackedWidget()
        self.dashboard_view = EmployeeDashboardView(employee_id=self.employee_id)
        self.dashboard_view.navigate_to_payslip = lambda: self._navigate(2)
        from views.employee_timekeeping_view import EmployeeTimekeepingView
        self.timekeeping_view = EmployeeTimekeepingView(employee_id=self.employee_id, user_id=user.id if user else None)
        self.payslip_view = EmployeePayslipView(employee_id=self.employee_id)
        from views.employee_contributions_view import EmployeeContributionsView
        self.contributions_view = EmployeeContributionsView(employee_id=self.employee_id)
        from views.employee_leave_benefits_view import EmployeeLeaveBenefitsView
        self.leave_benefits_view = EmployeeLeaveBenefitsView(employee_id=self.employee_id)

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.timekeeping_view)
        self.stack.addWidget(self.payslip_view)
        self.stack.addWidget(self.contributions_view)
        self.stack.addWidget(self.leave_benefits_view)

        cc_layout.addWidget(self.stack)

        main_hlayout.addWidget(content_container)

        # Navigation
        self.btn_dashboard.clicked.connect(lambda: self._navigate(0))
        self.btn_timekeeping.clicked.connect(lambda: self._navigate(1))
        self.btn_payslip.clicked.connect(lambda: self._navigate(2))
        self.btn_contributions.clicked.connect(lambda: self._navigate(3))
        self.btn_leave_benefits.clicked.connect(lambda: self._navigate(4))

        self.btn_dashboard.setChecked(True)
        
        # Ensure initial data load
        if self.employee_id:
            self.dashboard_view.refresh_data()
            self.timekeeping_view.refresh_data()
            self.payslip_view.refresh_data()
            self.contributions_view.refresh_data()
            self.leave_benefits_view.refresh_data()
    
    def update_employee_id(self, employee_id: Optional[int]):
        """Update employee ID for all views and refresh data."""
        self.employee_id = employee_id
        if hasattr(self.dashboard_view, 'set_employee_id'):
            self.dashboard_view.set_employee_id(employee_id)
        if hasattr(self.timekeeping_view, 'set_employee_id'):
            self.timekeeping_view.set_employee_id(employee_id)
        if hasattr(self.payslip_view, 'set_employee_id'):
            self.payslip_view.set_employee_id(employee_id)
        if hasattr(self, 'contributions_view') and self.contributions_view:
            self.contributions_view.employee_id = employee_id
            self.contributions_view.refresh_data()
        if hasattr(self, 'leave_benefits_view') and self.leave_benefits_view:
            self.leave_benefits_view.employee_id = employee_id
            self.leave_benefits_view.refresh_data()

    def _create_nav_btn(self, text: str, icon_path: str | None = None) -> QPushButton:
        btn = QPushButton(f"  {text}")
        btn.setProperty("class", "NavBtn")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if icon_path:
            icon = QIcon(icon_path)
            if not icon.isNull():
                btn.setIcon(icon)
                btn.setIconSize(QSize(20, 20))
        return btn

    def _navigate(self, index: int):
        """Navigate to a page and refresh its data."""
        self.stack.setCurrentIndex(index)
        
        # Refresh data when navigating to a page
        try:
            if index == 0:  # Dashboard
                self.dashboard_view.refresh_data()
            elif index == 1:  # Timekeeping
                self.timekeeping_view.refresh_data()
            elif index == 2:  # Payslip View
                self.payslip_view.refresh_data()
        except Exception as e:
            logger.exception("Error refreshing view data: %s", e)
    
    def _handle_logout(self):
        """Handle logout - close main window and show login window."""
        from PyQt6.QtWidgets import QMessageBox, QApplication
        from views.login_view import LoginWindow
        from controllers.auth_controller import AuthController
        
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Log the logout action
            if self.user:
                from models.audit_model import log_audit
                log_audit(self.user.id, "Logout", "User logged out")
            
            # Create and show login window BEFORE closing this window
            login_window = LoginWindow()
            auth_controller = AuthController(login_window)
            login_window.show()
            
            # Keep reference to prevent garbage collection
            app = QApplication.instance()
            if app:
                app.login_window = login_window
                app.auth_controller = auth_controller
            
            # Close this window
            self.close()
    
    def refresh_all_views(self):
        """Refresh data in all views."""
        try:
            self.dashboard_view.refresh_data()
            self.payslip_view.refresh_data()
        except Exception as e:
            logger.exception("Error refreshing all views: %s", e)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = EmployeeMainWindow()
    window.show()
    sys.exit(app.exec())

