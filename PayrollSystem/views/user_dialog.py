from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QGridLayout,
    QFrame,
)

from services.user_service import create_user, update_user


class UserDialog(QDialog):
    """Dialog for adding or editing users."""

    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit_mode = user_data is not None

        self.setWindowTitle("Edit User" if self.is_edit_mode else "Add New User")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #F2EBE9;
            }
            QLabel {
                font-size: 13px;
                color: #333333;
                font-weight: 600;
                background-color: transparent;
            }
            QLineEdit, QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #D6CDC6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #333;
                min-height: 30px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #F0D095;
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

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Edit User Details" if self.is_edit_mode else "Create New User")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #333;")
        layout.addWidget(title)

        # Form
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(15)
        form_layout.setColumnMinimumWidth(0, 120)

        # Username
        form_layout.addWidget(QLabel("Username:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        if self.is_edit_mode:
            self.username_edit.setText(self.user_data.get('username', ''))
            self.username_edit.setReadOnly(True)  # Username cannot be changed
        form_layout.addWidget(self.username_edit, 0, 1)

        # Password
        form_layout.addWidget(QLabel("Password:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        if self.is_edit_mode:
            self.password_edit.setPlaceholderText("Leave blank to keep current password")
        else:
            self.password_edit.setPlaceholderText("Enter password")
        form_layout.addWidget(self.password_edit, 1, 1)

        # Role
        form_layout.addWidget(QLabel("Role:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Administrator", "HR Officer", "Accountant", "Employee"])
        if self.is_edit_mode and self.user_data.get('role'):
            index = self.role_combo.findText(self.user_data['role'])
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
        form_layout.addWidget(self.role_combo, 2, 1)

        # Status
        form_layout.addWidget(QLabel("Status:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        if self.is_edit_mode:
            status = "Active" if self.user_data.get('status') == 'Active' else "Inactive"
            self.status_combo.setCurrentText(status)
        form_layout.addWidget(self.status_combo, 3, 1)

        # Employee Code (optional, for Employee role)
        form_layout.addWidget(QLabel("Employee Code:"), 4, 0, Qt.AlignmentFlag.AlignRight)
        self.employee_code_edit = QLineEdit()
        self.employee_code_edit.setPlaceholderText("Optional: Link to employee (e.g., EMP001)")
        if self.is_edit_mode:
            self.employee_code_edit.setText(self.user_data.get('employee_code', ''))
        form_layout.addWidget(self.employee_code_edit, 4, 1)

        layout.addLayout(form_layout)
        layout.addSpacing(10)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton("Save" if self.is_edit_mode else "Create")
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.setFixedWidth(120)
        self.save_btn.clicked.connect(self._save)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.setFixedWidth(120)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _save(self):
        """Validate and save user data."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        role = self.role_combo.currentText()
        status = self.status_combo.currentText()
        employee_code = self.employee_code_edit.text().strip()

        # Delegate to service layer
        is_active = status == "Active"

        if self.is_edit_mode:
            success = update_user(
                username=username,
                role_name=role,
                is_active=is_active,
                new_password=password or None,
                parent_widget=self,
            )
        else:
            success = create_user(
                username=username,
                password=password,
                role_name=role,
                is_active=is_active,
                parent_widget=self,
            )

        if success:
            self.accept()  # Close dialog with success

    def get_result(self):
        """Get the result data."""
        return {
            'username': self.username_edit.text().strip(),
            'role': self.role_combo.currentText(),
            'status': self.status_combo.currentText(),
            'employee_code': self.employee_code_edit.text().strip(),
        }

