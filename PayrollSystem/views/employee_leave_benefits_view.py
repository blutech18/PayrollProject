"""
Employee Leave Balances and Benefits View.
Implements Solution 3: Employee Self-Service - Leave Balances and Benefits Information.
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


class EmployeeLeaveBenefitsView(QWidget):
    """View showing employee leave balances and benefits information."""

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

        # Leave Balances Card
        leave_card = ShadowCard()
        leave_card.setMinimumWidth(900)
        leave_card.setMaximumWidth(1200)
        leave_card.setMinimumHeight(400)
        leave_layout = QVBoxLayout(leave_card)
        leave_layout.setContentsMargins(40, 40, 40, 40)

        leave_layout.addWidget(QLabel("LEAVE BALANCES", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        leave_layout.addSpacing(20)

        self.leave_table = QTableWidget(0, 5)
        self.leave_table.setHorizontalHeaderLabels(["Leave Type", "Total Allocated", "Used", "Pending", "Balance"])
        self.leave_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.leave_table.verticalHeader().setVisible(False)
        self.leave_table.setAlternatingRowColors(True)
        
        # Style with white text
        self.leave_table.setStyleSheet("""
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
        leave_layout.addWidget(self.leave_table)

        # Center the leave card
        leave_card_container = QHBoxLayout()
        leave_card_container.addStretch()
        leave_card_container.addWidget(leave_card)
        leave_card_container.addStretch()
        layout.addLayout(leave_card_container)

        # Benefits Information Card
        benefits_card = ShadowCard()
        benefits_card.setMinimumWidth(900)
        benefits_card.setMaximumWidth(1200)
        benefits_card.setMinimumHeight(300)
        benefits_layout = QVBoxLayout(benefits_card)
        benefits_layout.setContentsMargins(40, 40, 40, 40)

        benefits_layout.addWidget(QLabel("BENEFITS INFORMATION", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        benefits_layout.addSpacing(20)

        # Benefits grid
        benefits_grid = QHBoxLayout()
        benefits_grid.setSpacing(30)
        
        # Left column
        left_col = QVBoxLayout()
        left_col.setSpacing(15)
        self.sss_label = QLabel("SSS Number: N/A", styleSheet="font-size:14px; color:#555;")
        self.philhealth_label = QLabel("PhilHealth Number: N/A", styleSheet="font-size:14px; color:#555;")
        self.pagibig_label = QLabel("Pag-IBIG Number: N/A", styleSheet="font-size:14px; color:#555;")
        left_col.addWidget(self.sss_label)
        left_col.addWidget(self.philhealth_label)
        left_col.addWidget(self.pagibig_label)
        
        # Right column
        right_col = QVBoxLayout()
        right_col.setSpacing(15)
        self.tin_label = QLabel("TIN Number: N/A", styleSheet="font-size:14px; color:#555;")
        self.base_salary_label = QLabel("Base Salary: PHP 0.00", styleSheet="font-size:14px; color:#555;")
        self.department_label = QLabel("Department: N/A", styleSheet="font-size:14px; color:#555;")
        right_col.addWidget(self.tin_label)
        right_col.addWidget(self.base_salary_label)
        right_col.addWidget(self.department_label)
        
        benefits_grid.addLayout(left_col)
        benefits_grid.addLayout(right_col)
        benefits_grid.addStretch()
        
        benefits_layout.addLayout(benefits_grid)
        
        # Center the benefits card
        benefits_card_container = QHBoxLayout()
        benefits_card_container.addStretch()
        benefits_card_container.addWidget(benefits_card)
        benefits_card_container.addStretch()
        layout.addLayout(benefits_card_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)

        if self.employee_id:
            self._load_data()

    def _load_data(self):
        """Load leave balances and benefits data."""
        try:
            from models.database import get_connection
            from models.leave_balance_model import get_employee_leave_balances, initialize_employee_leave_balance
            from datetime import date
            
            current_year = date.today().year
            
            # Initialize leave balances if not exists
            initialize_employee_leave_balance(self.employee_id, current_year)
            
            # Get leave balances
            leave_balances = get_employee_leave_balances(self.employee_id, current_year)
            
            # Populate leave table
            self.leave_table.setRowCount(len(leave_balances))
            for row, balance in enumerate(leave_balances):
                self.leave_table.setItem(row, 0, QTableWidgetItem(balance['leave_type']))
                self.leave_table.setItem(row, 1, QTableWidgetItem(f"{float(balance['total_allocated']):.2f}"))
                self.leave_table.setItem(row, 2, QTableWidgetItem(f"{float(balance['used']):.2f}"))
                self.leave_table.setItem(row, 3, QTableWidgetItem(f"{float(balance['pending']):.2f}"))
                self.leave_table.setItem(row, 4, QTableWidgetItem(f"{float(balance['balance']):.2f}"))
            
            # Get employee benefits information
            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("""
                        SELECT 
                            e.sss_no,
                            e.philhealth_no,
                            e.pagibig_no,
                            e.tin_no,
                            e.base_salary,
                            d.name as department_name
                        FROM employees e
                        LEFT JOIN departments d ON e.department_id = d.id
                        WHERE e.id = %s
                    """, (self.employee_id,))
                    employee = cur.fetchone()
                    
                    if employee:
                        self.sss_label.setText(f"SSS Number: {employee['sss_no'] or 'N/A'}")
                        self.philhealth_label.setText(f"PhilHealth Number: {employee['philhealth_no'] or 'N/A'}")
                        self.pagibig_label.setText(f"Pag-IBIG Number: {employee['pagibig_no'] or 'N/A'}")
                        self.tin_label.setText(f"TIN Number: {employee['tin_no'] or 'N/A'}")
                        self.base_salary_label.setText(f"Base Salary: PHP {float(employee['base_salary'] or 0):,.2f}")
                        self.department_label.setText(f"Department: {employee['department_name'] or 'N/A'}")

        except Exception as e:
            logger.exception("Error loading leave/benefits data: %s", e)

    def refresh_data(self):
        """Refresh the data display."""
        if self.employee_id:
            self._load_data()

