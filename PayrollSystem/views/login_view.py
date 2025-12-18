import sys
import os
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QWidget, QFrame, 
    QGraphicsDropShadowEffect
)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PROLY - Login")
        self.resize(1080, 720)
        
        # Load the background image
        bg_path = Path(__file__).parent.parent / "assets" / "images" / "loginBackground.png"
        self.bg_pixmap = QPixmap(str(bg_path))
        
        self._setup_ui()

    def paintEvent(self, event):
        """Draws the gradient background AND the overlay image"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. FIX: Draw the Gradient Background matching the wireframe
        # Instead of solid black, we use the specific grey gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#8c8c8c")) # Lighter Grey (Top)
        gradient.setColorAt(1.0, QColor("#4a4a4a")) # Darker Charcoal (Bottom)
        painter.fillRect(self.rect(), gradient)
        
        # 2. Draw the background image as an overlay
        if not self.bg_pixmap.isNull():
            # Scale the image to fill width while keeping aspect ratio
            scaled_pixmap = self.bg_pixmap.scaled(
                self.width(),
                self.bg_pixmap.height() * self.width() // self.bg_pixmap.width(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Align image to bottom center
            x = (self.width() - scaled_pixmap.width()) // 2
            y = self.height() - scaled_pixmap.height()
            
            # Optional: Set opacity if you want the gradient to blend through the image
            # painter.setOpacity(0.8) 
            
            painter.drawPixmap(x, y, scaled_pixmap)
        
        # We do NOT call super().paintEvent(event) for QWidget custom painting
        # to ensure our background stays exactly as we drew it.

    def _setup_ui(self):
        # 1. Main Window Styling
        # We set background to transparent so the paintEvent (gradient) is visible
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                font-family: 'Segoe UI', sans-serif;
            }            
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 2. The Card Frame
        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setFixedSize(480, 580)
        
        # Drop shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)

        # 3. Card Styling (Sand/Beige Theme)
        self.card.setStyleSheet("""
            QFrame#LoginCard {
                background-color: #333333; /* Dark Charcoal */
                border-radius: 20px;
            }
            QLabel {
                background: transparent;
            }
            QLabel#Title {
                color: #E8E0D5;
                font-size: 48px;
                font-weight: 800;
                letter-spacing: 2px;
            }
            QLabel#FieldLabel {
                color: #C0C0C0;
                font-size: 13px;
                font-weight: 500;
                margin-bottom: 2px;
            }
            QLineEdit {
                background-color: #E6E1D5;
                border: none;
                border-radius: 4px;
                padding: 12px 15px;
                font-size: 14px;
                color: #333333;
                selection-background-color: #A0A0A0;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
            QPushButton#LoginButton {
                background-color: #DCC08E;
                color: #2b2b2b;
                font-size: 14px;
                font-weight: 900;
                letter-spacing: 1px;
                border-radius: 4px;
                padding: 14px;
            }
            QPushButton#LoginButton:hover {
                background-color: #E6D0A0;
            }
            QPushButton#LoginButton:pressed {
                background-color: #C4AA7D;
            }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(50, 40, 50, 50)
        card_layout.setSpacing(15)

        # -- Logo Section --
        logo_container = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setFixedSize(96, 96)
        logo_label.setStyleSheet("background: transparent;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Load logo
        try:
            logo_path = Path(__file__).parent.parent / "assets" / "images" / "logo.png"
            pix = QPixmap(str(logo_path))
            if not pix.isNull():
                logo_label.setScaledContents(True)
                logo_label.setPixmap(pix)
            else:
                # Fallback text logo
                logo_label.setText("PL")
                logo_label.setStyleSheet(
                    "background-color: #1f232b; border-radius: 48px; "
                    "color: #DCC08E; font-weight: bold; font-size: 24px;"
                )
        except Exception:
            pass

        logo_container.addStretch()
        logo_container.addWidget(logo_label)
        logo_container.addStretch()

        # -- Title Section --
        title_label = QLabel("PROLY")
        title_label.setObjectName("Title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # -- Form Section --
        user_label = QLabel("Username")
        user_label.setObjectName("FieldLabel")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("")
        self.user_input.clear()  # Ensure field is empty on initialization
        
        pass_label = QLabel("Password")
        pass_label.setObjectName("FieldLabel")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("")
        self.pass_input.clear()  # Ensure field is empty on initialization

        # -- Button Section --
        self.login_button = QPushButton("LOGIN")
        self.login_button.setObjectName("LoginButton")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setEnabled(True)  # Ensure button is enabled
        
        # Connect Enter key from password field to trigger login
        self.pass_input.returnPressed.connect(lambda: self.login_button.click())

        # Add to Layout
        card_layout.addLayout(logo_container)
        card_layout.addSpacing(10)
        card_layout.addWidget(title_label)
        card_layout.addSpacing(30)
        
        card_layout.addWidget(user_label)
        card_layout.addWidget(self.user_input)
        card_layout.addSpacing(5)
        card_layout.addWidget(pass_label)
        card_layout.addWidget(self.pass_input)
        
        card_layout.addStretch()
        card_layout.addWidget(self.login_button)

        main_layout.addWidget(self.card)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())