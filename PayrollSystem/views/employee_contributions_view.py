"""
Employee Contributions and Deductions Summary View.
Implements Solution 3: Employee Self-Service - Tax Contributions and Deductions Summary.
"""

from __future__ import annotations

from typing import Optional
import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)


logger = logging.getLogger(__name__)


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


class EmployeeContributionsView(QWidget):
    """View showing employee tax contributions and deductions summary."""

    def __init__(self, employee_id: Optional[int] = None):
        super().__init__()
        self.employee_id = employee_id
        
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

        # Tax Contributions Card
        tax_card = ShadowCard()
        tax_card.setMinimumWidth(900)
        tax_card.setMaximumWidth(1200)
        tax_card.setMinimumHeight(400)
        tax_layout = QVBoxLayout(tax_card)
        tax_layout.setContentsMargins(40, 40, 40, 40)

        tax_layout.addWidget(QLabel("TAX CONTRIBUTIONS SUMMARY", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        tax_layout.addSpacing(20)

        self.tax_table = QTableWidget(0, 5)
        self.tax_table.setHorizontalHeaderLabels(["Period", "SSS", "PhilHealth", "Pag-IBIG", "Withholding Tax"])
        self.tax_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tax_table.verticalHeader().setVisible(False)
        self.tax_table.setAlternatingRowColors(True)
        
        # Style with white text
        self.tax_table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                color: #FFFFFF;
                gridline-color: #444444;
                border: 1px solid #C0A065;
                border-radius: 8px;
            }
            QTableWidget::item {
                color: #FFFFFF;
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QTableWidget::item:selected {
                background-color: #C0A065;
                color: #FFFFFF;
            }
            QTableWidget::item:alternate {
                background-color: #222222;
            }
            QHeaderView::section {
                background-color: #C0A065;
                color: #FFFFFF;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        tax_layout.addWidget(self.tax_table)

        # Center the tax card
        tax_card_container = QHBoxLayout()
        tax_card_container.addStretch()
        tax_card_container.addWidget(tax_card)
        tax_card_container.addStretch()
        layout.addLayout(tax_card_container)

        # Deductions Summary Card
        deductions_card = ShadowCard()
        deductions_card.setMinimumWidth(900)
        deductions_card.setMaximumWidth(1200)
        deductions_card.setMinimumHeight(400)
        deductions_layout = QVBoxLayout(deductions_card)
        deductions_layout.setContentsMargins(40, 40, 40, 40)

        deductions_layout.addWidget(QLabel("DEDUCTIONS SUMMARY", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        deductions_layout.addSpacing(20)

        self.deductions_table = QTableWidget(0, 5)
        self.deductions_table.setHorizontalHeaderLabels(["Period", "Late", "Cash Advance", "Undertime", "Other"])
        self.deductions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.deductions_table.verticalHeader().setVisible(False)
        self.deductions_table.setAlternatingRowColors(True)
        
        # Style with white text
        self.deductions_table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                color: #FFFFFF;
                gridline-color: #444444;
                border: 1px solid #C0A065;
                border-radius: 8px;
            }
            QTableWidget::item {
                color: #FFFFFF;
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QTableWidget::item:selected {
                background-color: #C0A065;
                color: #FFFFFF;
            }
            QTableWidget::item:alternate {
                background-color: #222222;
            }
            QHeaderView::section {
                background-color: #C0A065;
                color: #FFFFFF;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        deductions_layout.addWidget(self.deductions_table)

        # Center the deductions card
        deductions_card_container = QHBoxLayout()
        deductions_card_container.addStretch()
        deductions_card_container.addWidget(deductions_card)
        deductions_card_container.addStretch()
        layout.addLayout(deductions_card_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)

        if self.employee_id:
            self._load_data()

    def _load_data(self):
        """Load tax contributions and deductions data."""
        try:
            from models.database import get_connection

            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cur:
                    # Get all payroll entries for this employee
                    cur.execute("""
                        SELECT 
                            pp.name as period_name,
                            pp.start_date,
                            pp.end_date,
                            pe.sss_contrib,
                            pe.philhealth_contrib,
                            pe.pagibig_contrib,
                            pe.withholding_tax,
                            pe.late_deduction,
                            pe.cash_advance,
                            pe.undertime_deduction,
                            pe.other_deductions
                        FROM payroll_entries pe
                        JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
                        WHERE pe.employee_id = %s
                        ORDER BY pp.start_date DESC
                        LIMIT 12
                    """, (self.employee_id,))
                    
                    entries = cur.fetchall()

            # Populate tax contributions table
            self.tax_table.setRowCount(len(entries))
            for row, entry in enumerate(entries):
                period = entry['period_name'] or f"{entry['start_date']} to {entry['end_date']}"
                self.tax_table.setItem(row, 0, QTableWidgetItem(str(period)))
                self.tax_table.setItem(row, 1, QTableWidgetItem(f"{float(entry['sss_contrib'] or 0):,.2f}"))
                self.tax_table.setItem(row, 2, QTableWidgetItem(f"{float(entry['philhealth_contrib'] or 0):,.2f}"))
                self.tax_table.setItem(row, 3, QTableWidgetItem(f"{float(entry['pagibig_contrib'] or 0):,.2f}"))
                self.tax_table.setItem(row, 4, QTableWidgetItem(f"{float(entry['withholding_tax'] or 0):,.2f}"))

            # Populate deductions table
            self.deductions_table.setRowCount(len(entries))
            for row, entry in enumerate(entries):
                period = entry['period_name'] or f"{entry['start_date']} to {entry['end_date']}"
                self.deductions_table.setItem(row, 0, QTableWidgetItem(str(period)))
                self.deductions_table.setItem(row, 1, QTableWidgetItem(f"{float(entry['late_deduction'] or 0):,.2f}"))
                self.deductions_table.setItem(row, 2, QTableWidgetItem(f"{float(entry['cash_advance'] or 0):,.2f}"))
                self.deductions_table.setItem(row, 3, QTableWidgetItem(f"{float(entry['undertime_deduction'] or 0):,.2f}"))
                self.deductions_table.setItem(row, 4, QTableWidgetItem(f"{float(entry['other_deductions'] or 0):,.2f}"))

        except Exception as e:
            logger.exception("Error loading contributions data: %s", e)

    def refresh_data(self):
        """Refresh the data display."""
        if self.employee_id:
            self._load_data()

