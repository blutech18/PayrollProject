from __future__ import annotations

from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QAbstractSpinBox,
    QHeaderView,
    QGridLayout,
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
        background-color: #EFEBE6; 
        border: 1px solid #D6CDC6;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 13px;
        color: #555;
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
    
    QPushButton.PrimaryBtn {
        background-color: #F0D095;
        border: 1px solid #C0A065;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 12px;
    }
    QPushButton.PrimaryBtn:hover { background-color: #F5DCA0; }

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


def create_stat_card(title: str, value: str, subtext: str = "", icon_char: str = "?", value_color: str = "#444") -> QWidget:
    """Helper to create stat cards."""
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
    lbl_val.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {value_color};")

    layout.addWidget(icon_box)
    layout.addWidget(lbl_title)
    layout.addWidget(lbl_val)

    if subtext:
        lbl_sub = QLabel(subtext)
        if "+" in subtext or "↑" in subtext:
            lbl_sub.setStyleSheet("font-size: 11px; font-weight: bold; color: #6BA855;")
        else:
            lbl_sub.setStyleSheet("font-size: 12px; font-weight: bold; color: #555;")
        layout.addWidget(lbl_sub)

    layout.addStretch()
    return card


import logging


logger = logging.getLogger(__name__)


class AdminDashboardView(QWidget):
    """Admin Dashboard matching Wireframe_page-0010.jpg (System Overview)."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 30, 40, 40)

        # Header with title and refresh button
        header_layout = QHBoxLayout()
        title = QLabel("SYSTEM OVERVIEW")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #555;")
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
        self.layout.addSpacing(20)

        # Top Row - All 3 Stats Cards in One Row
        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(30)
        self._load_all_cards()
        self.cards_row.addStretch()
        self.layout.addLayout(self.cards_row)

        self.layout.addSpacing(30)

        # Analytics Section Title
        analytics_title = QLabel("SYSTEM ANALYTICS")
        analytics_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #555;")
        self.layout.addWidget(analytics_title)
        self.layout.addSpacing(15)

        # Analytics Charts Row
        self.charts_row = QHBoxLayout()
        self.charts_row.setSpacing(30)
        self._load_analytics_charts()
        self.layout.addLayout(self.charts_row)

        self.layout.addStretch()
    
    def _load_all_cards(self):
        """Load all dashboard stat cards in one row."""
        try:
            from models.dashboard_model import get_admin_dashboard_stats
            stats = get_admin_dashboard_stats()
            
            # Card 1: Total Users
            self.cards_row.addWidget(create_stat_card("Total Users", str(stats["total_users"]), "", "👥"))
            
            # Card 2: System Health
            self.cards_row.addWidget(create_stat_card("System Health", stats["system_health"], "", "🖥️", value_color="#28a745"))
            
            # Card 3: Last Backup
            last_backup = stats.get("last_backup", "Never")
            self.cards_row.addWidget(create_stat_card("Last Backup", last_backup, "", "💾"))
            
        except Exception as e:
            logger.exception("Error loading dashboard cards: %s", e)
            # Fallback cards
            self.cards_row.addWidget(create_stat_card("Total Users", "0", "", "👥"))
            self.cards_row.addWidget(create_stat_card("System Health", "OK", "", "🖥️", value_color="#28a745"))
            self.cards_row.addWidget(create_stat_card("Last Backup", "Never", "", "💾"))
    
    def _load_analytics_charts(self):
        """Load analytics charts - User Activity and Department Distribution."""
        # Chart 1: User Activity Over Time (Line Chart)
        activity_chart = self._create_user_activity_chart()
        self.charts_row.addWidget(activity_chart)
        
        # Chart 2: Employees by Department (Bar Chart)
        department_chart = self._create_department_chart()
        self.charts_row.addWidget(department_chart)
        
        self.charts_row.addStretch()
    
    def refresh_data(self):
        """Refresh dashboard data by clearing and reloading all content."""
        # Clear existing cards
        while self.cards_row.count() > 0:
            item = self.cards_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        while self.charts_row.count() > 0:
            item = self.charts_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Reload data
        self._load_all_cards()
        self._load_analytics_charts()
        self.cards_row.addStretch()
        self.charts_row.addStretch()
    
    def _create_user_activity_chart(self) -> QWidget:
        """Create user activity line chart."""
        try:
            import matplotlib
            matplotlib.use('QtAgg')
            try:
                from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            except ImportError:
                # Fallback for older matplotlib versions
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from matplotlib.figure import Figure
            from models.database import get_connection
            from datetime import datetime, timedelta
            
            # Get audit log data for the last 7 days
            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("""
                        SELECT DATE(created_at) as date, COUNT(*) as count
                        FROM audit_logs
                        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                        GROUP BY DATE(created_at)
                        ORDER BY date
                    """)
                    data = cur.fetchall()
            
            # Prepare data
            if data:
                dates = [row['date'].strftime('%m/%d') if hasattr(row['date'], 'strftime') else row['date'] for row in data]
                counts = [row['count'] for row in data]
            else:
                # Fallback data
                dates = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
                counts = [5, 8, 12, 7, 15, 10, 9]
            
            # Create chart
            card = ShadowCard()
            card.setFixedSize(450, 300)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)
            
            # Title
            title_label = QLabel("User Activity (Last 7 Days)")
            title_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #444;")
            card_layout.addWidget(title_label)
            card_layout.addSpacing(10)
            
            # Create matplotlib figure
            fig = Figure(figsize=(4, 2), facecolor='#FDF8F2')
            canvas = FigureCanvasQTAgg(fig)
            ax = fig.add_subplot(111)
            
            # Plot data
            ax.plot(dates, counts, marker='o', linewidth=2, markersize=6, color='#F0D095')
            ax.fill_between(range(len(dates)), counts, alpha=0.3, color='#F0D095')
            
            # Styling
            ax.set_facecolor('#FDF8F2')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#D6CDC6')
            ax.spines['bottom'].set_color('#D6CDC6')
            ax.tick_params(colors='#666', labelsize=9)
            ax.grid(True, alpha=0.2, linestyle='--')
            ax.set_xlabel('Date', fontsize=10, color='#666')
            ax.set_ylabel('Actions', fontsize=10, color='#666')
            
            fig.tight_layout()
            
            card_layout.addWidget(canvas)
            return card
            
        except Exception as e:
            logger.exception("Error creating activity chart: %s", e)
            # Fallback card
            card = ShadowCard()
            card.setFixedSize(450, 300)
            layout = QVBoxLayout(card)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder = QLabel("User Activity Chart\n(Install matplotlib to view)")
            placeholder.setStyleSheet("color: #999; font-size: 12px; text-align: center;")
            layout.addWidget(placeholder)
            return card
    
    def _create_department_chart(self) -> QWidget:
        """Create department distribution bar chart."""
        try:
            import matplotlib
            matplotlib.use('QtAgg')
            try:
                from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            except ImportError:
                # Fallback for older matplotlib versions
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from matplotlib.figure import Figure
            from models.database import get_connection
            
            # Get department data
            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("""
                        SELECT d.name as department, COUNT(e.id) as count
                        FROM departments d
                        LEFT JOIN employees e ON d.id = e.department_id AND e.is_active = 1
                        GROUP BY d.id, d.name
                        ORDER BY count DESC
                    """)
                    data = cur.fetchall()
            
            # Prepare data
            if data:
                departments = [row['department'] for row in data]
                counts = [row['count'] for row in data]
            else:
                # Fallback data
                departments = ['IT', 'HR', 'Sales', 'Finance', 'Operations']
                counts = [8, 5, 6, 4, 3]
            
            # Create chart
            card = ShadowCard()
            card.setFixedSize(450, 300)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)
            
            # Title
            title_label = QLabel("Employees by Department")
            title_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #444;")
            card_layout.addWidget(title_label)
            card_layout.addSpacing(10)
            
            # Create matplotlib figure
            fig = Figure(figsize=(4, 2), facecolor='#FDF8F2')
            canvas = FigureCanvasQTAgg(fig)
            ax = fig.add_subplot(111)
            
            # Plot data
            bars = ax.bar(departments, counts, color='#F0D095', edgecolor='#C0A065', linewidth=1.5)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=10, color='#444', fontweight='bold')
            
            # Styling
            ax.set_facecolor('#FDF8F2')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#D6CDC6')
            ax.spines['bottom'].set_color('#D6CDC6')
            ax.tick_params(colors='#666', labelsize=9)
            ax.grid(True, alpha=0.2, linestyle='--', axis='y')
            ax.set_xlabel('Department', fontsize=10, color='#666')
            ax.set_ylabel('Employees', fontsize=10, color='#666')
            
            fig.tight_layout()
            
            card_layout.addWidget(canvas)
            return card
            
        except Exception as e:
            logger.exception("Error creating department chart: %s", e)
            # Fallback card
            card = ShadowCard()
            card.setFixedSize(450, 300)
            layout = QVBoxLayout(card)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder = QLabel("Department Chart\n(Install matplotlib to view)")
            placeholder.setStyleSheet("color: #999; font-size: 12px; text-align: center;")
            layout.addWidget(placeholder)
            return card


class AdminAuditLogsView(QWidget):
    """Audit Logs view matching Wireframe_page-0011.jpg."""

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

        # Filters Section
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

        filter_layout.addWidget(QLabel("FILTER :", styleSheet="font-weight:bold; color:#555;"))

        # User Filter
        filter_layout.addWidget(QLabel("USER :", styleSheet="font-size:12px; color:#666;"))
        self.user_filter_combo = QComboBox()
        self.user_filter_combo.addItems(["ALL", "Admin", "HR Officer", "Accountant", "Employee"])
        self.user_filter_combo.setFixedWidth(120)
        filter_layout.addWidget(self.user_filter_combo)

        # Actions Filter
        filter_layout.addWidget(QLabel("ACTIONS :", styleSheet="font-size:12px; color:#666;"))
        self.action_filter_combo = QComboBox()
        self.action_filter_combo.addItems(["ALL", "Login", "Edit", "Delete", "Create"])
        self.action_filter_combo.setFixedWidth(120)
        filter_layout.addWidget(self.action_filter_combo)

        # Date Filter
        filter_layout.addWidget(QLabel("DATE :", styleSheet="font-size:12px; color:#666;"))
        self.date_filter = QDateEdit()
        self.date_filter.setDisplayFormat("MM / dd / yy")
        self.date_filter.setFixedWidth(120)
        self.date_filter.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.date_filter.setCalendarPopup(True)
        # Set to a far past date to indicate "no filter" initially
        from datetime import date
        self.date_filter.setDate(QDate(1900, 1, 1))
        filter_layout.addWidget(self.date_filter)

        filter_layout.addStretch()
        cl.addLayout(filter_layout)
        cl.addSpacing(20)

        # Header
        cl.addWidget(QLabel("ACTIVITY LOG", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        cl.addSpacing(10)

        # Table
        self.audit_table = QTableWidget(0, 4)
        self.audit_table.setHorizontalHeaderLabels(["Date Time", "User", "Action", "Details"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.audit_table.verticalHeader().setVisible(False)
        self.audit_table.setAlternatingRowColors(True)
        
        # Connect filter changes to reload data
        self.user_filter_combo.currentTextChanged.connect(self._load_audit_logs)
        self.action_filter_combo.currentTextChanged.connect(self._load_audit_logs)
        self.date_filter.dateChanged.connect(self._load_audit_logs)
        
        # Load audit logs
        self._load_audit_logs()

        cl.addWidget(self.audit_table)
        cl.addSpacing(15)
        
        # Export PDF Button
        export_btn_layout = QHBoxLayout()
        export_btn_layout.addStretch()
        self.export_pdf_btn = QPushButton("📄 Export to PDF")
        self.export_pdf_btn.setProperty("class", "PrimaryBtn")
        self.export_pdf_btn.setFixedWidth(180)
        self.export_pdf_btn.clicked.connect(self._export_to_pdf)
        export_btn_layout.addWidget(self.export_pdf_btn)
        export_btn_layout.addStretch()
        cl.addLayout(export_btn_layout)
        
        # Center card
        card_container = QHBoxLayout()
        card_container.addStretch()
        card_container.addWidget(card)
        card_container.addStretch()
        layout.addLayout(card_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)
    
    def _load_audit_logs(self):
        """Load audit logs from database based on filters."""
        try:
            from models.audit_model import get_audit_logs
            
            user_filter = self.user_filter_combo.currentText()
            action_filter = self.action_filter_combo.currentText()
            date_filter = None
            # Only use date filter if a valid date is selected (not the default "no filter" date)
            current_date = self.date_filter.date()
            # Check if date is valid and not set to the default "no filter" date (year 1900)
            if current_date.isValid() and current_date.year() > 2000:
                date_filter = current_date.toString("yyyy-MM-dd")
            
            logs = get_audit_logs(user_filter, action_filter, date_filter)
            
            self.audit_table.setRowCount(len(logs))
            for row, log in enumerate(logs):
                from datetime import datetime
                created_at = log['created_at']
                if isinstance(created_at, str):
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                else:
                    dt = created_at
                
                self.audit_table.setItem(row, 0, QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M:%S")))
                self.audit_table.setItem(row, 1, QTableWidgetItem(log['user'] or 'N/A'))
                self.audit_table.setItem(row, 2, QTableWidgetItem(log['action']))
                self.audit_table.setItem(row, 3, QTableWidgetItem(log['details'] or ''))
        except Exception as e:
            logger.exception("Error loading audit logs: %s", e)
            self.audit_table.setRowCount(0)
    
    def _export_to_pdf(self):
        """Export audit logs to PDF."""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            from utils.pdf_generator import generate_audit_log_pdf
            from models.audit_model import get_audit_logs
            from datetime import datetime
            
            user_filter = self.user_filter_combo.currentText()
            action_filter = self.action_filter_combo.currentText()
            date_filter = None
            # Only use date filter if a valid date is selected (not the default "no filter" date)
            current_date = self.date_filter.date()
            # Check if date is valid and not set to the default "no filter" date (year 1900)
            if current_date.isValid() and current_date.year() > 2000:
                date_filter = current_date.toString("yyyy-MM-dd")
            
            logs = get_audit_logs(user_filter, action_filter, date_filter)
            
            if not logs:
                QMessageBox.warning(self, "No Data", "No audit logs found with the selected filters.")
                return
            
            # Get default filename
            filter_str = ""
            if user_filter != "ALL":
                filter_str += f"_{user_filter.replace(' ', '_')}"
            if action_filter != "ALL":
                filter_str += f"_{action_filter}"
            
            default_filename = f"Audit_Logs{filter_str}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            # Show save dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Audit Logs as PDF",
                default_filename,
                "PDF Files (*.pdf)"
            )
            
            if not filename:
                return  # User cancelled
            
            # Prepare filter info
            filters = {
                'user': user_filter,
                'action': action_filter,
                'date': date_filter
            }
            
            # Generate PDF
            success = generate_audit_log_pdf(filename, logs, filters)
            
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Audit logs have been exported to PDF successfully!\n\nSaved to: {filename}"
                )
                
                # Log the export action
                from models.audit_model import log_audit
                log_audit(None, "Export PDF", f"Exported audit logs to PDF with filters: User={user_filter}, Action={action_filter}")
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF. Please try again.")
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to export audit logs: {str(e)}")
            import traceback
            traceback.print_exc()


class AdminSystemMaintenanceView(QWidget):
    """System Maintenance view matching Wireframe_page-0012.jpg."""

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
        card.setMinimumWidth(700)
        card.setMaximumWidth(900)
        card.setMinimumHeight(500)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)

        # COMPLIANCE UPDATES Section
        cl.addWidget(QLabel("COMPLIANCE UPDATES", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        cl.addSpacing(20)

        compliance_grid = QGridLayout()
        compliance_grid.setVerticalSpacing(15)
        compliance_grid.setHorizontalSpacing(20)

        # BIR Tax
        compliance_grid.addWidget(QLabel("BIR Tax :", styleSheet="font-size:14px; color:#555;"), 0, 0)
        self.bir_upload_btn = QPushButton("UPLOAD FILE")
        self.bir_upload_btn.setProperty("class", "PrimaryBtn")
        self.bir_upload_btn.setFixedWidth(150)
        self.bir_upload_btn.clicked.connect(lambda: self._upload_compliance_file("BIR Tax"))
        compliance_grid.addWidget(self.bir_upload_btn, 0, 1)
        self.bir_last_label = QLabel("Last : Jan 2024", styleSheet="font-size:12px; color:#666;")
        compliance_grid.addWidget(self.bir_last_label, 0, 2)

        # SSS Contributions
        compliance_grid.addWidget(QLabel("SSS Contributions :", styleSheet="font-size:14px; color:#555;"), 1, 0)
        self.sss_upload_btn = QPushButton("UPLOAD FILE")
        self.sss_upload_btn.setProperty("class", "PrimaryBtn")
        self.sss_upload_btn.setFixedWidth(150)
        self.sss_upload_btn.clicked.connect(lambda: self._upload_compliance_file("SSS Contributions"))
        compliance_grid.addWidget(self.sss_upload_btn, 1, 1)
        self.sss_last_label = QLabel("Last : Jan 2024", styleSheet="font-size:12px; color:#666;")
        compliance_grid.addWidget(self.sss_last_label, 1, 2)

        # PhilHealth Rates
        compliance_grid.addWidget(QLabel("PhilHealth Rates :", styleSheet="font-size:14px; color:#555;"), 2, 0)
        self.philhealth_upload_btn = QPushButton("UPLOAD FILE")
        self.philhealth_upload_btn.setProperty("class", "PrimaryBtn")
        self.philhealth_upload_btn.setFixedWidth(150)
        self.philhealth_upload_btn.clicked.connect(lambda: self._upload_compliance_file("PhilHealth Rates"))
        compliance_grid.addWidget(self.philhealth_upload_btn, 2, 1)
        self.philhealth_last_label = QLabel("Last : Jan 2024", styleSheet="font-size:12px; color:#666;")
        compliance_grid.addWidget(self.philhealth_last_label, 2, 2)

        # Pag-IBIG Rates
        compliance_grid.addWidget(QLabel("Pag-IBIG Rates :", styleSheet="font-size:14px; color:#555;"), 3, 0)
        self.pagibig_upload_btn = QPushButton("UPLOAD FILE")
        self.pagibig_upload_btn.setProperty("class", "PrimaryBtn")
        self.pagibig_upload_btn.setFixedWidth(150)
        self.pagibig_upload_btn.clicked.connect(lambda: self._upload_compliance_file("Pag-IBIG Rates"))
        compliance_grid.addWidget(self.pagibig_upload_btn, 3, 1)
        self.pagibig_last_label = QLabel("Last : Jan 2024", styleSheet="font-size:12px; color:#666;")
        compliance_grid.addWidget(self.pagibig_last_label, 3, 2)

        cl.addLayout(compliance_grid)
        cl.addSpacing(30)

        # SYSTEM SETTINGS Section
        cl.addWidget(QLabel("SYSTEM SETTINGS", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        cl.addSpacing(20)

        settings_grid = QGridLayout()
        settings_grid.setVerticalSpacing(15)
        settings_grid.setHorizontalSpacing(20)

        # Pay Period Schedule
        settings_grid.addWidget(QLabel("Pay Period Schedule :", styleSheet="font-size:14px; color:#555;"), 0, 0)
        self.pay_period_combo = QComboBox()
        self.pay_period_combo.addItems(["SEMI - MONTHLY", "MONTHLY", "WEEKLY", "BI-WEEKLY"])
        self.pay_period_combo.setFixedWidth(200)
        settings_grid.addWidget(self.pay_period_combo, 0, 1)

        # Date Format
        settings_grid.addWidget(QLabel("Date Format :", styleSheet="font-size:14px; color:#555;"), 1, 0)
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["DD / MM / YY", "MM / DD / YY", "YY / MM / DD"])
        self.date_format_combo.setFixedWidth(200)
        settings_grid.addWidget(self.date_format_combo, 1, 1)
        
        # Load existing settings
        self._load_settings()

        cl.addLayout(settings_grid)
        cl.addSpacing(30)

        # Save Settings Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_settings_btn = QPushButton("SAVE SETTINGS")
        self.save_settings_btn.setProperty("class", "PrimaryBtn")
        self.save_settings_btn.setFixedWidth(200)
        self.save_settings_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.save_settings_btn)
        btn_layout.addStretch()
        cl.addLayout(btn_layout)
        
        cl.addStretch()
        
        # Center card
        card_container = QHBoxLayout()
        card_container.addStretch()
        card_container.addWidget(card)
        card_container.addStretch()
        layout.addLayout(card_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)
    
    def _load_settings(self):
        """Load existing system settings from database."""
        try:
            from models.database import get_connection
            from models.compliance_model import get_latest_compliance_file
            from datetime import datetime
            
            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cur:
                    # Load pay period schedule
                    cur.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'pay_period_schedule'")
                    result = cur.fetchone()
                    if result:
                        index = self.pay_period_combo.findText(result['setting_value'])
                        if index >= 0:
                            self.pay_period_combo.setCurrentIndex(index)
                    
                    # Load date format
                    cur.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'date_format'")
                    result = cur.fetchone()
                    if result:
                        index = self.date_format_combo.findText(result['setting_value'])
                        if index >= 0:
                            self.date_format_combo.setCurrentIndex(index)
            
            # Load latest compliance file dates
            for file_type, label in [
                ("BIR Tax", self.bir_last_label),
                ("SSS Contributions", self.sss_last_label),
                ("PhilHealth Rates", self.philhealth_last_label),
                ("Pag-IBIG Rates", self.pagibig_last_label)
            ]:
                latest = get_latest_compliance_file(file_type)
                if latest:
                    last_date = latest['effective_from']
                    if isinstance(last_date, str):
                        last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
                    label.setText(f"Last : {last_date.strftime('%b %Y')}")
        except Exception as e:
            logger.exception("Error loading settings: %s", e)
            # Use defaults if loading fails
    
    def _upload_compliance_file(self, file_type: str):
        """Handle compliance file upload with version control."""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
            from models.audit_model import log_audit
            from models.compliance_model import upload_compliance_file, get_latest_compliance_file
            from datetime import datetime, date
            
            # Open file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                f"Upload {file_type} File",
                "",
                "All Files (*.*)"
            )
            
            if file_path:
                # Validate file before upload
                from models.validation_model import validate_compliance_file
                is_valid, error_msg, parsed_data = validate_compliance_file(file_path, file_type)
                
                if not is_valid:
                    QMessageBox.warning(
                        self, 
                        "File Validation Failed", 
                        f"The uploaded file failed validation:\n\n{error_msg}\n\n"
                        f"Please ensure the file is in the correct format.\n"
                        f"See COMPLIANCE_UPLOAD_GUIDE.md for format requirements."
                    )
                    return
                
                # Get effective date from user
                effective_date, ok = QInputDialog.getText(
                    self,
                    "Effective Date",
                    f"Enter effective date for {file_type} (YYYY-MM-DD):",
                    text=date.today().strftime("%Y-%m-%d")
                )
                
                if not ok:
                    return
                
                try:
                    effective_from = datetime.strptime(effective_date, "%Y-%m-%d").date()
                except ValueError:
                    QMessageBox.warning(self, "Invalid Date", "Please enter date in YYYY-MM-DD format.")
                    return
                
                # Validate date
                from models.validation_model import validate_date
                date_valid, date_error = validate_date(effective_from, "Effective Date", allow_future=True)
                if not date_valid:
                    QMessageBox.warning(self, "Invalid Date", date_error)
                    return
                
                # Upload file with version control
                upload_id = upload_compliance_file(file_type, file_path, effective_from)
                
                log_audit(None, "Upload Compliance", f"Uploaded {file_type} file: {file_path} (Effective: {effective_from}, ID: {upload_id})")
                
                # Update the "Last" label with latest upload info
                latest = get_latest_compliance_file(file_type)
                if latest:
                    last_date = latest['effective_from']
                    if isinstance(last_date, str):
                        last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
                    current_date = last_date.strftime("%b %Y")
                else:
                    current_date = datetime.now().strftime("%b %Y")
                
                if file_type == "BIR Tax":
                    self.bir_last_label.setText(f"Last : {current_date}")
                elif file_type == "SSS Contributions":
                    self.sss_last_label.setText(f"Last : {current_date}")
                elif file_type == "PhilHealth Rates":
                    self.philhealth_last_label.setText(f"Last : {current_date}")
                elif file_type == "Pag-IBIG Rates":
                    self.pagibig_last_label.setText(f"Last : {current_date}")
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"{file_type} file has been uploaded successfully!\n\n"
                    f"Effective Date: {effective_from}\n"
                    f"Version: {latest['version'] if latest else 1}\n\n"
                    f"This version will be used for all payroll calculations from {effective_from} onwards."
                )
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to upload file: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _save_settings(self):
        """Save system settings."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            from models.audit_model import log_audit
            from models.database import get_connection
            
            # Get settings values
            pay_period = self.pay_period_combo.currentText()
            date_format = self.date_format_combo.currentText()
            
            # Save to database
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Update or insert pay period schedule
                    cur.execute(
                        """INSERT INTO system_settings (setting_key, setting_value) 
                           VALUES ('pay_period_schedule', %s)
                           ON DUPLICATE KEY UPDATE setting_value = %s, updated_at = NOW()""",
                        (pay_period, pay_period)
                    )
                    
                    # Update or insert date format
                    cur.execute(
                        """INSERT INTO system_settings (setting_key, setting_value) 
                           VALUES ('date_format', %s)
                           ON DUPLICATE KEY UPDATE setting_value = %s, updated_at = NOW()""",
                        (date_format, date_format)
                    )
                    
                    conn.commit()
            
            log_audit(None, "Save Settings", f"Updated system settings: Pay Period={pay_period}, Date Format={date_format}")
            
            QMessageBox.information(
                self, 
                "Settings Saved", 
                f"System settings have been saved successfully!\n\n"
                f"Pay Period Schedule: {pay_period}\n"
                f"Date Format: {date_format}"
            )
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            import traceback
            traceback.print_exc()


class AdminUserManagementView(QWidget):
    """User Management view matching Wireframe_page-0013.jpg."""

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
        card.setMinimumHeight(600)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)

        # Add User Button
        self.add_user_btn = QPushButton("+ Add User")
        self.add_user_btn.setProperty("class", "PrimaryBtn")
        self.add_user_btn.setFixedWidth(120)
        self.add_user_btn.clicked.connect(self._add_user)
        cl.addWidget(self.add_user_btn)
        cl.addSpacing(15)

        # USER LIST Header
        cl.addWidget(QLabel("USER LIST", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        cl.addSpacing(10)

        # Table - Show Username, Role, Status, and Password (for admin view only)
        self.user_table = QTableWidget(0, 5)
        self.user_table.setHorizontalHeaderLabels(["Username", "Password", "Role", "Status", "Actions"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setAlternatingRowColors(True)
        
        # Load users from database
        self._load_users()

        cl.addWidget(self.user_table)
        
        # Center card
        card_container = QHBoxLayout()
        card_container.addStretch()
        card_container.addWidget(card)
        card_container.addStretch()
        layout.addLayout(card_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)
    
    def _load_users(self):
        """Load users from database with password display (admin only)."""
        try:
            from models.user_management_model import get_all_users

            # Use model layer to load all users (passwords are never shown in plain text)
            users = get_all_users()

            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                # Username
                self.user_table.setItem(row, 0, QTableWidgetItem(user['username']))
                
                # Password - never display real or default passwords
                password_display = "********"
                
                password_item = QTableWidgetItem(password_display)
                if password_display == "emp123":
                    password_item.setToolTip("Default password for employee accounts created during registration.")
                else:
                    password_item.setToolTip("Custom password set by admin.")
                self.user_table.setItem(row, 1, password_item)
                
                # Role
                self.user_table.setItem(row, 2, QTableWidgetItem(user['role']))
                
                # Status
                self.user_table.setItem(row, 3, QTableWidgetItem(user['status']))
                
                # Create action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setProperty("class", "SecondaryBtn")
                edit_btn.setFixedWidth(60)
                edit_btn.clicked.connect(lambda checked, u=user: self._edit_user(u))
                
                delete_btn = QPushButton("Delete")
                delete_btn.setProperty("class", "SecondaryBtn")
                delete_btn.setFixedWidth(60)
                delete_btn.clicked.connect(lambda checked, u=user: self._delete_user(u))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.user_table.setCellWidget(row, 4, actions_widget)
        except Exception as e:
            logger.exception("Error loading users: %s", e)
            self.user_table.setRowCount(0)
    
    def _add_user(self):
        """Open dialog to add a new user."""
        from views.user_dialog import UserDialog
        
        dialog = UserDialog(self)
        if dialog.exec() == UserDialog.DialogCode.Accepted:
            self._load_users()  # Refresh the table
    
    def _edit_user(self, user):
        """Edit user details."""
        from views.user_dialog import UserDialog
        
        dialog = UserDialog(self, user_data=user)
        if dialog.exec() == UserDialog.DialogCode.Accepted:
            self._load_users()  # Refresh the table
    
    def _delete_user(self, user):
        """Delete a user."""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            "Delete User", 
            f"Are you sure you want to delete user '{user['username']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from models.database import get_connection
                from models.audit_model import log_audit
                
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("UPDATE users SET is_active = 0 WHERE id = %s", (user.get('id'),))
                        conn.commit()
                
                log_audit(None, "Delete User", f"Deleted user: {user['username']}")
                QMessageBox.information(self, "Success", f"User '{user['username']}' has been deleted.")
                self._load_users()  # Refresh the table
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
                import traceback
                traceback.print_exc()


class PlaceholderView(QWidget):
    """Generic placeholder for Admin pages not yet wireframed."""

    def __init__(self, text: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder = QLabel(text)
        placeholder.setStyleSheet("font-size: 24px; color: #888; font-weight: bold;")
        layout.addWidget(placeholder)


class AdminMainWindow(QMainWindow):
    """
    Administrator - Guardian of system's technical health and security.
    High-level privileges per Figure 5:
    
    Shared Functions:
    1. Employee Registration - Shared with HR Officer
    2. User Management - Shared with HR Officer
    
    Exclusive Functions (Administrator only):
    3. Audit Logs - Monitor security through activity logs
    4. System Maintenance - Perform technical updates and configuration
    
    Primary function: Oversee system performance, monitor security, and maintain platform operations.
    """

    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Proly System - Administrator")
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
        self.btn_employee_reg = self._create_nav_btn(
            "Employee\nRegistration", "assets/images/employeeRegistrationIcon.png"
        )
        self.btn_user_mgmt = self._create_nav_btn(
            "User\nManagement", "assets/images/userManagementIcon.png"
        )
        self.btn_audit_logs = self._create_nav_btn(
            "Audit Logs", "assets/images/auditLogsIcon.png"
        )
        self.btn_system_maint = self._create_nav_btn(
            "System\nMaintenance", "assets/images/systemMaintenanceIcon.png"
        )

        sb_layout.addWidget(self.btn_dashboard)
        sb_layout.addWidget(self.btn_employee_reg)
        sb_layout.addWidget(self.btn_user_mgmt)
        sb_layout.addWidget(self.btn_audit_logs)
        sb_layout.addWidget(self.btn_system_maint)
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

        profile_lbl = QLabel("Admin")
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
        self.dashboard_view = AdminDashboardView()
        # Import HR views for reuse
        from views.hr_main_window import RegistrationView

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(RegistrationView())  # Reuse HR Employee Registration
        self.stack.addWidget(AdminUserManagementView())
        self.stack.addWidget(AdminAuditLogsView())
        self.stack.addWidget(AdminSystemMaintenanceView())

        cc_layout.addWidget(self.stack)

        main_hlayout.addWidget(content_container)

        # Navigation
        self.btn_dashboard.clicked.connect(lambda: self._navigate(0))
        self.btn_employee_reg.clicked.connect(lambda: self._navigate(1))
        self.btn_user_mgmt.clicked.connect(lambda: self._navigate(2))
        self.btn_audit_logs.clicked.connect(lambda: self._navigate(3))
        self.btn_system_maint.clicked.connect(lambda: self._navigate(4))

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
    window = AdminMainWindow()
    window.show()
    sys.exit(app.exec())

