import sys
import logging

from PyQt6.QtWidgets import QApplication

from controllers.auth_controller import AuthController
from models.database import init_database
from models.migrate_payslip_fields import migrate_payslip_fields
from models.seed_data import seed_database
from utils.logging_config import configure_logging
from views.login_view import LoginWindow


logger = logging.getLogger(__name__)


def main():
    # Configure logging once at application startup
    configure_logging()

    # Ensure database and core tables exist before showing UI
    init_database()
    # Initialize integration tables (Solution 2: Centralized Data Integration)
    try:
        from models.integration_model import init_integration_tables
        init_integration_tables()
    except Exception as e:
        logger.warning("Integration tables may have already been initialized or failed to initialize: %s", e)
    # Initialize leave balance tables (Solution 3: Employee Self-Service)
    try:
        from models.leave_balance_model import init_leave_balance_tables
        init_leave_balance_tables()
    except Exception as e:
        logger.warning("Leave balance tables may have already been initialized or failed to initialize: %s", e)
    # Run migration to add payslip fields
    try:
        migrate_payslip_fields()
    except Exception as e:
        logger.warning("Migration may have already run or failed: %s", e)
    # Seed database with sample data
    try:
        seed_database()
    except Exception as e:
        logger.warning("Seed data may already exist or failed to seed: %s", e)

    app = QApplication(sys.argv)
    login_view = LoginWindow()
    # Store AuthController instance to prevent garbage collection
    auth_controller = AuthController(login_view)
    login_view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



