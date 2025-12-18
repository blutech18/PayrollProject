from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
)


class SideMenu(QWidget):
    """
    Left vertical menu matching the Proly wireframe.
    Items can be configured per role (HR, Accountant, Employee, Admin).
    """

    def __init__(self, menu_items, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f0d7aa;
            }
            QLabel#Brand {
                font-size: 20px;
                font-weight: 700;
                color: #3b3b3b;
            }
            QLabel#MenuTitle {
                font-size: 11px;
                color: #7b6b5a;
                margin-left: 16px;
            }
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 10px 16px;
                margin: 2px 0;
                color: #3b3b3b;
            }
            QListWidget::item:selected {
                background-color: #e5c69b;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        brand = QLabel("Proly")
        brand.setObjectName("Brand")

        root.addWidget(brand)

        menu_label = QLabel("MENU")
        menu_label.setObjectName("MenuTitle")
        root.addWidget(menu_label)

        self.list = QListWidget()
        for text in menu_items:
            item = QListWidgetItem(text)
            self.list.addItem(item)

        root.addWidget(self.list)
        root.addStretch()


class TopBar(QWidget):
    """
    Top horizontal bar with search box, role label, and logout icon placeholder.
    """

    def __init__(self, role_label: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f3d7aa;
            }
            QLineEdit {
                background-color: #fdf7ea;
                border-radius: 16px;
                border: none;
                padding: 8px 12px;
            }
            QLabel#RoleLabel {
                font-weight: 600;
                color: #3b3b3b;
            }
            QPushButton#LogoutButton {
                border: none;
                background-color: #3b3b3b;
                color: #fdf7ea;
                border-radius: 14px;
                padding: 4px 10px;
            }
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(16)

        from PyQt6.QtWidgets import QLineEdit

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search")

        layout.addWidget(self.search_edit, 1)
        layout.addStretch()

        role = QLabel(role_label)
        role.setObjectName("RoleLabel")
        layout.addWidget(role)

        logout = QPushButton("⎋")
        logout.setObjectName("LogoutButton")
        layout.addWidget(logout)


class PlaceholderPage(QWidget):
    """
    Simple card-like placeholder for each screen.
    You can later replace the inner layout with full forms/tables.
    """

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f3e4e4;
            }
            QFrame#Card {
                background-color: #f7e6c3;
                border-radius: 24px;
            }
            QLabel#Title {
                font-size: 22px;
                font-weight: 700;
                color: #4a4a4a;
            }
            """
        )
        from PyQt6.QtWidgets import QFrame

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)

        title_label = QLabel(title)
        title_label.setObjectName("Title")
        root.addWidget(title_label)
        root.addSpacing(16)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.addStretch()

        hint = QLabel("Design this section to match the wireframe for: " + title)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(hint)

        root.addWidget(card, 1)


class MainWindow(QMainWindow):
    """
    Main application window with side menu, top bar and stacked pages.
    Fallback window for different user roles with placeholder pages.
    HR Officer: Dashboard, Employee Registration, Payroll Computation, Reports
    Accountant: Dashboard, Payroll Computation, Reports, Payroll Verification
    Employee: Dashboard, Payslip Viewing
    Administrator: Dashboard, Employee Registration, User Management, Audit Logs, System Maintenance
    """

    def __init__(self, role: str = "HR Officer", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Proly - {role}")
        self.resize(1280, 720)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Configure menu items per role – you can extend this later.
        if role == "HR Officer":
            menu_items = ["Dashboard", "Employee Registration", "Payroll Computation", "Reports"]
        elif role == "Accountant":
            menu_items = ["Dashboard", "Payroll Computation", "Reports", "Payroll Verification"]
        elif role == "Employee":
            menu_items = ["Dashboard", "Payslip Viewing"]
        else:  # Admin
            menu_items = ["Dashboard", "Employee Registration", "User Management", "Audit Logs", "System Maintenance"]

        self.side_menu = SideMenu(menu_items)
        main_layout.addWidget(self.side_menu)

        # Right side: vertical layout with top bar and stacked pages
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.top_bar = TopBar(role)
        right_layout.addWidget(self.top_bar)

        self.stack = QStackedWidget()
        for item in menu_items:
            self.stack.addWidget(PlaceholderPage(item.upper()))

        right_layout.addWidget(self.stack, 1)
        main_layout.addWidget(right, 1)

        self.side_menu.list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.side_menu.list.setCurrentRow(0)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow("HR Officer")
    w.show()
    sys.exit(app.exec())


