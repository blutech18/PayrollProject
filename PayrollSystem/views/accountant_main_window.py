from __future__ import annotations

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

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
    QLineEdit, QComboBox, QDateEdit {
        background-color: #FFFFFF; 
        border: 2px solid #D6CDC6;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #333333;
    }
    QComboBox::drop-down {
        border: none;
        width: 30px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid #666;
        width: 0;
        height: 0;
    }
    QComboBox QAbstractItemView {
        background-color: white;
        color: #333333;
        selection-background-color: #F0D095;
        selection-color: #333333;
    }

    /* TABLE STYLING */
    QTableWidget {
        background-color: #FDF8F2;
        border: 1px solid #EBE0D6;
        gridline-color: #E0D0C0;
        font-size: 13px;
    }
    QHeaderView::section {
        background-color: #C0A065;
        padding: 10px;
        border: none;
        font-weight: bold;
        color: #FFFFFF;
        font-size: 13px;
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

    QPushButton.SecondaryBtn {
        background-color: #EFEBE6;
        border: 1px solid #C0C0C0;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 12px;
    }
    QPushButton.SecondaryBtn:hover { background-color: #E0DBD5; }
    
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


def create_stat_card(title: str, value: str, subtext: str = "", icon_char: str = "?") -> QWidget:
    """Helper to create those square stat cards."""
    card = ShadowCard()
    card.setFixedSize(280, 160)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(25, 25, 25, 25)

    icon_box = QLabel(icon_char)
    icon_box.setFixedSize(32, 32)
    icon_box.setStyleSheet(
        "background-color: #555; color: white; border-radius: 4px; font-weight: bold; qproperty-alignment: AlignCenter;"
    )

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet("font-size: 13px; color: #666; font-weight: 500; margin-top: 5px;")

    lbl_val = QLabel(value)
    lbl_val.setStyleSheet("font-size: 32px; font-weight: 800; color: #444;")

    lbl_sub = QLabel(subtext)
    if "+" in subtext or "↑" in subtext:
        lbl_sub.setStyleSheet("font-size: 11px; font-weight: bold; color: #6BA855;")
    else:
        lbl_sub.setStyleSheet("font-size: 12px; font-weight: bold; color: #555;")

    layout.addWidget(icon_box)
    layout.addWidget(lbl_title)
    layout.addWidget(lbl_val)
    layout.addWidget(lbl_sub)
    layout.addStretch()
    return card


import logging


logger = logging.getLogger(__name__)


class AccountantDashboardView(QWidget):
    """Accountant Dashboard matching Wireframe_page-0005.jpg."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 30, 40, 40)

        title = QLabel("DASHBOARD OVERVIEW")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #555;")
        self.layout.addWidget(title)
        self.layout.addSpacing(20)

        # Top Row Cards
        self.row = QHBoxLayout()
        self.row.setSpacing(30)
        self._load_data()
        self.row.addStretch()
        self.layout.addLayout(self.row)

        self.layout.addSpacing(20)

        # Bottom Center Card (Total Payroll)
        self.row2 = QHBoxLayout()
        self.row2.setSpacing(30)
        self.row2.addSpacing(100)  # Offset to center visually like wireframe
        self._load_total_payroll_card()
        self.row2.addStretch()
        self.layout.addLayout(self.row2)
        self.layout.addStretch()
    
    def _load_data(self):
        """Load dashboard data from database."""
        try:
            from models.dashboard_model import get_accountant_dashboard_stats
            stats = get_accountant_dashboard_stats()
            
            self.row.addWidget(create_stat_card("Pending Verification", str(stats["pending_verification"]), "", "?"))
            self.row.addWidget(create_stat_card("Verified This Month", str(stats["verified_this_month"]), "", "✓"))
        except Exception:
            # Fallback to default values
            self.row.addWidget(create_stat_card("Pending Verification", "0", "", "?"))
            self.row.addWidget(create_stat_card("Verified This Month", "0", "", "✓"))
    
    def _load_total_payroll_card(self):
        """Load total payroll card."""
        try:
            from models.dashboard_model import get_accountant_dashboard_stats
            stats = get_accountant_dashboard_stats()
            total_payroll = stats["total_payroll"]
            
            # Format as PHP currency
            if total_payroll >= 1000000:
                formatted = f"{total_payroll / 1000000:.1f}M PHP"
            elif total_payroll >= 1000:
                formatted = f"{total_payroll / 1000:.1f}K PHP"
            else:
                formatted = f"{total_payroll:.2f} PHP"
        except Exception:
            formatted = "0 PHP"
        
        money_card = ShadowCard()
        money_card.setFixedSize(320, 180)
        ml = QVBoxLayout(money_card)
        ml.setContentsMargins(30, 30, 30, 30)

        icon = QLabel("■")
        icon.setStyleSheet("color: #555; font-size: 20px;")
        ml.addWidget(icon)
        ml.addSpacing(10)
        ml.addWidget(QLabel("Total Payroll", styleSheet="color:#666; font-weight:500;"))
        ml.addWidget(QLabel(formatted, styleSheet="font-size:36px; font-weight:900; color:#444; letter-spacing:1px;"))
        ml.addStretch()

        self.row2.addWidget(money_card)


class AccountantPayrollCompView(QWidget):
    """Payroll Computation view matching Wireframe_page-0006.jpg."""

    def __init__(self):
        super().__init__()
        
        # Main scroll container to handle fullscreen properly
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("QWidget { background-color: transparent; }")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(30)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        card = ShadowCard()
        card.setMinimumWidth(1000)
        card.setMaximumWidth(1200)
        card.setMinimumHeight(650)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)

        # Header with Title
        header_layout = QHBoxLayout()
        title_label = QLabel("PAYROLL COMPUTATION")
        title_label.setStyleSheet("font-size:20px; font-weight:800; color:#444;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        cl.addLayout(header_layout)
        cl.addSpacing(20)

        # Top Controls
        top = QHBoxLayout()
        top.addWidget(QLabel("Pay Period :", styleSheet="font-weight:600; font-size:13px; color:#555;"))
        self.pay_period_combo = QComboBox()
        self.pay_period_combo.setFixedWidth(250)
        self.pay_period_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #D6CDC6;
                border-radius: 6px;
                background-color: white;
                color: #333333;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333333;
                selection-background-color: #F0D095;
                selection-color: #333333;
            }
        """)
        # Don't connect signal yet - will connect after table is created
        top.addWidget(self.pay_period_combo)
        top.addSpacing(15)
        self.run_payroll_btn = QPushButton("🔄 RUN PAYROLL")
        self.run_payroll_btn.setProperty("class", "PrimaryBtn")
        self.run_payroll_btn.setFixedWidth(160)
        self.run_payroll_btn.setFixedHeight(38)
        self.run_payroll_btn.clicked.connect(self._run_payroll)
        top.addWidget(self.run_payroll_btn)
        top.addStretch()
        cl.addLayout(top)
        cl.addSpacing(20)

        # Summary Info Row
        self.summary_layout = QHBoxLayout()
        self.total_employees_label = QLabel("Employees: 0")
        self.total_employees_label.setStyleSheet("font-size:13px; font-weight:600; color:#666;")
        self.total_payroll_label = QLabel("Total Payroll: PHP 0.00")
        self.total_payroll_label.setStyleSheet("font-size:14px; font-weight:700; color:#F0D095;")
        self.summary_layout.addWidget(self.total_employees_label)
        self.summary_layout.addSpacing(30)
        self.summary_layout.addWidget(self.total_payroll_label)
        self.summary_layout.addStretch()
        cl.addLayout(self.summary_layout)
        cl.addSpacing(15)

        # Table
        self.payroll_table = QTableWidget(0, 6)
        self.payroll_table.setHorizontalHeaderLabels(["Employee ID", "Name", "Gross Pay", "Deductions", "Net Pay", "Status"])
        self.payroll_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.payroll_table.verticalHeader().setVisible(False)
        self.payroll_table.setAlternatingRowColors(True)
        self.payroll_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.payroll_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.payroll_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EBE0D6;
                border-radius: 8px;
            }
        """)
        cl.addWidget(self.payroll_table)
        cl.addSpacing(15)

        # Bottom Buttons
        bot = QHBoxLayout()
        bot.addStretch()
        self.view_details_btn = QPushButton("📋 View Details")
        self.view_details_btn.setProperty("class", "SecondaryBtn")
        self.view_details_btn.setFixedWidth(150)
        self.view_details_btn.setFixedHeight(38)
        self.view_details_btn.setStyleSheet("""
            QPushButton {
                background-color: #EFEBE6;
                border: 2px solid #C0C0C0;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E0DBD5;
                border-color: #A0A0A0;
            }
        """)
        self.view_details_btn.clicked.connect(self._view_details)
        
        self.submit_btn = QPushButton("✓ Submit for Verification")
        self.submit_btn.setProperty("class", "PrimaryBtn")
        self.submit_btn.setFixedWidth(200)
        self.submit_btn.setFixedHeight(38)
        self.submit_btn.clicked.connect(self._submit_payroll)
        
        self.export_pdf_btn = QPushButton("📄 Export PDF")
        self.export_pdf_btn.setProperty("class", "PrimaryBtn")
        self.export_pdf_btn.setFixedWidth(150)
        self.export_pdf_btn.setFixedHeight(38)
        self.export_pdf_btn.clicked.connect(self._export_payroll_to_pdf)
        
        bot.addWidget(self.view_details_btn)
        bot.addSpacing(15)
        bot.addWidget(self.submit_btn)
        bot.addSpacing(15)
        bot.addWidget(self.export_pdf_btn)
        bot.addStretch()
        cl.addLayout(bot)

        # Center card
        card_container = QHBoxLayout()
        card_container.addStretch()
        card_container.addWidget(card)
        card_container.addStretch()
        layout.addLayout(card_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)
        
        # NOW load payroll periods and connect signal (after table is created)
        self._load_payroll_periods()
        self.pay_period_combo.currentIndexChanged.connect(self._on_period_changed)
    
    def _load_payroll_periods(self):
        """Load payroll periods from database."""
        try:
            from models.payroll_model import get_payroll_periods
            periods = get_payroll_periods()
            for period in periods:
                self.pay_period_combo.addItem(period["name"], period["id"])
        except Exception:
            pass
    
    def _on_period_changed(self, index):
        """Load payroll entries when period is selected."""
        if index < 0:
            return
        period_id = self.pay_period_combo.currentData()
        if period_id:
            self._load_payroll_entries(period_id)
    
    def _load_payroll_entries(self, period_id: int):
        """Load payroll entries for selected period."""
        try:
            from models.payroll_model import get_payroll_entries_by_period
            from decimal import Decimal
            
            entries = get_payroll_entries_by_period(period_id)
            
            if not entries:
                self.payroll_table.setRowCount(0)
                self.total_employees_label.setText("Employees: 0")
                self.total_payroll_label.setText("Total Payroll: PHP 0.00")
                return
            
            self.payroll_table.setRowCount(len(entries))
            total_payroll = 0.0
            
            for row, entry in enumerate(entries):
                # Convert Decimal to float for all numeric fields
                gross_pay = float(entry['gross_pay']) if entry.get('gross_pay') else 0.0
                total_deductions = float(entry['total_deductions']) if entry.get('total_deductions') else 0.0
                net_pay = float(entry['net_pay']) if entry.get('net_pay') else 0.0
                
                # Employee ID
                id_item = QTableWidgetItem(entry.get("employee_code", "N/A"))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.payroll_table.setItem(row, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(entry.get("name", "Unknown"))
                self.payroll_table.setItem(row, 1, name_item)
                
                # Gross Pay
                gross_item = QTableWidgetItem(f"PHP {gross_pay:,.2f}")
                gross_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.payroll_table.setItem(row, 2, gross_item)
                
                # Deductions
                ded_item = QTableWidgetItem(f"PHP {total_deductions:,.2f}")
                ded_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.payroll_table.setItem(row, 3, ded_item)
                
                # Net Pay
                total_payroll += net_pay
                net_item = QTableWidgetItem(f"PHP {net_pay:,.2f}")
                net_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                net_item.setForeground(QColor("#28a745"))
                from PyQt6.QtGui import QFont
                font = QFont()
                font.setBold(True)
                net_item.setFont(font)
                self.payroll_table.setItem(row, 4, net_item)
                
                # Status
                status = entry.get('status', 'DRAFT')
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if status == 'PENDING':
                    status_item.setForeground(QColor("#FFA500"))
                elif status == 'VERIFIED':
                    status_item.setForeground(QColor("#28a745"))
                else:
                    status_item.setForeground(QColor("#666"))
                self.payroll_table.setItem(row, 5, status_item)
            
            # Update summary
            self.total_employees_label.setText(f"Employees: {len(entries)}")
            self.total_payroll_label.setText(f"Total Payroll: PHP {total_payroll:,.2f}")
            
        except Exception as e:
            self.payroll_table.setRowCount(0)
            self.total_employees_label.setText("Employees: 0")
            self.total_payroll_label.setText("Total Payroll: PHP 0.00")
            logger.exception("Error loading payroll entries: %s", e)
    
    def _view_details(self):
        """View detailed breakdown of selected payroll entry."""
        from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
        current_row = self.payroll_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a payroll entry to view details.")
            return
        
        # Get payroll entry details
        employee_code = self.payroll_table.item(current_row, 0).text()
        name = self.payroll_table.item(current_row, 1).text()
        gross = self.payroll_table.item(current_row, 2).text()
        deductions = self.payroll_table.item(current_row, 3).text()
        net = self.payroll_table.item(current_row, 4).text()
        status = self.payroll_table.item(current_row, 5).text()
        
        # Create detailed dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Payroll Details - {name}")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #F2EBE9;
            }
            QLabel {
                font-size: 13px;
                color: #444;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel(f"PAYROLL BREAKDOWN")
        header.setStyleSheet("font-size: 18px; font-weight: 800; color: #333;")
        layout.addWidget(header)
        layout.addSpacing(10)
        
        # Employee Info
        emp_info = QLabel(f"<b>{name}</b> ({employee_code})")
        emp_info.setStyleSheet("font-size: 14px; color: #555;")
        layout.addWidget(emp_info)
        layout.addSpacing(20)
        
        # Details Grid
        grid = QGridLayout()
        grid.setVerticalSpacing(15)
        grid.setHorizontalSpacing(20)
        
        details = [
            ("Gross Pay:", gross, "#444"),
            ("Total Deductions:", deductions, "#dc3545"),
            ("Net Pay:", net, "#28a745"),
            ("Status:", status, "#FFA500" if status == "PENDING" else "#28a745"),
        ]
        
        for row, (label_text, value, color) in enumerate(details):
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: 600;")
            grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignRight)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"font-weight: 700; font-size: 14px; color: {color};")
            grid.addWidget(value_label, row, 1)
        
        layout.addLayout(grid)
        layout.addSpacing(20)
        
        # Note
        note = QLabel("Note: For detailed breakdown including SSS, PhilHealth, Pag-IBIG, and Tax,\nplease refer to the payslip generation module.")
        note.setStyleSheet("font-size: 11px; color: #888; font-style: italic;")
        layout.addWidget(note)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setFixedHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0D095;
                border: 2px solid #C0A065;
                border-radius: 6px;
                font-weight: 700;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def _export_payroll_to_pdf(self):
        """Export payroll report to PDF."""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            from utils.pdf_generator import generate_payroll_report_pdf
            from models.payroll_model import get_payroll_entries_by_period
            from models.audit_model import log_audit
            from datetime import datetime
            
            # Get current period
            period_text = self.pay_period_combo.currentText()
            if period_text == "Select Period" or not period_text:
                QMessageBox.warning(self, "No Period", "Please select a payroll period first.")
                return
            
            period_id = self.pay_period_combo.currentData()
            if not period_id:
                QMessageBox.warning(self, "No Period", "Please select a valid payroll period.")
                return
            
            # Get payroll entries
            payroll_data = get_payroll_entries_by_period(period_id)
            
            if not payroll_data:
                QMessageBox.warning(self, "No Data", "No payroll entries found for the selected period.")
                return
            
            # Get default filename
            period_safe = period_text.replace(" ", "_").replace(",", "")
            default_filename = f"Payroll_Report_{period_safe}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            # Show save dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Payroll Report as PDF",
                default_filename,
                "PDF Files (*.pdf)"
            )
            
            if not filename:
                return  # User cancelled
            
            # Generate PDF
            success = generate_payroll_report_pdf(filename, payroll_data, period_text)
            
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Payroll report has been exported to PDF successfully!\n\nSaved to: {filename}"
                )
                
                # Log the action
                log_audit(None, "Export PDF", f"Exported payroll report to PDF: {period_text}")
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF. Please try again.")
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to export payroll report: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _submit_payroll(self):
        """Submit payroll for verification."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            from models.audit_model import log_audit
            
            period_id = self.pay_period_combo.currentData()
            if not period_id:
                QMessageBox.warning(self, "Validation Error", "Please select a pay period.")
                return
            
            # Update payroll entries status to PENDING for verification
            from models.database import get_connection
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE payroll_entries SET status = 'PENDING' WHERE payroll_period_id = %s",
                        (period_id,)
                    )
                    conn.commit()
            
            log_audit(None, "Submit Payroll", f"Submitted payroll period {self.pay_period_combo.currentText()} for verification")
            QMessageBox.information(self, "Success", "Payroll has been submitted for verification.")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to submit payroll: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _run_payroll(self):
        """Run payroll computation for selected period."""
        from PyQt6.QtWidgets import QMessageBox
        from models.audit_model import log_audit
        
        period_id = self.pay_period_combo.currentData()
        if not period_id:
            QMessageBox.warning(self, "Validation Error", "Please select a pay period first.")
            return
        
        reply = QMessageBox.question(
            self,
            "Run Payroll",
            f"Are you sure you want to run payroll computation for:\n{self.pay_period_combo.currentText()}?\n\nThis will calculate salaries for all active employees.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from models.payroll_computation_model import compute_payroll_period
                from models.database import get_connection
                
                # Get period details for computation
                with get_connection() as conn:
                    with conn.cursor(dictionary=True) as cur:
                        cur.execute("SELECT start_date, end_date FROM payroll_periods WHERE id = %s", (period_id,))
                        period = cur.fetchone()
                
                if not period:
                    QMessageBox.critical(self, "Error", "Payroll period not found.")
                    return
                
                # Compute payroll using attendance data
                results = compute_payroll_period(period_id)
                
                # Reload payroll entries to refresh data
                self._load_payroll_entries(period_id)
                
                log_audit(None, "Run Payroll", 
                         f"Computed payroll for period: {self.pay_period_combo.currentText()}. "
                         f"Employees computed: {results['computed']}/{results['total_employees']}")
                
                msg = f"Payroll computation completed!\n\n"
                msg += f"Period: {self.pay_period_combo.currentText()}\n"
                msg += f"Total Employees: {results['total_employees']}\n"
                msg += f"Successfully Computed: {results['computed']}\n"
                if results['errors']:
                    msg += f"Errors: {len(results['errors'])}\n"
                msg += f"\n{self.total_payroll_label.text()}"
                
                QMessageBox.information(self, "Success", msg)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to run payroll: {str(e)}")
                import traceback
                traceback.print_exc()


class AccountantPayrollVerificationView(QWidget):
    """Payroll Verification view matching Wireframe_page-0007.jpg."""

    def __init__(self):
        super().__init__()
        
        # Main scroll container to handle fullscreen properly
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("QWidget { background-color: transparent; }")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(30)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        card = ShadowCard()
        card.setMinimumWidth(900)
        card.setMaximumWidth(1200)
        card.setMinimumHeight(600)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)

        # Header
        cl.addWidget(QLabel("PENDING VERIFICATION", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        self.period_label = QLabel("Pay Period :", styleSheet="font-size:14px; font-weight:500; color:#666;")
        cl.addWidget(self.period_label)
        cl.addSpacing(15)

        # Table
        self.verification_table = QTableWidget(0, 5)
        self.verification_table.setHorizontalHeaderLabels(["ID", "Name", "Salary", "Deduction", "Net Pay"])
        self.verification_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verification_table.verticalHeader().setVisible(False)
        self.verification_table.setAlternatingRowColors(True)
        cl.addWidget(self.verification_table)

        # Total
        cl.addSpacing(10)
        self.total_label = QLabel("Total Payroll : PHP 0.00", styleSheet="font-size:14px; font-weight:bold; color:#444;")
        cl.addWidget(self.total_label)
        cl.addSpacing(20)

        # Bottom Buttons
        bot = QHBoxLayout()
        self.approve_all_btn = QPushButton("APPROVE ALL")
        self.approve_all_btn.setProperty("class", "PrimaryBtn")
        self.approve_all_btn.setMinimumWidth(150)
        self.approve_all_btn.clicked.connect(self._approve_all)
        self.reject_btn = QPushButton("REJECT")
        self.reject_btn.setProperty("class", "SecondaryBtn")
        self.reject_btn.setMinimumWidth(150)
        self.reject_btn.clicked.connect(self._reject_payroll)
        self.request_revision_btn = QPushButton("REQUEST REVISION")
        self.request_revision_btn.setProperty("class", "SecondaryBtn")
        self.request_revision_btn.setMinimumWidth(150)
        self.request_revision_btn.clicked.connect(self._request_revision)

        bot.addWidget(self.approve_all_btn)
        bot.addSpacing(20)
        bot.addWidget(self.reject_btn)
        bot.addSpacing(20)
        bot.addWidget(self.request_revision_btn)
        bot.addStretch()
        cl.addLayout(bot)

        # Center card
        card_container = QHBoxLayout()
        card_container.addStretch()
        card_container.addWidget(card)
        card_container.addStretch()
        layout.addLayout(card_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)
        
        # Load pending verification data
        self._load_pending_verification()
    
    def _load_pending_verification(self):
        """Load pending verification entries."""
        try:
            from models.payroll_model import get_pending_verification_entries, get_total_payroll_for_period
            entries = get_pending_verification_entries()
            total = get_total_payroll_for_period()
            
            self.verification_table.setRowCount(len(entries))
            for row, entry in enumerate(entries):
                # Convert Decimal to float for numeric fields
                salary = float(entry.get('salary', 0))
                deduction = float(entry.get('deduction', 0))
                net_pay = float(entry.get('net_pay', 0))
                
                self.verification_table.setItem(row, 0, QTableWidgetItem(entry.get("employee_code", "N/A")))
                self.verification_table.setItem(row, 1, QTableWidgetItem(entry.get("name", "Unknown")))
                self.verification_table.setItem(row, 2, QTableWidgetItem(f"PHP {salary:,.2f}"))
                self.verification_table.setItem(row, 3, QTableWidgetItem(f"PHP {deduction:,.2f}"))
                self.verification_table.setItem(row, 4, QTableWidgetItem(f"PHP {net_pay:,.2f}"))
            
            # Update period label if entries exist
            if entries:
                period_name = entries[0].get("period_name", "Unknown Period")
                self.period_label.setText(f"Pay Period : {period_name}")
            else:
                self.period_label.setText("Pay Period : No pending entries")
            
            self.total_label.setText(f"Total Payroll : PHP {total:,.2f}")
        except Exception as e:
            self.verification_table.setRowCount(0)
            self.total_label.setText("Total Payroll : PHP 0.00")
            self.period_label.setText("Pay Period : Error loading data")
            logger.exception("Error loading pending verification: %s", e)
    
    def _approve_all(self):
        """Approve all pending payroll entries."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            from models.audit_model import log_audit
            from models.database import get_connection
            
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE payroll_entries SET status = 'VERIFIED' WHERE status = 'PENDING'")
                    affected = cur.rowcount
                    conn.commit()
            
            log_audit(None, "Approve Payroll", f"Approved {affected} payroll entries")
            QMessageBox.information(self, "Success", f"Approved {affected} payroll entries.")
            self._load_pending_verification()  # Refresh the table
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to approve payroll: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _reject_payroll(self):
        """Reject pending payroll entries."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            from models.audit_model import log_audit
            from models.database import get_connection
            
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE payroll_entries SET status = 'REJECTED' WHERE status = 'PENDING'")
                    affected = cur.rowcount
                    conn.commit()
            
            log_audit(None, "Reject Payroll", f"Rejected {affected} payroll entries")
            QMessageBox.information(self, "Success", f"Rejected {affected} payroll entries.")
            self._load_pending_verification()  # Refresh the table
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to reject payroll: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _request_revision(self):
        """Request revision for pending payroll entries."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            from models.audit_model import log_audit
            from models.database import get_connection
            
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE payroll_entries SET status = 'REVISION_REQUESTED' WHERE status = 'PENDING'")
                    affected = cur.rowcount
                    conn.commit()
            
            log_audit(None, "Request Revision", f"Requested revision for {affected} payroll entries")
            QMessageBox.information(self, "Success", f"Revision requested for {affected} payroll entries.")
            self._load_pending_verification()  # Refresh the table
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to request revision: {str(e)}")
            import traceback
            traceback.print_exc()


class AccountantMainWindow(QMainWindow):
    """
    Accountant main window with focus on financial accuracy and integrity.
    Core functions per Figure 3:
    1. Payroll Computation - Execute salary calculations
    2. Reports - Generate financial summaries for stakeholders
    3. Payroll Verification - Validate payroll data before disbursement
    
    Strictly confined to fiscal dimensions with separation of duties from administrative functions.
    """

    def __init__(self, user=None):
        super().__init__()
        self.user = user  # Store user for logout and audit logging
        self.setWindowTitle("Proly System - Accountant")
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
        self.btn_payroll_comp = self._create_nav_btn(
            "Payroll\nComputation", "assets/images/payrollComputationIcon.png"
        )
        self.btn_reports = self._create_nav_btn(
            "Reports", "assets/images/reportsIcon.png"
        )
        self.btn_payroll_verify = self._create_nav_btn(
            "Payroll\nVerification", "assets/images/payrollVerificationIcon.png"
        )

        sb_layout.addWidget(self.btn_dashboard)
        sb_layout.addWidget(self.btn_payroll_comp)
        sb_layout.addWidget(self.btn_reports)
        sb_layout.addWidget(self.btn_payroll_verify)
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

        profile_lbl = QLabel("Accountant")
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
        self.dashboard_view = AccountantDashboardView()
        self.payroll_comp_view = AccountantPayrollCompView()
        # Import Reports view from HR module (shared for financial summaries)
        from views.hr_main_window import ReportsView
        self.reports_view = ReportsView()
        self.payroll_verify_view = AccountantPayrollVerificationView()

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.payroll_comp_view)
        self.stack.addWidget(self.reports_view)
        self.stack.addWidget(self.payroll_verify_view)

        cc_layout.addWidget(self.stack)

        main_hlayout.addWidget(content_container)

        # Navigation
        self.btn_dashboard.clicked.connect(lambda: self._navigate(0))
        self.btn_payroll_comp.clicked.connect(lambda: self._navigate(1))
        self.btn_reports.clicked.connect(lambda: self._navigate(2))
        self.btn_payroll_verify.clicked.connect(lambda: self._navigate(3))

        self.btn_dashboard.setChecked(True)

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
        self.stack.setCurrentIndex(index)
    
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


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = AccountantMainWindow()
    window.show()
    sys.exit(app.exec())

