from __future__ import annotations

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QSizePolicy,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QDateEdit,
)

# --- GLOBAL STYLES ---
# Palette chosen to match the beige/sand aesthetic of the HR Officer wireframes
STYLESHEET = """
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        color: #333333;
    }

    /* Main Background Area */
    QWidget#MainContentArea {
        background-color: #F2EBE9; /* Light Pinkish-Grey from wireframe */
    }

    /* Sidebar & Header */
    QWidget#Sidebar, QWidget#TopBar {
        background-color: #F5E6D3; /* Sand/Beige */
        border: none;
    }

    /* Cards */
    QFrame.Card {
        background-color: #FDF8F2; /* Cream/Off-white */
        border-radius: 15px;
        border: 1px solid #EBE0D6;
    }

    /* Input Fields */
    QLineEdit, QComboBox, QDateEdit {
        background-color: #FFFFFF;
        border: 2px solid #D6CDC6;
        border-radius: 8px;
        padding: 11px 15px;
        font-size: 14px;
        color: #333;
        min-height: 22px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
        border: 2px solid #F0D095;
        background-color: #FFFEF9;
    }
    QLineEdit:hover, QComboBox:hover, QDateEdit:hover {
        border: 2px solid #C0A065;
    }
    QLineEdit::placeholder {
        color: #999;
        font-style: italic;
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

    /* Sidebar buttons */
    QPushButton#SidebarBtn {
        text-align: left;
        padding: 15px 20px;
        border: none;
        background-color: transparent;
        font-weight: 600;
        font-size: 14px;
        color: #5A5A5A;
        border-left: 5px solid transparent;
    }
    QPushButton#SidebarBtn:checked {
        background-color: #E6D6C4;
        color: #333333;
        border-left: 5px solid #333333;
    }
    QPushButton#SidebarBtn:hover {
        background-color: #EBE0D0;
    }

    /* Primary buttons */
    QPushButton#SaveBtn {
        background-color: #F0D095; /* Gold/Beige Accent */
        border: 2px solid #C0A065;
        border-radius: 8px;
        padding: 12px 35px;
        font-weight: 700;
        font-size: 14px;
        color: #333;
        letter-spacing: 0.5px;
    }
    QPushButton#SaveBtn:hover { 
        background-color: #F5DCA0; 
        border: 2px solid #B89555;
    }
    QPushButton#SaveBtn:pressed {
        background-color: #E6C885;
        border: 2px solid #A88545;
    }

    QPushButton#ClearBtn {
        background-color: #FFFFFF;
        border: 2px solid #333333;
        border-radius: 8px;
        padding: 12px 35px;
        font-weight: 700;
        font-size: 14px;
        color: #333333;
        letter-spacing: 0.5px;
    }
    QPushButton#ClearBtn:hover { 
        background-color: #F8F8F8; 
        border: 2px solid #222;
    }
    QPushButton#ClearBtn:pressed {
        background-color: #EFEBE6;
        border: 2px solid #111;
    }

    /* Quick Period Selection Buttons */
    QPushButton#QuickBtn {
        background-color: #E8DFD6;
        border: 2px solid #C0A065;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 13px;
        color: #333;
    }
    QPushButton#QuickBtn:hover {
        background-color: #F0D095;
        border: 2px solid #B89555;
    }
    QPushButton#QuickBtn:pressed {
        background-color: #D6C8B6;
        border: 2px solid #A88545;
    }

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
    """Helper class to create a card with a drop shadow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card")  # For stylesheet targeting
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


import logging


logger = logging.getLogger(__name__)


class DashboardView(QWidget):
    """HR Officer dashboard matching Wireframe_page-0002."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        # Header with title and refresh button
        header_layout = QHBoxLayout()
        title = QLabel("DASHBOARD OVERVIEW")
        title.setStyleSheet(
            "font-size: 24px; font-weight: 800; color: #333; letter-spacing: 1px; margin-bottom: 5px;"
        )
        title.setGraphicsEffect(self._text_shadow())
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Add refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #C0A065;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #D6B075;
            }
            QPushButton:pressed {
                background-color: #A08050;
            }
        """)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        self.layout.addLayout(header_layout)
        self.layout.addSpacing(15)

        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(40)
        self.cards_row.setContentsMargins(0, 0, 0, 0)
        
        self._load_data()
        
        self.cards_row.addStretch()
        self.layout.addLayout(self.cards_row)
    
    def _load_data(self):
        """Load dashboard data from database."""
        try:
            from models.dashboard_model import get_hr_dashboard_stats
            stats = get_hr_dashboard_stats()
            
            total_employees_card = self._create_stat_card(
                "Total Employees", str(stats["total_employees"]), "+ 12% vs last month"
            )
            reports_card = self._create_stat_card(
                "Report Generated", str(stats["reports_generated"]), "+ 12% vs last month"
            )
            
            self.cards_row.addWidget(total_employees_card)
            self.cards_row.addWidget(reports_card)
        except Exception as e:
            # Fallback to default values if database error
            logger.exception("Error loading HR dashboard stats: %s", e)
            total_employees_card = self._create_stat_card("Total Employees", "0", "")
            reports_card = self._create_stat_card("Report Generated", "0", "")
            self.cards_row.addWidget(total_employees_card)
            self.cards_row.addWidget(reports_card)

        self.layout.addSpacing(20)

        # Recent Activities / Quick Stats Section
        large_card = ShadowCard()
        large_card.setMinimumHeight(320)
        large_card_layout = QVBoxLayout(large_card)
        large_card_layout.setContentsMargins(40, 30, 40, 30)
        large_card_layout.setSpacing(15)
        
        # Section title
        section_title = QLabel("RECENT ACTIVITIES & QUICK STATS")
        section_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #333; letter-spacing: 0.5px;")
        large_card_layout.addWidget(section_title)
        large_card_layout.addSpacing(10)
        
        # Load recent activities
        self._load_recent_activities(large_card_layout)
        
        large_card_layout.addStretch()
        self.layout.addWidget(large_card)
        self.layout.addStretch()
    
    def _load_recent_activities(self, layout):
        """Load recent activities and quick stats."""
        try:
            from models.database import get_connection
            from datetime import date, timedelta
            
            # Get employee and payroll statistics
            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cur:
                    # Recent employees (hired in last 30 days based on date_hired)
                    thirty_days_ago = date.today() - timedelta(days=30)
                    cur.execute("""
                        SELECT COUNT(*) as count 
                        FROM employees 
                        WHERE date_hired >= %s AND is_active = 1
                    """, (thirty_days_ago,))
                    recent_emp = cur.fetchone()
                    new_employees = recent_emp['count'] if recent_emp else 0
                    
                    # Total active employees
                    cur.execute("SELECT COUNT(*) as count FROM employees WHERE is_active = 1")
                    active_result = cur.fetchone()
                    active_employees = active_result['count'] if active_result else 0
                    
                    # Departments count
                    cur.execute("SELECT COUNT(*) as count FROM departments")
                    dept_result = cur.fetchone()
                    departments = dept_result['count'] if dept_result else 0
                    
                    # Total payroll periods
                    cur.execute("SELECT COUNT(*) as count FROM payroll_periods")
                    payroll_result = cur.fetchone()
                    total_periods = payroll_result['count'] if payroll_result else 0
            
            # Display stats in a grid with proper column sizing
            grid = QGridLayout()
            grid.setSpacing(20)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 1)
            
            # Row 1
            self._add_stat_item(grid, 0, 0, "👥 Active Employees", str(active_employees))
            self._add_stat_item(grid, 0, 1, "🏢 Departments", str(departments))
            
            # Row 2
            self._add_stat_item(grid, 1, 0, "✨ New This Month", str(new_employees))
            self._add_stat_item(grid, 1, 1, "💰 Payroll Periods", str(total_periods))
            
            layout.addLayout(grid)
            
        except Exception as e:
            logger.exception("Error loading recent activities: %s", e)
            error_label = QLabel("Unable to load recent activities")
            error_label.setStyleSheet("color: #999; font-size: 13px; font-style: italic;")
            layout.addWidget(error_label)
    
    def _add_stat_item(self, grid, row, col, label_text, value_text):
        """Add a stat item to the grid."""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #F5F3F0;
                border-radius: 8px;
            }
        """)
        container.setMinimumHeight(100)
        
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(25, 20, 25, 20)
        v_layout.setSpacing(10)
        
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 13px; color: #666; font-weight: 600;")
        label.setWordWrap(True)
        
        value = QLabel(value_text)
        value.setStyleSheet("font-size: 28px; color: #333; font-weight: 800;")
        value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        value.setMinimumHeight(40)
        value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        v_layout.addWidget(label)
        v_layout.addWidget(value)
        v_layout.addStretch()
        
        grid.addWidget(container, row, col, 1, 1)
    
    def refresh_data(self):
        """Refresh dashboard data by clearing and reloading all content."""
        # Clear the entire layout except title
        while self.layout.count() > 2:  # Keep title and spacing
            item = self.layout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        
        # Recreate cards row
        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(40)
        self.cards_row.setContentsMargins(0, 0, 0, 0)
        
        # Reload all data
        self._load_data()
        self.cards_row.addStretch()
        self.layout.addLayout(self.cards_row)
    
    def _clear_layout(self, layout):
        """Helper to clear a layout recursively."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _text_shadow(self) -> QGraphicsDropShadowEffect:
        """Create text shadow effect for titles."""
        eff = QGraphicsDropShadowEffect()
        eff.setBlurRadius(5)
        eff.setColor(QColor(0, 0, 0, 50))
        eff.setOffset(1, 1)
        return eff

    def _create_stat_card(self, title_text: str, count_text: str, sub_text: str) -> QWidget:
        card = ShadowCard()
        card.setFixedSize(280, 180)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(25, 25, 25, 25)
        cl.setSpacing(8)

        icon_box = QLabel()
        icon_box.setFixedSize(42, 42)
        icon_box.setStyleSheet("""
            background-color: #F0D095;
            border-radius: 6px;
            qproperty-alignment: AlignCenter;
            font-size: 20px;
        """)

        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet("font-size: 13px; color: #666; font-weight: 600; letter-spacing: 0.3px;")
        title_lbl.setWordWrap(False)

        count_lbl = QLabel(count_text)
        count_lbl.setStyleSheet("font-size: 36px; font-weight: 900; color: #333; letter-spacing: -1px;")
        count_lbl.setWordWrap(False)

        sub_lbl = QLabel(sub_text)
        if sub_text:
            sub_lbl.setStyleSheet(
                "font-size: 12px; font-weight: 600; color: #6BA855; padding-top: 3px;"
            )
            sub_lbl.setWordWrap(False)
        else:
            sub_lbl.setVisible(False)

        cl.addWidget(icon_box)
        cl.addSpacing(6)
        cl.addWidget(title_lbl)
        cl.addSpacing(2)
        cl.addWidget(count_lbl)
        if sub_text:
            cl.addWidget(sub_lbl)
        cl.addStretch()

        return card


class RegistrationView(QWidget):
    """Employee Registration form matching Wireframe_page-0003."""

    def __init__(self):
        super().__init__()
        # Use scroll area to ensure all content is visible
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(40, 20, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        form_card = ShadowCard()
        form_card.setFixedWidth(720)
        form_card.setMinimumHeight(900)  # Increased to accommodate user account section

        fc_layout = QVBoxLayout(form_card)
        fc_layout.setContentsMargins(50, 30, 50, 30)
        fc_layout.setSpacing(0)

        h1 = QLabel("EMPLOYEE INFORMATION")
        h1.setStyleSheet(
            "font-size: 20px; font-weight: 800; color: #333; margin-bottom: 8px; letter-spacing: 0.5px;"
        )
        h1.setGraphicsEffect(self._text_shadow())
        fc_layout.addWidget(h1)
        fc_layout.addSpacing(10)

        grid1 = QGridLayout()
        grid1.setVerticalSpacing(8)
        grid1.setHorizontalSpacing(25)
        grid1.setColumnMinimumWidth(0, 160)
        grid1.setColumnStretch(1, 1)

        # Employee ID
        self.employee_id_edit = QLineEdit()
        self.employee_id_edit.setPlaceholderText("Enter employee ID (e.g., EMP001)")
        self.employee_id_edit.setFixedHeight(38)
        self._add_row(grid1, 0, "Employee ID :", self.employee_id_edit)
        
        # First Name
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Enter first name")
        self.first_name_edit.setFixedHeight(38)
        self._add_row(grid1, 1, "First Name :", self.first_name_edit)
        
        # Last Name
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Enter last name")
        self.last_name_edit.setFixedHeight(38)
        self._add_row(grid1, 2, "Last Name :", self.last_name_edit)
        
        # Position
        self.position_edit = QLineEdit()
        self.position_edit.setPlaceholderText("Enter position/title")
        self.position_edit.setFixedHeight(38)
        self._add_row(grid1, 3, "Position :", self.position_edit)

        # Department
        self.dept_combo = QComboBox()
        self.dept_combo.addItem("Select Department")
        self.dept_combo.setPlaceholderText("Select Department")
        self.dept_combo.setFixedHeight(38)
        self._load_departments()
        self._add_row(grid1, 4, "Department :", self.dept_combo)
        
        # Date Hired
        self.date_hired_edit = QDateEdit()
        self.date_hired_edit.setDisplayFormat("dd / MM / yyyy")
        self.date_hired_edit.setCalendarPopup(True)
        self.date_hired_edit.setFixedHeight(38)
        from PyQt6.QtCore import QDate
        self.date_hired_edit.setDate(QDate.currentDate())
        # Remove date restrictions - allow any date
        self.date_hired_edit.setMinimumDate(QDate(1900, 1, 1))
        self.date_hired_edit.setMaximumDate(QDate(2100, 12, 31))
        self._add_row(grid1, 5, "Date Hired :", self.date_hired_edit)

        fc_layout.addLayout(grid1)
        fc_layout.addSpacing(18)

        h2 = QLabel("Government IDs")
        h2.setStyleSheet(
            "font-size: 20px; font-weight: 800; color: #333; margin-bottom: 8px; letter-spacing: 0.5px;"
        )
        h2.setGraphicsEffect(self._text_shadow())
        fc_layout.addWidget(h2)
        fc_layout.addSpacing(10)

        grid2 = QGridLayout()
        grid2.setVerticalSpacing(8)
        grid2.setHorizontalSpacing(25)
        grid2.setColumnMinimumWidth(0, 160)
        grid2.setColumnStretch(1, 1)

        # SSS
        self.sss_edit = QLineEdit()
        self.sss_edit.setPlaceholderText("Enter SSS number")
        self.sss_edit.setFixedHeight(38)
        self._add_row(grid2, 0, "SSS :", self.sss_edit)
        
        # PhilHealth
        self.philhealth_edit = QLineEdit()
        self.philhealth_edit.setPlaceholderText("Enter PhilHealth number")
        self.philhealth_edit.setFixedHeight(38)
        self._add_row(grid2, 1, "PhilHealth :", self.philhealth_edit)
        
        # Pag-IBIG
        self.pagibig_edit = QLineEdit()
        self.pagibig_edit.setPlaceholderText("Enter Pag-IBIG number")
        self.pagibig_edit.setFixedHeight(38)
        self._add_row(grid2, 2, "Pag-IBIG :", self.pagibig_edit)
        
        # TIN
        self.tin_edit = QLineEdit()
        self.tin_edit.setPlaceholderText("Enter TIN number")
        self.tin_edit.setFixedHeight(38)
        self._add_row(grid2, 3, "TIN :", self.tin_edit)

        fc_layout.addLayout(grid2)
        fc_layout.addSpacing(20)
        
        # Salary Type and Rate fields
        salary_type_row = QHBoxLayout()
        salary_type_label = QLabel("Salary Type :")
        salary_type_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        salary_type_label.setStyleSheet("color: #555; font-weight: 600; font-size: 14px; padding-right: 10px;")
        
        self.salary_type_combo = QComboBox()
        self.salary_type_combo.addItems(["MONTHLY", "HOURLY", "DAILY"])
        self.salary_type_combo.setMinimumHeight(38)
        self.salary_type_combo.currentTextChanged.connect(self._on_salary_type_changed)
        
        salary_type_row.addWidget(salary_type_label)
        salary_type_row.addWidget(self.salary_type_combo)
        salary_type_row.addStretch()
        
        fc_layout.addLayout(salary_type_row)
        fc_layout.addSpacing(15)
        
        # Base Salary field
        salary_row = QHBoxLayout()
        salary_label = QLabel("Base Salary (PHP) :")
        salary_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        salary_label.setStyleSheet("color: #555; font-weight: 600; font-size: 14px; padding-right: 10px;")
        
        self.salary_edit = QLineEdit()
        self.salary_edit.setPlaceholderText("Enter base salary (e.g., 25000)")
        self.salary_edit.setMinimumHeight(38)
        self.salary_edit.textChanged.connect(self._on_salary_type_changed)
        
        salary_row.addWidget(salary_label)
        salary_row.addWidget(self.salary_edit)
        salary_row.addStretch()
        
        fc_layout.addLayout(salary_row)
        fc_layout.addSpacing(15)
        
        # Hourly Rate field (auto-calculated or manual entry)
        hourly_rate_row = QHBoxLayout()
        hourly_rate_label = QLabel("Hourly Rate (PHP) :")
        hourly_rate_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        hourly_rate_label.setStyleSheet("color: #555; font-weight: 600; font-size: 14px; padding-right: 10px;")
        
        self.hourly_rate_edit = QLineEdit()
        self.hourly_rate_edit.setPlaceholderText("Auto-calculated or enter manually")
        self.hourly_rate_edit.setMinimumHeight(38)
        self.hourly_rate_edit.setReadOnly(True)  # Auto-calculated by default
        
        hourly_rate_row.addWidget(hourly_rate_label)
        hourly_rate_row.addWidget(self.hourly_rate_edit)
        hourly_rate_row.addStretch()
        
        fc_layout.addLayout(hourly_rate_row)
        fc_layout.addSpacing(20)
        
        # User Account Creation Section
        user_account_frame = QFrame()
        user_account_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F6F4;
                border: 2px solid #E8E0DC;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        user_account_layout = QVBoxLayout(user_account_frame)
        user_account_layout.setContentsMargins(15, 15, 15, 15)
        user_account_layout.setSpacing(12)
        
        user_account_title = QLabel("User Account Creation")
        user_account_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #333;")
        user_account_layout.addWidget(user_account_title)
        
        # Checkbox to create user account
        self.create_user_checkbox = QCheckBox("Create user account for this employee")
        self.create_user_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: 600;
                color: #555;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.create_user_checkbox.setChecked(True)  # Default to checked
        self.create_user_checkbox.stateChanged.connect(self._on_user_account_checkbox_changed)
        user_account_layout.addWidget(self.create_user_checkbox)
        
        # Username field (defaults to employee code)
        username_row = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: #555; font-weight: 600; font-size: 13px; min-width: 100px;")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Will use Employee Code by default")
        self.username_edit.setMinimumHeight(35)
        self.username_edit.setEnabled(True)  # Enabled when checkbox is checked
        username_row.addWidget(username_label)
        username_row.addWidget(self.username_edit)
        user_account_layout.addLayout(username_row)
        
        # Password field (default password)
        password_row = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #555; font-weight: 600; font-size: 13px; min-width: 100px;")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Default: emp123 (employee should change on first login)")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(35)
        self.password_edit.setText("emp123")  # Default password
        self.password_edit.setEnabled(True)  # Enabled when checkbox is checked
        password_row.addWidget(password_label)
        password_row.addWidget(self.password_edit)
        user_account_layout.addLayout(password_row)
        
        info_label = QLabel("ℹ️ User account will be created with 'Employee' role. Employee can log in immediately.")
        info_label.setStyleSheet("font-size: 12px; color: #666; font-style: italic; padding-top: 5px;")
        info_label.setWordWrap(True)
        user_account_layout.addWidget(info_label)
        
        fc_layout.addWidget(user_account_frame)
        fc_layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.save_btn = QPushButton("SAVE")
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setMinimumWidth(140)
        self.save_btn.setMinimumHeight(42)

        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setObjectName("ClearBtn")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setMinimumWidth(140)
        self.clear_btn.setMinimumHeight(42)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()

        fc_layout.addLayout(btn_layout)
        layout.addWidget(form_card)
        layout.addStretch()
        
        # Set up scroll area and add to main widget
        scroll.setWidget(scroll_content)
        
        # Replace the main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Connect buttons and signals
        self.save_btn.clicked.connect(self._save_employee)
        self.clear_btn.clicked.connect(self._clear_form)
        # Auto-update username when employee code changes
        self.employee_id_edit.textChanged.connect(self._on_employee_code_changed)
    
    def _on_employee_code_changed(self):
        """Update username field when employee code changes."""
        if self.create_user_checkbox.isChecked() and not self.username_edit.text().strip():
            employee_code = self.employee_id_edit.text().strip()
            if employee_code:
                self.username_edit.setText(employee_code)
    
    def _save_employee(self):
        """Save employee data to database with comprehensive validation."""
        try:
            from models.employee_model import create_employee
            from models.audit_model import log_audit
            from models.validation_model import (
                validate_employee_code, validate_name, validate_salary,
                validate_government_id, validate_date
            )
            from models.integration_model import log_integration
            from PyQt6.QtWidgets import QMessageBox
            
            # Comprehensive validation
            employee_code = self.employee_id_edit.text().strip()
            first_name = self.first_name_edit.text().strip()
            last_name = self.last_name_edit.text().strip()
            
            # Validate employee code
            code_valid, code_error = validate_employee_code(employee_code)
            if not code_valid:
                QMessageBox.warning(self, "Validation Error", code_error)
                return
            
            # Validate names
            first_valid, first_error = validate_name(first_name, "First Name")
            if not first_valid:
                QMessageBox.warning(self, "Validation Error", first_error)
                return
            
            last_valid, last_error = validate_name(last_name, "Last Name")
            if not last_valid:
                QMessageBox.warning(self, "Validation Error", last_error)
                return
            
            # Validate government IDs
            sss_no = self.sss_edit.text().strip()
            if sss_no:
                sss_valid, sss_error = validate_government_id(sss_no, "SSS")
                if not sss_valid:
                    QMessageBox.warning(self, "Validation Error", sss_error)
                    return
            
            philhealth_no = self.philhealth_edit.text().strip()
            if philhealth_no:
                ph_valid, ph_error = validate_government_id(philhealth_no, "PhilHealth")
                if not ph_valid:
                    QMessageBox.warning(self, "Validation Error", ph_error)
                    return
            
            pagibig_no = self.pagibig_edit.text().strip()
            if pagibig_no:
                pag_valid, pag_error = validate_government_id(pagibig_no, "Pag-IBIG")
                if not pag_valid:
                    QMessageBox.warning(self, "Validation Error", pag_error)
                    return
            
            tin_no = self.tin_edit.text().strip()
            if tin_no:
                tin_valid, tin_error = validate_government_id(tin_no, "TIN")
                if not tin_valid:
                    QMessageBox.warning(self, "Validation Error", tin_error)
                    return
            
            # Validate date hired
            if self.date_hired_edit.date().isValid():
                date_hired = self.date_hired_edit.date().toPyDate()
                date_valid, date_error = validate_date(date_hired, "Date Hired", allow_future=False)
                if not date_valid:
                    QMessageBox.warning(self, "Validation Error", date_error)
                    return
            
            # Get department ID
            dept_id = self.dept_combo.currentData()
            if not dept_id or self.dept_combo.currentText() == "Select Department":
                QMessageBox.warning(self, "Validation Error", "Please select a department.")
                return
            
            # Validate and get salary
            salary_text = self.salary_edit.text().strip()
            base_salary = 0.0
            if salary_text:
                try:
                    base_salary = float(salary_text)
                    if base_salary < 0:
                        QMessageBox.warning(self, "Validation Error", "Salary cannot be negative.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Validation Error", "Please enter a valid salary amount.")
                    return
            
            # Get salary type
            salary_type = self.salary_type_combo.currentText()
            
            # Get hourly rate (auto-calculated or manual)
            hourly_rate = 0.0
            hourly_rate_text = self.hourly_rate_edit.text().strip()
            if hourly_rate_text:
                try:
                    hourly_rate = float(hourly_rate_text)
                    if hourly_rate < 0:
                        QMessageBox.warning(self, "Validation Error", "Hourly rate cannot be negative.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Validation Error", "Please enter a valid hourly rate.")
                    return
            else:
                # Auto-calculate hourly rate if not provided
                if base_salary > 0:
                    if salary_type == 'HOURLY':
                        hourly_rate = base_salary
                    elif salary_type == 'DAILY':
                        hourly_rate = base_salary / 8.0
                    elif salary_type == 'MONTHLY':
                        hourly_rate = base_salary / 176.0  # 22 days * 8 hours
            
            # Prepare employee data
            employee_data = {
                "employee_code": self.employee_id_edit.text().strip(),
                "first_name": self.first_name_edit.text().strip(),
                "last_name": self.last_name_edit.text().strip(),
                "position": self.position_edit.text().strip() or None,
                "department_id": dept_id,
                "date_hired": self.date_hired_edit.date().toPyDate().isoformat() if self.date_hired_edit.date().isValid() else None,
                "sss_no": self.sss_edit.text().strip() or None,
                "philhealth_no": self.philhealth_edit.text().strip() or None,
                "pagibig_no": self.pagibig_edit.text().strip() or None,
                "tin_no": self.tin_edit.text().strip() or None,
                "base_salary": base_salary,
                "hourly_rate": hourly_rate,
                "salary_type": salary_type,
            }
            
            # Create employee
            employee_id = create_employee(employee_data)
            
            # Log audit
            log_audit(None, "Create", f"Created employee: {employee_data['employee_code']}")
            
            # Create user account if checkbox is checked
            user_created = False
            if self.create_user_checkbox.isChecked():
                username = self.username_edit.text().strip()
                password = self.password_edit.text().strip()
                
                # Use employee code as username if username is empty
                if not username:
                    username = employee_code
                
                # Use default password if empty
                if not password:
                    password = "emp123"
                
                # Validate username
                if len(username) < 3:
                    QMessageBox.warning(self, "Validation Error", "Username must be at least 3 characters.")
                    return
                
                # Create user account
                try:
                    from models.database import get_connection
                    from utils.security import hash_password
                    
                    # Get Employee role ID
                    with get_connection() as conn:
                        with conn.cursor(dictionary=True) as cur:
                            # Get Employee role ID
                            cur.execute("SELECT id FROM roles WHERE name = 'Employee'")
                            role_result = cur.fetchone()
                            if not role_result:
                                QMessageBox.warning(self, "Error", "Employee role not found in system.")
                                return
                            role_id = role_result['id']
                            
                            # Check if username already exists
                            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                            if cur.fetchone():
                                QMessageBox.warning(self, "Validation Error", 
                                    f"Username '{username}' already exists. Please choose a different username.")
                                return
                            
                            # Hash password
                            password_hash = hash_password(password)
                            
                            # Create user
                            cur.execute(
                                """INSERT INTO users (username, password_hash, role_id, is_active) 
                                   VALUES (%s, %s, %s, 1)""",
                                (username, password_hash, role_id)
                            )
                            user_id = cur.lastrowid
                            conn.commit()
                            
                            # Log audit
                            log_audit(None, "Create User", 
                                f"Created user account for employee {employee_code}: username={username}")
                            
                            user_created = True
                except Exception as e:
                    QMessageBox.warning(self, "User Creation Error", 
                        f"Employee was created successfully, but user account creation failed: {str(e)}\n\n"
                        f"You can create the user account manually in Admin → User Management.")
                    import traceback
                    traceback.print_exc()
            
            # Log integration activity (Solution 2: Centralized Data Integration)
            from models.integration_model import log_integration
            log_integration(
                source_system='HR_SYSTEM',
                target_system='PAYROLL_SYSTEM',
                integration_type='EMPLOYEE_UPDATE',
                record_type='EMPLOYEE',
                action='CREATE',
                status='SUCCESS',
                record_id=str(employee_id),
                details=f"Created employee: {employee_code} - {first_name} {last_name}"
            )
            
            # Success message
            success_msg = f"Employee {employee_data['employee_code']} has been registered successfully!"
            if user_created:
                username_used = self.username_edit.text().strip() or employee_code
                success_msg += f"\n\n✅ User account created:\n"
                success_msg += f"   Username: {username_used}\n"
                success_msg += f"   Password: {self.password_edit.text()}\n"
                success_msg += f"   Role: Employee\n\n"
                success_msg += f"Employee can now log in to access their account."
            
            QMessageBox.information(self, "Success", success_msg)
            self._clear_form()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to save employee: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _clear_form(self):
        """Clear all form fields."""
        from PyQt6.QtCore import QDate
        self.employee_id_edit.clear()
        self.first_name_edit.clear()
        self.last_name_edit.clear()
        self.position_edit.clear()
        self.dept_combo.setCurrentIndex(0)
        self.date_hired_edit.setDate(QDate.currentDate())
        self.sss_edit.clear()
        self.philhealth_edit.clear()
        self.pagibig_edit.clear()
        self.tin_edit.clear()
        self.salary_edit.clear()
        self.salary_type_combo.setCurrentIndex(0)
        self.hourly_rate_edit.clear()
        # Reset user account fields
        self.create_user_checkbox.setChecked(True)
        self.username_edit.clear()
        self.password_edit.setText("emp123")
        self._on_user_account_checkbox_changed()
    
    def _on_user_account_checkbox_changed(self):
        """Handle user account checkbox state change."""
        is_checked = self.create_user_checkbox.isChecked()
        self.username_edit.setEnabled(is_checked)
        self.password_edit.setEnabled(is_checked)
        
        # Auto-fill username with employee code if available
        if is_checked:
            employee_code = self.employee_id_edit.text().strip()
            if employee_code and not self.username_edit.text().strip():
                self.username_edit.setText(employee_code)
        else:
            # Clear fields when unchecked
            self.username_edit.clear()
            self.password_edit.setText("emp123")
    
    def _on_salary_type_changed(self):
        """Recalculate hourly rate when salary type changes."""
        try:
            salary_text = self.salary_edit.text().strip()
            if salary_text:
                base_salary = float(salary_text)
                salary_type = self.salary_type_combo.currentText()
                
                if salary_type == 'HOURLY':
                    hourly_rate = base_salary
                elif salary_type == 'DAILY':
                    hourly_rate = base_salary / 8.0
                elif salary_type == 'MONTHLY':
                    hourly_rate = base_salary / 176.0
                else:
                    hourly_rate = 0.0
                
                self.hourly_rate_edit.setText(f"{hourly_rate:.2f}")
        except ValueError:
            self.hourly_rate_edit.clear()
    
    def _load_departments(self):
        """Load departments from database."""
        try:
            from models.user_management_model import get_departments
            departments = get_departments()
            for dept in departments:
                self.dept_combo.addItem(dept["name"], dept["id"])
        except Exception:
            # Fallback to default departments
            self.dept_combo.addItems(["IT", "HR", "Sales"])

    def _add_row(self, layout: QGridLayout, row: int, label_text: str, widget: QWidget) -> QWidget:
        lbl = QLabel(label_text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl.setStyleSheet("color: #555; font-weight: 600; font-size: 14px; padding-right: 15px;")
        layout.addWidget(lbl, row, 0)
        layout.addWidget(widget, row, 1)
        
        return widget

    def _text_shadow(self) -> QGraphicsDropShadowEffect:
        eff = QGraphicsDropShadowEffect()
        eff.setBlurRadius(5)
        eff.setColor(QColor(0, 0, 0, 50))
        eff.setOffset(1, 1)
        return eff


class ReportsView(QWidget):
    """Report Generator view matching Wireframe_page-0004."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(20)

        # Filter Card - Fixed height to prevent collapse
        filter_card = ShadowCard()
        filter_card.setMinimumWidth(900)
        filter_card.setMaximumWidth(1200)
        filter_card.setFixedHeight(380)  # Fixed height to maintain layout

        cl = QVBoxLayout(filter_card)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(15)

        title = QLabel("Report Generator")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #333; letter-spacing: 0.5px;")
        eff = QGraphicsDropShadowEffect()
        eff.setBlurRadius(5)
        eff.setColor(QColor(0, 0, 0, 50))
        eff.setOffset(1, 1)
        title.setGraphicsEffect(eff)
        cl.addWidget(title)

        cl.addSpacing(10)

        grid = QGridLayout()
        grid.setVerticalSpacing(15)
        grid.setHorizontalSpacing(20)
        grid.setColumnMinimumWidth(0, 150)
        grid.setColumnStretch(1, 1)

        # Report Type
        self.cb_type = QComboBox()
        self.cb_type.setStyleSheet("""
            QComboBox {
                color: #333333;
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                color: #333333;
                background-color: #FFFFFF;
                selection-background-color: #F0D095;
                selection-color: #333333;
            }
        """)
        self.cb_type.addItems(["Select Report Type", "Attendance", "Payroll", "Performance", "Total Payroll Summary"])
        self._add_row(grid, 0, "Report Type :", self.cb_type)

        # Quick Period Selection Buttons
        period_layout = QHBoxLayout()
        period_layout.setSpacing(8)
        
        self.btn_today = QPushButton("Today")
        self.btn_today.setObjectName("QuickBtn")
        self.btn_today.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_today.setFixedHeight(32)
        self.btn_today.setFixedWidth(100)
        self.btn_today.clicked.connect(self._set_today_range)
        
        self.btn_this_week = QPushButton("This Week")
        self.btn_this_week.setObjectName("QuickBtn")
        self.btn_this_week.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_this_week.setFixedHeight(32)
        self.btn_this_week.setFixedWidth(100)
        self.btn_this_week.clicked.connect(self._set_this_week_range)
        
        self.btn_this_month = QPushButton("This Month")
        self.btn_this_month.setObjectName("QuickBtn")
        self.btn_this_month.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_this_month.setFixedHeight(32)
        self.btn_this_month.setFixedWidth(110)
        self.btn_this_month.clicked.connect(self._set_this_month_range)
        
        self.btn_last_month = QPushButton("Last Month")
        self.btn_last_month.setObjectName("QuickBtn")
        self.btn_last_month.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_last_month.setFixedHeight(32)
        self.btn_last_month.setFixedWidth(110)
        self.btn_last_month.clicked.connect(self._set_last_month_range)
        
        period_layout.addWidget(self.btn_today)
        period_layout.addWidget(self.btn_this_week)
        period_layout.addWidget(self.btn_this_month)
        period_layout.addWidget(self.btn_last_month)
        period_layout.addStretch()
        
        lbl_quick = QLabel("Quick Period :")
        lbl_quick.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_quick.setStyleSheet("color: #555; font-weight: 600; font-size: 13px; padding-right: 10px;")
        
        grid.addWidget(lbl_quick, 1, 0)
        grid.addLayout(period_layout, 1, 1)

        # Date Range
        range_layout = QHBoxLayout()
        range_layout.setSpacing(10)
        
        self.date_start = QDateEdit()
        self.date_start.setDisplayFormat("dd / MM / yyyy")
        self.date_start.setCalendarPopup(True)
        from PyQt6.QtCore import QDate
        self.date_start.setDate(QDate.currentDate().addMonths(-1))
        self.date_start.setFixedHeight(38)
        self.date_start.setMinimumWidth(150)
        # Remove date restrictions
        self.date_start.setMinimumDate(QDate(1900, 1, 1))
        self.date_start.setMaximumDate(QDate(2100, 12, 31))
        
        self.date_end = QDateEdit()
        self.date_end.setDisplayFormat("dd / MM / yyyy")
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setFixedHeight(38)
        self.date_end.setMinimumWidth(150)
        # Remove date restrictions
        self.date_end.setMinimumDate(QDate(1900, 1, 1))
        self.date_end.setMaximumDate(QDate(2100, 12, 31))
        
        lbl_to = QLabel("to")
        lbl_to.setStyleSheet("color: #666; font-weight: 500; font-size: 14px; padding: 0 5px;")

        range_layout.addWidget(self.date_start)
        range_layout.addWidget(lbl_to)
        range_layout.addWidget(self.date_end)
        range_layout.addStretch()

        lbl_range = QLabel("Date Range :")
        lbl_range.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_range.setStyleSheet("color: #555; font-weight: 600; font-size: 13px; padding-right: 10px;")

        grid.addWidget(lbl_range, 2, 0)
        grid.addLayout(range_layout, 2, 1)

        # Department
        self.cb_dept = QComboBox()
        self.cb_dept.setStyleSheet("""
            QComboBox {
                color: #333333;
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                color: #333333;
                background-color: #FFFFFF;
                selection-background-color: #F0D095;
                selection-color: #333333;
            }
        """)
        self.cb_dept.addItem("All Departments")
        self._load_departments_for_reports(self.cb_dept)
        self._add_row(grid, 3, "Department :", self.cb_dept)

        cl.addLayout(grid)
        cl.addSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_gen = QPushButton("GENERATE REPORT")
        self.btn_gen.setObjectName("SaveBtn")
        self.btn_gen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gen.setFixedWidth(180)
        self.btn_gen.setFixedHeight(40)
        self.btn_gen.clicked.connect(self._generate_report)
        
        self.btn_export_pdf = QPushButton("📄 EXPORT TO PDF")
        self.btn_export_pdf.setObjectName("SaveBtn")
        self.btn_export_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_pdf.setFixedWidth(180)
        self.btn_export_pdf.setFixedHeight(40)
        self.btn_export_pdf.clicked.connect(self._export_to_pdf)
        self.btn_export_pdf.setEnabled(False)  # Disabled until report is generated
        
        btn_row.addWidget(self.btn_gen)
        btn_row.addSpacing(15)
        btn_row.addWidget(self.btn_export_pdf)
        btn_row.addStretch()

        cl.addLayout(btn_row)
        
        # Add the filter card to main layout with proper alignment
        filter_layout = QHBoxLayout()
        filter_layout.addStretch()
        filter_layout.addWidget(filter_card)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        layout.addSpacing(20)
        
        # Report Display Area - Improved sizing for better responsiveness
        from PyQt6.QtWidgets import QScrollArea, QTableWidget, QHeaderView
        
        # Create a card for the table to match filter card styling
        self.report_card = ShadowCard()
        self.report_card.setMinimumWidth(900)
        self.report_card.setMaximumWidth(1200)
        self.report_card.setMinimumHeight(400)
        
        report_card_layout = QVBoxLayout(self.report_card)
        report_card_layout.setContentsMargins(20, 20, 20, 20)
        report_card_layout.setSpacing(0)
        
        self.report_scroll = QScrollArea()
        self.report_scroll.setWidgetResizable(True)
        self.report_scroll.setMinimumHeight(350)
        self.report_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        self.report_table = QTableWidget()
        self.report_table.setAlternatingRowColors(True)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.verticalHeader().setVisible(False)
        
        # Style the table with white text
        self.report_table.setStyleSheet("""
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
        
        self.report_scroll.setWidget(self.report_table)
        report_card_layout.addWidget(self.report_scroll)
        
        self.report_card.setVisible(False)  # Hidden until report is generated
        
        # Center the report card same as filter card
        report_card_container = QHBoxLayout()
        report_card_container.addStretch()
        report_card_container.addWidget(self.report_card)
        report_card_container.addStretch()
        layout.addLayout(report_card_container)
        
        self.report_data = None  # Store report data for PDF export
    
    def _set_today_range(self):
        """Set date range to today."""
        from PyQt6.QtCore import QDate
        today = QDate.currentDate()
        self.date_start.setDate(today)
        self.date_end.setDate(today)
    
    def _set_this_week_range(self):
        """Set date range to this week (Monday to Sunday)."""
        from PyQt6.QtCore import QDate
        today = QDate.currentDate()
        # Get Monday of current week
        day_of_week = today.dayOfWeek()  # 1 = Monday, 7 = Sunday
        monday = today.addDays(1 - day_of_week)
        sunday = monday.addDays(6)
        self.date_start.setDate(monday)
        self.date_end.setDate(sunday)
    
    def _set_this_month_range(self):
        """Set date range to this month."""
        from PyQt6.QtCore import QDate
        today = QDate.currentDate()
        first_day = QDate(today.year(), today.month(), 1)
        last_day = QDate(today.year(), today.month(), today.daysInMonth())
        self.date_start.setDate(first_day)
        self.date_end.setDate(last_day)
    
    def _set_last_month_range(self):
        """Set date range to last month."""
        from PyQt6.QtCore import QDate
        today = QDate.currentDate()
        first_day_this_month = QDate(today.year(), today.month(), 1)
        last_day_last_month = first_day_this_month.addDays(-1)
        first_day_last_month = QDate(last_day_last_month.year(), last_day_last_month.month(), 1)
        self.date_start.setDate(first_day_last_month)
        self.date_end.setDate(last_day_last_month)
    
    def _load_departments_for_reports(self, combo: QComboBox):
        """Load departments from database for reports."""
        try:
            from models.user_management_model import get_departments
            departments = get_departments()
            for dept in departments:
                combo.addItem(dept["name"])
        except Exception:
            combo.addItems(["IT", "HR"])
    
    def _generate_report(self):
        """Generate report based on selected criteria."""
        try:
            from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
            from models.audit_model import log_audit
            from models.report_model import get_attendance_report, get_payroll_report, get_performance_report
            from models.user_management_model import get_departments
            
            report_type = self.cb_type.currentText()
            if report_type == "Select Report Type":
                QMessageBox.warning(self, "Validation Error", "Please select a report type.")
                return
            
            start_date = self.date_start.date().toPyDate()
            end_date = self.date_end.date().toPyDate()
            
            if start_date > end_date:
                QMessageBox.warning(self, "Validation Error", "Start date must be before or equal to end date.")
                return
            
            department = self.cb_dept.currentText()
            dept_id = None
            if department != "All Departments":
                depts = get_departments()
                for d in depts:
                    if d["name"] == department:
                        dept_id = d["id"]
                        break
            
            # Generate report based on type
            if report_type == "Attendance":
                self.report_data = get_attendance_report(start_date, end_date, dept_id)
                self._display_attendance_report()
            elif report_type == "Payroll":
                self.report_data = get_payroll_report(start_date, end_date, dept_id)
                self._display_payroll_report()
            elif report_type == "Performance":
                self.report_data = get_performance_report(start_date, end_date, dept_id)
                self._display_performance_report()
            elif report_type == "Total Payroll Summary":
                self._display_total_payroll_summary(start_date, end_date)
            
            # Show report area and enable PDF export
            self.report_card.setVisible(True)
            self.btn_export_pdf.setEnabled(True)
            
            # Log the report generation
            log_audit(None, "Generate Report", f"Generated {report_type} report for {department} from {start_date} to {end_date} ({len(self.report_data)} records)")
            
            QMessageBox.information(
                self, 
                "Report Generated", 
                f"{report_type} report has been generated successfully!\n\n"
                f"Department: {department}\n"
                f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n"
                f"Records: {len(self.report_data)}"
            )
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _display_attendance_report(self):
        """Display attendance report in table."""
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        
        if not self.report_data:
            # Show empty table with headers
            headers = ["Employee Code", "Name", "Department", "Date", "Time In", "Time Out", "Hours", "Status", "Late (min)", "Undertime (min)"]
            self.report_table.setColumnCount(len(headers))
            self.report_table.setHorizontalHeaderLabels(headers)
            self.report_table.setRowCount(0)
            return
        
        headers = ["Employee Code", "Name", "Department", "Date", "Time In", "Time Out", "Hours", "Status", "Late (min)", "Undertime (min)"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.setRowCount(len(self.report_data))
        
        for row, record in enumerate(self.report_data):
            self.report_table.setItem(row, 0, QTableWidgetItem(str(record.get('employee_code', 'N/A'))))
            name = f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()
            if not name:
                name = 'N/A'
            self.report_table.setItem(row, 1, QTableWidgetItem(name))
            self.report_table.setItem(row, 2, QTableWidgetItem(str(record.get('department_name', 'N/A'))))
            
            att_date = record.get('attendance_date')
            if att_date:
                if isinstance(att_date, str):
                    from datetime import datetime
                    try:
                        att_date = datetime.strptime(att_date, '%Y-%m-%d').date()
                    except:
                        att_date = None
                if att_date and hasattr(att_date, 'strftime'):
                    self.report_table.setItem(row, 3, QTableWidgetItem(att_date.strftime('%Y-%m-%d')))
                else:
                    self.report_table.setItem(row, 3, QTableWidgetItem(str(att_date) if att_date else 'N/A'))
            else:
                self.report_table.setItem(row, 3, QTableWidgetItem('N/A'))
            
            time_in = record.get('time_in')
            if time_in:
                time_in_str = str(time_in)
                if len(time_in_str) >= 5:
                    time_in_str = time_in_str[:5]  # HH:MM format
                self.report_table.setItem(row, 4, QTableWidgetItem(time_in_str))
            else:
                self.report_table.setItem(row, 4, QTableWidgetItem('N/A'))
            
            time_out = record.get('time_out')
            if time_out:
                time_out_str = str(time_out)
                if len(time_out_str) >= 5:
                    time_out_str = time_out_str[:5]  # HH:MM format
                self.report_table.setItem(row, 5, QTableWidgetItem(time_out_str))
            else:
                self.report_table.setItem(row, 5, QTableWidgetItem('N/A'))
            
            hours = record.get('hours_worked', 0) or 0
            try:
                hours_float = float(hours)
                self.report_table.setItem(row, 6, QTableWidgetItem(f"{hours_float:.2f}"))
            except (ValueError, TypeError):
                self.report_table.setItem(row, 6, QTableWidgetItem('0.00'))
            
            status = record.get('status', 'N/A')
            self.report_table.setItem(row, 7, QTableWidgetItem(str(status) if status else 'N/A'))
            
            late_min = record.get('late_minutes', 0) or 0
            self.report_table.setItem(row, 8, QTableWidgetItem(str(int(late_min))))
            
            undertime_min = record.get('undertime_minutes', 0) or 0
            self.report_table.setItem(row, 9, QTableWidgetItem(str(int(undertime_min))))
    
    def _display_payroll_report(self):
        """Display payroll report in table."""
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        
        if not self.report_data:
            # Show empty table with headers
            headers = ["Employee Code", "Name", "Department", "Period", "Gross Pay", "Deductions", "Net Pay", "Status"]
            self.report_table.setColumnCount(len(headers))
            self.report_table.setHorizontalHeaderLabels(headers)
            self.report_table.setRowCount(0)
            return
        
        headers = ["Employee Code", "Name", "Department", "Period", "Gross Pay", "Deductions", "Net Pay", "Status"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.setRowCount(len(self.report_data))
        
        for row, record in enumerate(self.report_data):
            self.report_table.setItem(row, 0, QTableWidgetItem(str(record.get('employee_code', 'N/A'))))
            name = f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()
            if not name:
                name = 'N/A'
            self.report_table.setItem(row, 1, QTableWidgetItem(name))
            self.report_table.setItem(row, 2, QTableWidgetItem(str(record.get('department_name', 'N/A'))))
            self.report_table.setItem(row, 3, QTableWidgetItem(str(record.get('period_name', 'N/A'))))
            
            try:
                gross = float(record.get('gross_pay', 0) or 0)
                self.report_table.setItem(row, 4, QTableWidgetItem(f"PHP {gross:,.2f}"))
            except (ValueError, TypeError):
                self.report_table.setItem(row, 4, QTableWidgetItem("PHP 0.00"))
            
            try:
                deductions = float(record.get('total_deductions', 0) or 0)
                self.report_table.setItem(row, 5, QTableWidgetItem(f"PHP {deductions:,.2f}"))
            except (ValueError, TypeError):
                self.report_table.setItem(row, 5, QTableWidgetItem("PHP 0.00"))
            
            try:
                net = float(record.get('net_pay', 0) or 0)
                net_item = QTableWidgetItem(f"PHP {net:,.2f}")
                net_item.setForeground(QColor("#28a745"))
                from PyQt6.QtGui import QFont
                font = QFont()
                font.setBold(True)
                net_item.setFont(font)
                self.report_table.setItem(row, 6, net_item)
            except (ValueError, TypeError):
                self.report_table.setItem(row, 6, QTableWidgetItem("PHP 0.00"))
            
            status = record.get('payroll_status', 'N/A')
            self.report_table.setItem(row, 7, QTableWidgetItem(str(status) if status else 'N/A'))
    
    def _display_performance_report(self):
        """Display performance report in table."""
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        
        if not self.report_data:
            # Show empty table with headers
            headers = ["Employee Code", "Name", "Department", "Payroll Periods", "Total Gross", "Avg Gross", "Total Overtime", "Total Incentives", "Late Count", "Undertime Count", "Avg Hours/Day"]
            self.report_table.setColumnCount(len(headers))
            self.report_table.setHorizontalHeaderLabels(headers)
            self.report_table.setRowCount(0)
            return
        
        headers = ["Employee Code", "Name", "Department", "Payroll Periods", "Total Gross", "Avg Gross", "Total Overtime", "Total Incentives", "Late Count", "Undertime Count", "Avg Hours/Day"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.setRowCount(len(self.report_data))
        
        for row, record in enumerate(self.report_data):
            self.report_table.setItem(row, 0, QTableWidgetItem(str(record.get('employee_code', 'N/A'))))
            name = f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()
            if not name:
                name = 'N/A'
            self.report_table.setItem(row, 1, QTableWidgetItem(name))
            self.report_table.setItem(row, 2, QTableWidgetItem(str(record.get('department_name', 'N/A'))))
            self.report_table.setItem(row, 3, QTableWidgetItem(str(record.get('payroll_periods_count', 0) or 0)))
            
            try:
                total_gross = float(record.get('total_gross_pay', 0) or 0)
                self.report_table.setItem(row, 4, QTableWidgetItem(f"PHP {total_gross:,.2f}"))
            except (ValueError, TypeError):
                self.report_table.setItem(row, 4, QTableWidgetItem("PHP 0.00"))
            
            try:
                avg_gross = float(record.get('avg_gross_pay', 0) or 0)
                self.report_table.setItem(row, 5, QTableWidgetItem(f"PHP {avg_gross:,.2f}"))
            except (ValueError, TypeError):
                self.report_table.setItem(row, 5, QTableWidgetItem("PHP 0.00"))
            
            try:
                total_ot = float(record.get('total_overtime', 0) or 0)
                self.report_table.setItem(row, 6, QTableWidgetItem(f"PHP {total_ot:,.2f}"))
            except (ValueError, TypeError):
                self.report_table.setItem(row, 6, QTableWidgetItem("PHP 0.00"))
            
            try:
                total_inc = float(record.get('total_incentives', 0) or 0)
                self.report_table.setItem(row, 7, QTableWidgetItem(f"PHP {total_inc:,.2f}"))
            except (ValueError, TypeError):
                self.report_table.setItem(row, 7, QTableWidgetItem("PHP 0.00"))
            
            late_count = record.get('late_occurrences', 0) or 0
            self.report_table.setItem(row, 8, QTableWidgetItem(str(int(late_count))))
            
            undertime_count = record.get('undertime_occurrences', 0) or 0
            self.report_table.setItem(row, 9, QTableWidgetItem(str(int(undertime_count))))
            
            try:
                avg_hours = float(record.get('avg_hours_per_day', 0) or 0)
                self.report_table.setItem(row, 10, QTableWidgetItem(f"{avg_hours:.2f}" if avg_hours > 0 else 'N/A'))
            except (ValueError, TypeError):
                self.report_table.setItem(row, 10, QTableWidgetItem('N/A'))
    
    def _display_total_payroll_summary(self, start_date, end_date):
        """Display comprehensive payroll summary with daily, weekly, and monthly breakdowns."""
        from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QColor
        from models.report_model import (
            get_daily_payroll_summary,
            get_weekly_payroll_summary,
            get_monthly_payroll_summary
        )
        from datetime import timedelta
        
        try:
            # Calculate number of days, weeks, months in the range
            days_diff = (end_date - start_date).days + 1
            
            headers = ["Period", "Date Range", "Employees", "Gross Pay", "Deductions", "Net Pay", "Entries"]
            self.report_table.setColumnCount(len(headers))
            self.report_table.setHorizontalHeaderLabels(headers)
            
            summary_rows = []
            
            # Daily summaries (if range is less than 31 days)
            if days_diff <= 31:
                current_date = start_date
                while current_date <= end_date:
                    daily_summary = get_daily_payroll_summary(current_date)
                    if daily_summary and daily_summary.get('total_net_pay', 0) > 0:
                        summary_rows.append({
                            'period': 'Daily',
                            'date_range': current_date.strftime('%Y-%m-%d'),
                            **daily_summary
                        })
                    current_date += timedelta(days=1)
            
            # Weekly summary
            weekly_summary = get_weekly_payroll_summary(start_date, end_date)
            if weekly_summary and weekly_summary.get('total_net_pay', 0) > 0:
                summary_rows.append({
                    'period': 'WEEKLY TOTAL',
                    'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    **weekly_summary
                })
            
            # Monthly summary (for each month in range)
            current_month_date = start_date.replace(day=1)
            end_month_date = end_date.replace(day=1)
            while current_month_date <= end_month_date:
                monthly_summary = get_monthly_payroll_summary(current_month_date.year, current_month_date.month)
                if monthly_summary and monthly_summary.get('total_net_pay', 0) > 0:
                    month_name = current_month_date.strftime('%B %Y')
                    summary_rows.append({
                        'period': f'MONTHLY TOTAL - {month_name}',
                        'date_range': month_name,
                        **monthly_summary
                    })
                # Move to next month
                if current_month_date.month == 12:
                    current_month_date = current_month_date.replace(year=current_month_date.year + 1, month=1)
                else:
                    current_month_date = current_month_date.replace(month=current_month_date.month + 1)
            
            # Populate table
            self.report_table.setRowCount(len(summary_rows))
            
            for row, record in enumerate(summary_rows):
                # Period
                period_item = QTableWidgetItem(record['period'])
                if 'TOTAL' in record['period']:
                    period_item.setBackground(QColor(220, 235, 250))
                    font = period_item.font()
                    font.setBold(True)
                    period_item.setFont(font)
                self.report_table.setItem(row, 0, period_item)
                
                # Date Range
                date_item = QTableWidgetItem(record['date_range'])
                if 'TOTAL' in record['period']:
                    date_item.setBackground(QColor(220, 235, 250))
                    font = date_item.font()
                    font.setBold(True)
                    date_item.setFont(font)
                self.report_table.setItem(row, 1, date_item)
                
                # Employees
                emp_item = QTableWidgetItem(str(record.get('total_employees', 0)))
                if 'TOTAL' in record['period']:
                    emp_item.setBackground(QColor(220, 235, 250))
                self.report_table.setItem(row, 2, emp_item)
                
                # Gross Pay
                gross = float(record.get('total_gross_pay', 0) or 0)
                gross_item = QTableWidgetItem(f"PHP {gross:,.2f}")
                if 'TOTAL' in record['period']:
                    gross_item.setBackground(QColor(220, 235, 250))
                    font = gross_item.font()
                    font.setBold(True)
                    gross_item.setFont(font)
                self.report_table.setItem(row, 3, gross_item)
                
                # Deductions
                deductions = float(record.get('total_deductions', 0) or 0)
                ded_item = QTableWidgetItem(f"PHP {deductions:,.2f}")
                if 'TOTAL' in record['period']:
                    ded_item.setBackground(QColor(220, 235, 250))
                self.report_table.setItem(row, 4, ded_item)
                
                # Net Pay
                net = float(record.get('total_net_pay', 0) or 0)
                net_item = QTableWidgetItem(f"PHP {net:,.2f}")
                if 'TOTAL' in record['period']:
                    net_item.setBackground(QColor(220, 235, 250))
                    font = net_item.font()
                    font.setBold(True)
                    net_item.setFont(font)
                self.report_table.setItem(row, 5, net_item)
                
                # Entries
                entries_item = QTableWidgetItem(str(record.get('total_entries', 0)))
                if 'TOTAL' in record['period']:
                    entries_item.setBackground(QColor(220, 235, 250))
                self.report_table.setItem(row, 6, entries_item)
            
            # Store for PDF export
            self.report_data = summary_rows
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate payroll summary: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _export_to_pdf(self):
        """Export report to PDF based on report type."""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            from models.audit_model import log_audit
            from datetime import datetime
            from utils.pdf_generator import generate_hr_report_pdf
            
            if not self.report_data:
                QMessageBox.warning(self, "No Data", "Please generate a report first.")
                return
            
            report_type = self.cb_type.currentText()
            if report_type == "Select Report Type":
                QMessageBox.warning(self, "Validation Error", "Please select a report type.")
                return
            
            department = self.cb_dept.currentText()
            start_date = self.date_start.date().toPyDate()
            end_date = self.date_end.date().toPyDate()
            
            # Get default filename
            dept_str = department.replace(" ", "_") if department != "All Departments" else "All_Departments"
            report_type_str = report_type.replace(" ", "_")
            default_filename = f"{report_type_str}_Report_{dept_str}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            # Show save dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Employee List as PDF",
                default_filename,
                "PDF Files (*.pdf)"
            )
            
            if not filename:
                return  # User cancelled
            
            # Generate PDF based on report type
            from models.company_model import get_company_settings
            company_settings = get_company_settings()
            company_name = company_settings.get('company_name', 'COMPANY NAME') if company_settings else 'COMPANY NAME'
            
            success = generate_hr_report_pdf(
                filename,
                report_type,
                self.report_data,
                company_name,
                department,
                start_date,
                end_date
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"{report_type} report exported to PDF successfully!\n\nSaved to: {filename}"
                )
                log_audit(None, "Export PDF", f"Exported {report_type} report to PDF: {filename}")
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF. Please try again.")
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to export report: {str(e)}")
            import traceback
            traceback.print_exc()

    def _add_row(self, grid: QGridLayout, row: int, txt: str, widget: QWidget):
        lbl = QLabel(txt)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl.setStyleSheet("color: #555; font-weight: 600; font-size: 14px; padding-right: 15px;")
        grid.addWidget(lbl, row, 0)
        grid.addWidget(widget, row, 1)
        
        # Set minimum height for better visual consistency
        if hasattr(widget, 'setMinimumHeight'):
            widget.setMinimumHeight(40)


class HrMainWindow(QMainWindow):
    """
    HR Officer main window with core functions:
    1. Employee Registration - onboard new staff
    2. Payroll Computation - salary processing
    3. Reports - organizational analysis
    
    Also includes Dashboard and Employee List for comprehensive HR operations.
    """

    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Proly System - HR Officer")
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

        # Logo row with app logo icon
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

        self.btn_dashboard = self._create_nav_btn(
            "Dashboard", "assets/images/dashboardIcon.png"
        )
        self.btn_employee_list = self._create_nav_btn(
            "Employee List", None
        )
        self.btn_employee = self._create_nav_btn(
            "Employee\nRegistration", "assets/images/employeeRegistrationIcon.png"
        )
        self.btn_payroll_comp = self._create_nav_btn(
            "Payroll\nComputation", "assets/images/payrollComputationIcon.png"
        )
        self.btn_reports = self._create_nav_btn(
            "Reports", "assets/images/reportsIcon.png"
        )

        sb_layout.addWidget(self.btn_dashboard)
        sb_layout.addWidget(self.btn_employee_list)
        sb_layout.addWidget(self.btn_employee)
        sb_layout.addWidget(self.btn_payroll_comp)
        sb_layout.addWidget(self.btn_reports)
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

        profile_lbl = QLabel("HR Officer")
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
        self.dashboard_view = DashboardView()
        from views.hr_employee_list_view import HrEmployeeListView
        self.employee_list_view = HrEmployeeListView()
        self.reg_view = RegistrationView()
        # Import Payroll Computation view from accountant module
        from views.accountant_main_window import AccountantPayrollCompView
        self.payroll_comp_view = AccountantPayrollCompView()
        self.reports_view = ReportsView()
        
        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.employee_list_view)
        self.stack.addWidget(self.reg_view)
        self.stack.addWidget(self.payroll_comp_view)
        self.stack.addWidget(self.reports_view)

        cc_layout.addWidget(self.stack)

        main_hlayout.addWidget(content_container)

        # Navigation
        self.btn_dashboard.clicked.connect(lambda: self._navigate(0))
        self.btn_employee_list.clicked.connect(lambda: self._navigate(1))
        self.btn_employee.clicked.connect(lambda: self._navigate(2))
        self.btn_payroll_comp.clicked.connect(lambda: self._navigate(3))
        self.btn_reports.clicked.connect(lambda: self._navigate(4))

        self.btn_dashboard.setChecked(True)

    def _create_nav_btn(self, text: str, icon_path: str | None = None) -> QPushButton:
        btn = QPushButton(f"  {text}")
        btn.setObjectName("SidebarBtn")
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
        # Refresh dashboard when navigating back to it
        if index == 0 and hasattr(self.dashboard_view, 'refresh_data'):
            self.dashboard_view.refresh_data()
    
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
    window = HrMainWindow()
    window.show()
    sys.exit(app.exec())


