from __future__ import annotations

import logging

from PyQt6.QtWidgets import QMessageBox

from models import user_model
from utils.security import verify_password
from views.main_window import MainWindow
from views.hr_main_window import HrMainWindow
from views.accountant_main_window import AccountantMainWindow
from views.employee_main_window import EmployeeMainWindow
from views.admin_main_window import AdminMainWindow


logger = logging.getLogger(__name__)


class AuthController:
    """
    Wires the login view to the backend user model and opens the appropriate main window.
    """

    def __init__(self, login_view):
        self.login_view = login_view
        self.main_window = None  # Will hold the main window after login
        self._connect_signals()

    def _connect_signals(self):
        # Connect the login button click signal
        if hasattr(self.login_view, 'login_button'):
            # Disconnect any existing connections first (in case of multiple calls)
            try:
                self.login_view.login_button.clicked.disconnect()
            except TypeError:
                # No connections exist yet, that's fine
                pass
            except Exception as e:
                logger.warning("Error disconnecting signal: %s", e)
            
            # Clear input fields to ensure clean state
            if hasattr(self.login_view, 'user_input'):
                self.login_view.user_input.clear()
            if hasattr(self.login_view, 'pass_input'):
                self.login_view.pass_input.clear()
            
            # Connect the handler
            self.login_view.login_button.clicked.connect(self.handle_login)
            receivers = self.login_view.login_button.receivers(self.login_view.login_button.clicked)
            logger.debug("Login button signal connected successfully. Receivers: %s", receivers)
        else:
            logger.error("Login button not found in login_view!")

    def handle_login(self):
        logger.debug("Login button clicked")
        username = self.login_view.user_input.text().strip()
        password = self.login_view.pass_input.text().strip()
        logger.debug("Username: %s, Password length: %s", username, len(password) if password else 0)

        if not username or not password:
            QMessageBox.warning(self.login_view, "Login Failed", "Please enter username and password.")
            # Clear password field for security
            self.login_view.pass_input.clear()
            return

        try:
            user = user_model.get_user_by_username(username)
            logger.debug("User lookup result: %s", user.username if user else "None")
            if not user:
                QMessageBox.warning(self.login_view, "Login Failed", 
                    f"User '{username}' not found.\n\nAvailable users:\n- admin / admin123\n- hr_officer / hr123\n- accountant / acc123\n- employee1 / emp123")
                # Clear password field for security
                self.login_view.pass_input.clear()
                return
            
            if not user.is_active:
                QMessageBox.warning(self.login_view, "Login Failed", "This account is inactive.")
                # Clear password field for security
                self.login_view.pass_input.clear()
                return

            is_match = verify_password(password, user.password_hash)
            logger.debug("Password hash match: %s", is_match)
            if not is_match:
                QMessageBox.warning(self.login_view, "Login Failed", 
                    "Invalid password.\n\nAvailable users:\n- admin / admin123\n- hr_officer / hr123\n- accountant / acc123\n- employee1 / emp123")
                # Clear password field for security
                self.login_view.pass_input.clear()
                return
            
            logger.info("Login successful for user: %s, role: %s", username, user.role_name)
            
            # Log the login action
            from models.audit_model import log_audit
            log_audit(user.id, "Login", f"User logged in successfully: {username}")
            
        except Exception as e:
            QMessageBox.critical(self.login_view, "Login Error", f"An error occurred: {str(e)}\n\nPlease check database connection.")
            logger.exception("Login error: %s", e)
            return

        # Successful login: open main window based on role
        role = user.role_name

        if role == "HR Officer":
            self.main_window = HrMainWindow(user=user)
        elif role == "Accountant":
            self.main_window = AccountantMainWindow(user=user)
        elif role == "Employee":
            self.main_window = EmployeeMainWindow(user=user)
        elif role == "Administrator":
            self.main_window = AdminMainWindow(user=user)
        else:
            self.main_window = MainWindow(role=role)

        self.main_window.show()
        self.login_view.close()



