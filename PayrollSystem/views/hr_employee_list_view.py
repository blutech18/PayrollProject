"""
HR Employee List View - View and manage all employees
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QMessageBox,
    QLineEdit,
)

from .hr_main_window import ShadowCard


class HrEmployeeListView(QWidget):
    """Employee List view for HR to view and manage all employees."""

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

        # Header Card
        header_card = ShadowCard()
        header_card.setMinimumWidth(1000)
        header_card.setMaximumWidth(1200)
        header_card.setFixedHeight(100)
        hc_layout = QHBoxLayout(header_card)
        hc_layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("EMPLOYEE LIST")
        title.setStyleSheet("font-size:24px; font-weight:800; color:#444;")
        hc_layout.addWidget(title)
        hc_layout.addStretch()

        # Search and Filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, code, or department...")
        self.search_input.setFixedWidth(300)
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self._on_search_changed)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setProperty("class", "PrimaryBtn")
        refresh_btn.setFixedWidth(120)
        refresh_btn.setFixedHeight(38)
        refresh_btn.clicked.connect(self._load_employees)

        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(10)
        search_layout.addWidget(refresh_btn)
        hc_layout.addLayout(search_layout)

        # Center header card
        header_container = QHBoxLayout()
        header_container.addStretch()
        header_container.addWidget(header_card)
        header_container.addStretch()
        layout.addLayout(header_container)

        # Employee List Card
        list_card = ShadowCard()
        list_card.setMinimumWidth(1000)
        list_card.setMaximumWidth(1200)
        list_card.setMinimumHeight(600)
        lc_layout = QVBoxLayout(list_card)
        lc_layout.setContentsMargins(40, 40, 40, 40)

        # Table
        self.employee_table = QTableWidget(0, 9)
        self.employee_table.setHorizontalHeaderLabels([
            "Employee Code", "Name", "Position", "Department", 
            "Date Hired", "Salary Type", "Base Salary", "Hourly Rate", "Status"
        ])
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employee_table.verticalHeader().setVisible(False)
        self.employee_table.setAlternatingRowColors(True)
        self.employee_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employee_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.employee_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EBE0D6;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #C0A065;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #FFFFFF;
                font-size: 13px;
            }
        """)
        lc_layout.addWidget(self.employee_table)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.view_details_btn = QPushButton("📋 View Details")
        self.view_details_btn.setProperty("class", "SecondaryBtn")
        self.view_details_btn.setFixedWidth(150)
        self.view_details_btn.setFixedHeight(38)
        self.view_details_btn.clicked.connect(self._view_employee_details)
        
        self.edit_btn = QPushButton("✏️ Edit Employee")
        self.edit_btn.setProperty("class", "PrimaryBtn")
        self.edit_btn.setFixedWidth(150)
        self.edit_btn.setFixedHeight(38)
        self.edit_btn.clicked.connect(self._edit_employee)
        
        self.view_attendance_btn = QPushButton("📅 View Attendance")
        self.view_attendance_btn.setProperty("class", "SecondaryBtn")
        self.view_attendance_btn.setFixedWidth(150)
        self.view_attendance_btn.setFixedHeight(38)
        self.view_attendance_btn.clicked.connect(self._view_employee_attendance)
        
        self.view_payroll_btn = QPushButton("💰 View Payroll History")
        self.view_payroll_btn.setProperty("class", "SecondaryBtn")
        self.view_payroll_btn.setFixedWidth(180)
        self.view_payroll_btn.setFixedHeight(38)
        self.view_payroll_btn.clicked.connect(self._view_payroll_history)

        btn_layout.addWidget(self.view_details_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.view_attendance_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.view_payroll_btn)
        btn_layout.addStretch()

        lc_layout.addSpacing(15)
        lc_layout.addLayout(btn_layout)

        # Center list card
        list_container = QHBoxLayout()
        list_container.addStretch()
        list_container.addWidget(list_card)
        list_container.addStretch()
        layout.addLayout(list_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)

        # Load employees
        self._load_employees()
    
    def _load_employees(self):
        """Load all employees from database."""
        try:
            from models.employee_model import get_all_employees
            from models.database import get_connection
            
            employees = get_all_employees(active_only=False)  # Get all including inactive
            
            # Filter by search if provided
            search_text = self.search_input.text().strip().lower()
            if search_text:
                employees = [
                    emp for emp in employees
                    if (search_text in emp.employee_code.lower() or
                        search_text in f"{emp.first_name} {emp.last_name}".lower() or
                        (emp.department_name and search_text in emp.department_name.lower()))
                ]
            
            self.employee_table.setRowCount(len(employees))
            
            for row, emp in enumerate(employees):
                self.employee_table.setItem(row, 0, QTableWidgetItem(emp.employee_code))
                name = f"{emp.first_name} {emp.last_name}"
                self.employee_table.setItem(row, 1, QTableWidgetItem(name))
                self.employee_table.setItem(row, 2, QTableWidgetItem(emp.position or 'N/A'))
                self.employee_table.setItem(row, 3, QTableWidgetItem(emp.department_name or 'N/A'))
                
                date_hired = emp.date_hired if emp.date_hired else 'N/A'
                self.employee_table.setItem(row, 4, QTableWidgetItem(str(date_hired)))
                
                salary_type = getattr(emp, 'salary_type', 'MONTHLY')
                self.employee_table.setItem(row, 5, QTableWidgetItem(salary_type))
                
                base_salary = getattr(emp, 'base_salary', 0)
                self.employee_table.setItem(row, 6, QTableWidgetItem(f"PHP {base_salary:,.2f}"))
                
                hourly_rate = getattr(emp, 'hourly_rate', 0)
                if hourly_rate == 0 and base_salary > 0:
                    # Calculate hourly rate
                    if salary_type == 'HOURLY':
                        hourly_rate = base_salary
                    elif salary_type == 'DAILY':
                        hourly_rate = base_salary / 8.0
                    elif salary_type == 'MONTHLY':
                        hourly_rate = base_salary / 176.0
                self.employee_table.setItem(row, 7, QTableWidgetItem(f"PHP {hourly_rate:,.2f}"))
                
                status = "Active" if emp.is_active else "Inactive"
                status_item = QTableWidgetItem(status)
                if emp.is_active:
                    status_item.setForeground(QColor("#28a745"))
                else:
                    status_item.setForeground(QColor("#dc3545"))
                self.employee_table.setItem(row, 8, status_item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load employees: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _on_search_changed(self):
        """Filter employees when search text changes."""
        self._load_employees()
    
    def _view_employee_details(self):
        """View detailed information about selected employee."""
        current_row = self.employee_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select an employee to view details.")
            return
        
        employee_code = self.employee_table.item(current_row, 0).text()
        
        try:
            from models.employee_model import get_employee_by_code
            from models.timekeeping_model import get_employee_attendance
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QPushButton
            from datetime import date, timedelta
            
            employee = get_employee_by_code(employee_code)
            if not employee:
                QMessageBox.warning(self, "Error", "Employee not found.")
                return
            
            # Create details dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Employee Details - {employee_code}")
            dialog.setFixedSize(600, 700)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #F2EBE9;
                }
                QLabel {
                    font-size: 13px;
                    color: #333333;
                    background-color: transparent;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(30, 30, 30, 30)
            
            # Header
            header = QLabel(f"EMPLOYEE DETAILS")
            header.setStyleSheet("font-size: 20px; font-weight: 800; color: #333;")
            layout.addWidget(header)
            layout.addSpacing(20)
            
            # Employee Information Grid
            grid = QGridLayout()
            grid.setVerticalSpacing(15)
            grid.setHorizontalSpacing(20)
            
            details = [
                ("Employee Code:", employee.employee_code),
                ("Name:", f"{employee.first_name} {employee.last_name}"),
                ("Position:", employee.position or 'N/A'),
                ("Department:", employee.department_name or 'N/A'),
                ("Date Hired:", employee.date_hired or 'N/A'),
                ("Salary Type:", getattr(employee, 'salary_type', 'MONTHLY')),
                ("Base Salary:", f"PHP {getattr(employee, 'base_salary', 0):,.2f}"),
                ("Hourly Rate:", f"PHP {getattr(employee, 'hourly_rate', 0):,.2f}"),
                ("SSS No:", employee.sss_no or 'N/A'),
                ("PhilHealth No:", employee.philhealth_no or 'N/A'),
                ("Pag-IBIG No:", employee.pagibig_no or 'N/A'),
                ("TIN No:", employee.tin_no or 'N/A'),
                ("Status:", "Active" if employee.is_active else "Inactive"),
            ]
            
            for row, (label_text, value) in enumerate(details):
                label = QLabel(label_text)
                label.setStyleSheet("font-weight: 600;")
                grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignRight)
                
                value_label = QLabel(str(value))
                value_label.setStyleSheet("font-weight: 500;")
                grid.addWidget(value_label, row, 1)
            
            layout.addLayout(grid)
            layout.addSpacing(20)
            
            # Recent Attendance Summary
            try:
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
                attendance_records = get_employee_attendance(employee.id, start_date, end_date)
                
                attendance_summary = QLabel(f"<b>Recent Attendance (Last 30 Days):</b><br>"
                                          f"Total Days: {len(attendance_records)}<br>"
                                          f"Total Hours: {sum(float(r.get('hours_worked', 0)) for r in attendance_records):.2f}")
                attendance_summary.setStyleSheet("font-size: 12px; color: #555;")
                layout.addWidget(attendance_summary)
            except:
                pass
            
            layout.addStretch()
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.setProperty("class", "PrimaryBtn")
            close_btn.setFixedWidth(100)
            close_btn.clicked.connect(dialog.close)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load employee details: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _edit_employee(self):
        """Edit selected employee with proper edit dialog."""
        current_row = self.employee_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select an employee to edit.")
            return
        
        employee_code = self.employee_table.item(current_row, 0).text()
        
        try:
            from models.employee_model import get_employee_by_code, update_employee
            from models.user_management_model import get_departments
            from PyQt6.QtWidgets import (
                QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton, QMessageBox
            )
            from PyQt6.QtCore import QDate
            from datetime import date
            
            employee = get_employee_by_code(employee_code)
            if not employee:
                QMessageBox.warning(self, "Error", "Employee not found.")
                return
            
            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit Employee - {employee_code}")
            dialog.setFixedSize(700, 750)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #F2EBE9;
                }
                QLabel {
                    font-size: 13px;
                    color: #333333;
                    background-color: transparent;
                    font-weight: 600;
                }
                QLineEdit, QComboBox, QDateEdit {
                    background-color: #FFFFFF;
                    border: 2px solid #D6CDC6;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    color: #333;
                    min-height: 30px;
                }
                QPushButton {
                    padding: 10px 25px;
                    border-radius: 6px;
                    font-weight: 700;
                    font-size: 13px;
                    min-height: 35px;
                }
                QPushButton#SaveBtn {
                    background-color: #F0D095;
                    border: 2px solid #C0A065;
                    color: #333;
                }
                QPushButton#SaveBtn:hover {
                    background-color: #F5DCA0;
                }
                QPushButton#CancelBtn {
                    background-color: #FFFFFF;
                    border: 2px solid #333;
                    color: #333;
                }
                QPushButton#CancelBtn:hover {
                    background-color: #F8F8F8;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(30, 30, 30, 30)
            layout.setSpacing(20)
            
            # Header
            header = QLabel("EDIT EMPLOYEE")
            header.setStyleSheet("font-size: 20px; font-weight: 800; color: #333;")
            layout.addWidget(header)
            
            # Form Grid
            grid = QGridLayout()
            grid.setVerticalSpacing(15)
            grid.setHorizontalSpacing(15)
            
            row = 0
            
            # Employee Code (Read-only)
            grid.addWidget(QLabel("Employee Code:"), row, 0, Qt.AlignmentFlag.AlignRight)
            code_edit = QLineEdit(employee.employee_code)
            code_edit.setReadOnly(True)
            code_edit.setStyleSheet(code_edit.styleSheet() + "background-color: #E8E8E8;")
            grid.addWidget(code_edit, row, 1)
            row += 1
            
            # First Name
            grid.addWidget(QLabel("First Name:"), row, 0, Qt.AlignmentFlag.AlignRight)
            first_name_edit = QLineEdit(employee.first_name)
            grid.addWidget(first_name_edit, row, 1)
            row += 1
            
            # Last Name
            grid.addWidget(QLabel("Last Name:"), row, 0, Qt.AlignmentFlag.AlignRight)
            last_name_edit = QLineEdit(employee.last_name)
            grid.addWidget(last_name_edit, row, 1)
            row += 1
            
            # Position
            grid.addWidget(QLabel("Position:"), row, 0, Qt.AlignmentFlag.AlignRight)
            position_edit = QLineEdit(employee.position or "")
            grid.addWidget(position_edit, row, 1)
            row += 1
            
            # Department
            grid.addWidget(QLabel("Department:"), row, 0, Qt.AlignmentFlag.AlignRight)
            dept_combo = QComboBox()
            departments = get_departments()
            dept_combo.addItem("Select Department", None)
            for dept in departments:
                dept_combo.addItem(dept["name"], dept["id"])
                if dept["id"] == employee.department_id:
                    dept_combo.setCurrentIndex(dept_combo.count() - 1)
            grid.addWidget(dept_combo, row, 1)
            row += 1
            
            # Date Hired
            grid.addWidget(QLabel("Date Hired:"), row, 0, Qt.AlignmentFlag.AlignRight)
            date_hired_edit = QDateEdit()
            date_hired_edit.setCalendarPopup(True)
            date_hired_edit.setDisplayFormat("dd / MM / yyyy")
            # Remove date restrictions - allow any date
            date_hired_edit.setMinimumDate(QDate(1900, 1, 1))
            date_hired_edit.setMaximumDate(QDate(2100, 12, 31))
            if employee.date_hired:
                if isinstance(employee.date_hired, str):
                    from datetime import datetime
                    date_obj = datetime.strptime(employee.date_hired, '%Y-%m-%d').date()
                    date_hired_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                else:
                    date_hired_edit.setDate(QDate(employee.date_hired.year, employee.date_hired.month, employee.date_hired.day))
            else:
                date_hired_edit.setDate(QDate.currentDate())
            grid.addWidget(date_hired_edit, row, 1)
            row += 1
            
            # Salary Type
            grid.addWidget(QLabel("Salary Type:"), row, 0, Qt.AlignmentFlag.AlignRight)
            salary_type_combo = QComboBox()
            salary_type_combo.addItems(["MONTHLY", "HOURLY", "DAILY"])
            salary_type = getattr(employee, 'salary_type', 'MONTHLY')
            salary_type_combo.setCurrentText(salary_type)
            grid.addWidget(salary_type_combo, row, 1)
            row += 1
            
            # Base Salary
            grid.addWidget(QLabel("Base Salary:"), row, 0, Qt.AlignmentFlag.AlignRight)
            base_salary_edit = QLineEdit(str(getattr(employee, 'base_salary', 0)))
            grid.addWidget(base_salary_edit, row, 1)
            row += 1
            
            # Hourly Rate
            grid.addWidget(QLabel("Hourly Rate:"), row, 0, Qt.AlignmentFlag.AlignRight)
            hourly_rate_edit = QLineEdit(str(getattr(employee, 'hourly_rate', 0)))
            grid.addWidget(hourly_rate_edit, row, 1)
            row += 1
            
            # SSS Number
            grid.addWidget(QLabel("SSS Number:"), row, 0, Qt.AlignmentFlag.AlignRight)
            sss_edit = QLineEdit(employee.sss_no or "")
            grid.addWidget(sss_edit, row, 1)
            row += 1
            
            # PhilHealth Number
            grid.addWidget(QLabel("PhilHealth Number:"), row, 0, Qt.AlignmentFlag.AlignRight)
            philhealth_edit = QLineEdit(employee.philhealth_no or "")
            grid.addWidget(philhealth_edit, row, 1)
            row += 1
            
            # Pag-IBIG Number
            grid.addWidget(QLabel("Pag-IBIG Number:"), row, 0, Qt.AlignmentFlag.AlignRight)
            pagibig_edit = QLineEdit(employee.pagibig_no or "")
            grid.addWidget(pagibig_edit, row, 1)
            row += 1
            
            # TIN Number
            grid.addWidget(QLabel("TIN Number:"), row, 0, Qt.AlignmentFlag.AlignRight)
            tin_edit = QLineEdit(employee.tin_no or "")
            grid.addWidget(tin_edit, row, 1)
            row += 1
            
            # Status
            grid.addWidget(QLabel("Status:"), row, 0, Qt.AlignmentFlag.AlignRight)
            status_combo = QComboBox()
            status_combo.addItems(["Active", "Inactive"])
            status_combo.setCurrentText("Active" if employee.is_active else "Inactive")
            grid.addWidget(status_combo, row, 1)
            
            layout.addLayout(grid)
            layout.addStretch()
            
            # Buttons
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setObjectName("CancelBtn")
            cancel_btn.setFixedWidth(120)
            cancel_btn.clicked.connect(dialog.reject)
            
            save_btn = QPushButton("Save Changes")
            save_btn.setObjectName("SaveBtn")
            save_btn.setFixedWidth(150)
            
            def save_changes():
                try:
                    # Validate inputs
                    if not first_name_edit.text().strip():
                        QMessageBox.warning(dialog, "Validation Error", "First name is required.")
                        return
                    
                    if not last_name_edit.text().strip():
                        QMessageBox.warning(dialog, "Validation Error", "Last name is required.")
                        return
                    
                    # Prepare update data
                    update_data = {
                        'first_name': first_name_edit.text().strip(),
                        'last_name': last_name_edit.text().strip(),
                        'position': position_edit.text().strip() or None,
                        'department_id': dept_combo.currentData(),
                        'date_hired': date_hired_edit.date().toPyDate(),
                        'salary_type': salary_type_combo.currentText(),
                        'base_salary': float(base_salary_edit.text()) if base_salary_edit.text() else 0,
                        'hourly_rate': float(hourly_rate_edit.text()) if hourly_rate_edit.text() else 0,
                        'sss_no': sss_edit.text().strip() or None,
                        'philhealth_no': philhealth_edit.text().strip() or None,
                        'pagibig_no': pagibig_edit.text().strip() or None,
                        'tin_no': tin_edit.text().strip() or None,
                        'is_active': 1 if status_combo.currentText() == "Active" else 0
                    }
                    
                    # Update employee
                    update_employee(employee.id, update_data)
                    
                    # Log audit
                    from models.audit_model import log_audit
                    log_audit(None, "Update Employee", f"Updated employee: {employee_code}")
                    
                    QMessageBox.information(dialog, "Success", f"Employee {employee_code} updated successfully!")
                    dialog.accept()
                    
                    # Reload employee list
                    self._load_employees()
                    
                except ValueError as ve:
                    QMessageBox.warning(dialog, "Validation Error", "Please enter valid numbers for salary fields.")
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Failed to update employee: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            save_btn.clicked.connect(save_changes)
            
            btn_layout.addWidget(cancel_btn)
            btn_layout.addSpacing(10)
            btn_layout.addWidget(save_btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit dialog: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _view_employee_attendance(self):
        """View attendance records for selected employee."""
        current_row = self.employee_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select an employee to view attendance.")
            return
        
        employee_code = self.employee_table.item(current_row, 0).text()
        
        try:
            from models.employee_model import get_employee_by_code
            from models.timekeeping_model import get_employee_attendance
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
            from datetime import date, timedelta
            
            employee = get_employee_by_code(employee_code)
            if not employee:
                QMessageBox.warning(self, "Error", "Employee not found.")
                return
            
            # Create attendance dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Attendance Records - {employee_code}")
            dialog.setFixedSize(800, 600)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #F2EBE9;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(30, 30, 30, 30)
            
            # Header
            header = QLabel(f"<b>Attendance Records - {employee.first_name} {employee.last_name}</b>")
            header.setStyleSheet("font-size: 18px; color: #333;")
            layout.addWidget(header)
            layout.addSpacing(15)
            
            # Get attendance records (last 60 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=60)
            records = get_employee_attendance(employee.id, start_date, end_date)
            
            # Table
            table = QTableWidget(len(records), 7)
            table.setHorizontalHeaderLabels(["Date", "Time In", "Time Out", "Hours", "Status", "Late (min)", "Overtime"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            
            for row, record in enumerate(records):
                att_date = record.get('attendance_date')
                if isinstance(att_date, str):
                    from datetime import datetime
                    att_date = datetime.strptime(att_date, '%Y-%m-%d').date()
                table.setItem(row, 0, QTableWidgetItem(str(att_date)))
                
                time_in = record.get('time_in')
                table.setItem(row, 1, QTableWidgetItem(str(time_in)[:5] if time_in else 'N/A'))
                
                time_out = record.get('time_out')
                table.setItem(row, 2, QTableWidgetItem(str(time_out)[:5] if time_out else 'N/A'))
                
                hours = float(record.get('hours_worked', 0))
                table.setItem(row, 3, QTableWidgetItem(f"{hours:.2f}"))
                
                status = record.get('status', 'N/A')
                table.setItem(row, 4, QTableWidgetItem(status))
                
                late_min = record.get('late_minutes', 0)
                table.setItem(row, 5, QTableWidgetItem(str(late_min)))
                
                ot_hours = float(record.get('overtime_hours', 0))
                table.setItem(row, 6, QTableWidgetItem(f"{ot_hours:.2f}"))
            
            layout.addWidget(table)
            layout.addSpacing(15)
            
            # Summary
            total_hours = sum(float(r.get('hours_worked', 0)) for r in records)
            summary = QLabel(f"<b>Summary:</b> {len(records)} records, Total Hours: {total_hours:.2f}")
            summary.setStyleSheet("font-size: 12px; color: #555;")
            layout.addWidget(summary)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.setProperty("class", "PrimaryBtn")
            close_btn.setFixedWidth(100)
            close_btn.clicked.connect(dialog.close)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load attendance: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _view_payroll_history(self):
        """View payroll history for selected employee."""
        current_row = self.employee_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select an employee to view payroll history.")
            return
        
        employee_code = self.employee_table.item(current_row, 0).text()
        
        try:
            from models.employee_model import get_employee_by_code
            from models.database import get_connection
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
            
            employee = get_employee_by_code(employee_code)
            if not employee:
                QMessageBox.warning(self, "Error", "Employee not found.")
                return
            
            # Create payroll history dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Payroll History - {employee_code}")
            dialog.setFixedSize(900, 600)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #F2EBE9;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(30, 30, 30, 30)
            
            # Header
            header = QLabel(f"<b>Payroll History - {employee.first_name} {employee.last_name}</b>")
            header.setStyleSheet("font-size: 18px; color: #333;")
            layout.addWidget(header)
            layout.addSpacing(15)
            
            # Get payroll history
            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("""
                        SELECT 
                            pp.name as period_name,
                            pp.start_date,
                            pp.end_date,
                            pe.basic_pay,
                            pe.overtime_pay,
                            pe.gross_pay,
                            pe.total_deductions,
                            pe.net_pay,
                            pe.status
                        FROM payroll_entries pe
                        JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
                        WHERE pe.employee_id = %s
                        ORDER BY pp.start_date DESC
                        LIMIT 12
                    """, (employee.id,))
                    records = cur.fetchall()
            
            # Table
            table = QTableWidget(len(records), 7)
            table.setHorizontalHeaderLabels(["Period", "Start Date", "End Date", "Gross Pay", "Deductions", "Net Pay", "Status"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            
            for row, record in enumerate(records):
                table.setItem(row, 0, QTableWidgetItem(record.get('period_name', 'N/A')))
                table.setItem(row, 1, QTableWidgetItem(str(record.get('start_date', 'N/A'))))
                table.setItem(row, 2, QTableWidgetItem(str(record.get('end_date', 'N/A'))))
                
                gross = float(record.get('gross_pay', 0))
                table.setItem(row, 3, QTableWidgetItem(f"PHP {gross:,.2f}"))
                
                deductions = float(record.get('total_deductions', 0))
                table.setItem(row, 4, QTableWidgetItem(f"PHP {deductions:,.2f}"))
                
                net = float(record.get('net_pay', 0))
                net_item = QTableWidgetItem(f"PHP {net:,.2f}")
                net_item.setForeground(QColor("#28a745"))
                from PyQt6.QtGui import QFont
                font = QFont()
                font.setBold(True)
                net_item.setFont(font)
                table.setItem(row, 5, net_item)
                
                status = record.get('status', 'N/A')
                status_item = QTableWidgetItem(status)
                if status == 'VERIFIED':
                    status_item.setForeground(QColor("#28a745"))
                elif status == 'PENDING':
                    status_item.setForeground(QColor("#FFA500"))
                table.setItem(row, 6, status_item)
            
            layout.addWidget(table)
            layout.addSpacing(15)
            
            # Summary
            if records:
                total_net = sum(float(r.get('net_pay', 0)) for r in records)
                summary = QLabel(f"<b>Summary:</b> {len(records)} periods, Total Net Pay: PHP {total_net:,.2f}")
                summary.setStyleSheet("font-size: 12px; color: #555;")
                layout.addWidget(summary)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.setProperty("class", "PrimaryBtn")
            close_btn.setFixedWidth(100)
            close_btn.clicked.connect(dialog.close)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load payroll history: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def refresh_data(self):
        """Refresh the employee list."""
        self._load_employees()

