"""
Employee Timekeeping View - Time-In/Time-Out Interface
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional
import logging

from PyQt6.QtCore import Qt, QTimer
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
)

from .employee_main_window import ShadowCard


logger = logging.getLogger(__name__)


class EmployeeTimekeepingView(QWidget):
    """Time-In/Time-Out view for employees."""

    def __init__(self, employee_id: Optional[int] = None, user_id: Optional[int] = None):
        super().__init__()
        self.employee_id = employee_id
        self.user_id = user_id
        self.current_attendance = None
        
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

        # Time-In/Time-Out Card
        timecard = ShadowCard()
        timecard.setMinimumWidth(700)
        timecard.setMaximumWidth(900)
        timecard.setMinimumHeight(400)
        tc_layout = QVBoxLayout(timecard)
        tc_layout.setContentsMargins(50, 40, 50, 40)

        # Title
        title = QLabel("TIME IN / TIME OUT")
        title.setStyleSheet("font-size:24px; font-weight:800; color:#444; qproperty-alignment:AlignCenter;")
        tc_layout.addWidget(title)
        tc_layout.addSpacing(30)

        # Current Date/Time Display
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("font-size:18px; font-weight:600; color:#555; qproperty-alignment:AlignCenter;")
        self._update_datetime()
        tc_layout.addWidget(self.datetime_label)

        # Timer to update datetime every second
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self._update_datetime)
        self.datetime_timer.start(1000)  # Update every second

        tc_layout.addSpacing(30)

        # Status Display
        self.status_label = QLabel("Status: Not checked in")
        self.status_label.setStyleSheet("font-size:16px; color:#666; qproperty-alignment:AlignCenter;")
        tc_layout.addWidget(self.status_label)

        self.time_in_label = QLabel("Time In: --:--")
        self.time_in_label.setStyleSheet("font-size:14px; color:#555; qproperty-alignment:AlignCenter;")
        tc_layout.addWidget(self.time_in_label)

        self.time_out_label = QLabel("Time Out: --:--")
        self.time_out_label.setStyleSheet("font-size:14px; color:#555; qproperty-alignment:AlignCenter;")
        tc_layout.addWidget(self.time_out_label)

        self.hours_label = QLabel("Hours Worked: 0.00")
        self.hours_label.setStyleSheet("font-size:14px; color:#555; qproperty-alignment:AlignCenter;")
        tc_layout.addWidget(self.hours_label)

        tc_layout.addSpacing(30)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.time_in_btn = QPushButton("🕐 TIME IN")
        self.time_in_btn.setProperty("class", "PrimaryBtn")
        self.time_in_btn.setFixedWidth(200)
        self.time_in_btn.setFixedHeight(60)
        self.time_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                border: 2px solid #1e7e34;
                border-radius: 8px;
                padding: 15px;
                font-weight: 700;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #ccc;
                border-color: #999;
            }
        """)
        self.time_in_btn.clicked.connect(self._handle_time_in)

        self.time_out_btn = QPushButton("🕐 TIME OUT")
        self.time_out_btn.setProperty("class", "PrimaryBtn")
        self.time_out_btn.setFixedWidth(200)
        self.time_out_btn.setFixedHeight(60)
        self.time_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border: 2px solid #c82333;
                border-radius: 8px;
                padding: 15px;
                font-weight: 700;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #ccc;
                border-color: #999;
            }
        """)
        self.time_out_btn.clicked.connect(self._handle_time_out)
        self.time_out_btn.setEnabled(False)

        btn_layout.addWidget(self.time_in_btn)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(self.time_out_btn)
        btn_layout.addStretch()

        tc_layout.addLayout(btn_layout)
        tc_layout.addStretch()

        # Center the timecard
        timecard_container = QHBoxLayout()
        timecard_container.addStretch()
        timecard_container.addWidget(timecard)
        timecard_container.addStretch()
        layout.addLayout(timecard_container)

        # Recent Attendance History
        history_card = ShadowCard()
        history_card.setMinimumWidth(900)
        history_card.setMaximumWidth(1200)
        history_card.setMinimumHeight(400)
        hc_layout = QVBoxLayout(history_card)
        hc_layout.setContentsMargins(40, 40, 40, 40)

        hc_layout.addWidget(QLabel("RECENT ATTENDANCE", styleSheet="font-size:18px; font-weight:800; color:#444;"))
        hc_layout.addSpacing(20)

        self.attendance_table = QTableWidget(0, 6)
        self.attendance_table.setHorizontalHeaderLabels(["Date", "Time In", "Time Out", "Hours", "Status", "Overtime"])
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.attendance_table.verticalHeader().setVisible(False)
        self.attendance_table.setAlternatingRowColors(True)
        
        # Style with white text
        self.attendance_table.setStyleSheet("""
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
        hc_layout.addWidget(self.attendance_table)

        # Center the history card
        history_card_container = QHBoxLayout()
        history_card_container.addStretch()
        history_card_container.addWidget(history_card)
        history_card_container.addStretch()
        layout.addLayout(history_card_container)
        
        layout.addStretch()
        scroll.setWidget(content_widget)

        if self.employee_id:
            self._load_today_attendance()
            self._load_recent_attendance()

    def set_employee_id(self, employee_id: Optional[int]):
        self.employee_id = employee_id
        self.refresh_data()

    def _update_datetime(self):
        """Update the current date/time display."""
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%A, %B %d, %Y\n%I:%M:%S %p"))

    def _load_today_attendance(self):
        """Load today's attendance record."""
        if not self.employee_id:
            return

        try:
            from models.timekeeping_model import get_today_attendance

            attendance = get_today_attendance(self.employee_id)
            self.current_attendance = attendance

            if attendance:
                if attendance.get('time_in'):
                    time_in_str = str(attendance['time_in'])
                    if len(time_in_str) >= 5:
                        time_in_str = time_in_str[:5]  # HH:MM format
                    self.time_in_label.setText(f"Time In: {time_in_str}")
                    self.status_label.setText("Status: Checked In")
                    self.time_in_btn.setEnabled(False)
                    self.time_out_btn.setEnabled(True)

                if attendance.get('time_out'):
                    time_out_str = str(attendance['time_out'])
                    if len(time_out_str) >= 5:
                        time_out_str = time_out_str[:5]
                    self.time_out_label.setText(f"Time Out: {time_out_str}")
                    self.status_label.setText("Status: Checked Out")
                    self.time_out_btn.setEnabled(False)
                    hours = float(attendance.get('hours_worked', 0))
                    self.hours_label.setText(f"Hours Worked: {hours:.2f}")
                else:
                    self.time_out_label.setText("Time Out: --:--")
                    self.hours_label.setText("Hours Worked: 0.00")
            else:
                self.status_label.setText("Status: Not checked in")
                self.time_in_label.setText("Time In: --:--")
                self.time_out_label.setText("Time Out: --:--")
                self.hours_label.setText("Hours Worked: 0.00")
                self.time_in_btn.setEnabled(True)
                self.time_out_btn.setEnabled(False)
        except Exception as e:
            logger.exception("Error loading today's attendance: %s", e)

    def _load_recent_attendance(self):
        """Load recent attendance history."""
        if not self.employee_id:
            return

        try:
            from models.timekeeping_model import get_employee_attendance
            from datetime import timedelta

            end_date = date.today()
            start_date = end_date - timedelta(days=14)  # Last 14 days

            records = get_employee_attendance(self.employee_id, start_date, end_date)

            self.attendance_table.setRowCount(len(records))
            for row, record in enumerate(records):
                # Date
                att_date = record.get('attendance_date')
                if isinstance(att_date, str):
                    att_date = datetime.strptime(att_date, '%Y-%m-%d').date()
                self.attendance_table.setItem(row, 0, QTableWidgetItem(att_date.strftime('%Y-%m-%d')))

                # Time In
                time_in = record.get('time_in')
                time_in_str = str(time_in)[:5] if time_in else '--:--'
                self.attendance_table.setItem(row, 1, QTableWidgetItem(time_in_str))

                # Time Out
                time_out = record.get('time_out')
                time_out_str = str(time_out)[:5] if time_out else '--:--'
                self.attendance_table.setItem(row, 2, QTableWidgetItem(time_out_str))

                # Hours
                hours = float(record.get('hours_worked', 0))
                self.attendance_table.setItem(row, 3, QTableWidgetItem(f"{hours:.2f}"))

                # Status
                status = record.get('status', 'N/A')
                self.attendance_table.setItem(row, 4, QTableWidgetItem(status))

                # Overtime
                ot_hours = float(record.get('overtime_hours', 0))
                self.attendance_table.setItem(row, 5, QTableWidgetItem(f"{ot_hours:.2f}"))
        except Exception as e:
            logger.exception("Error loading attendance history: %s", e)

    def _handle_time_in(self):
        """Handle time-in button click."""
        if not self.employee_id:
            QMessageBox.warning(self, "Error", "Employee ID not set.")
            return

        try:
            from models.timekeeping_model import time_in

            success, message = time_in(self.employee_id, user_id=self.user_id)

            if success:
                QMessageBox.information(self, "Success", message)
                self._load_today_attendance()
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record time-in: {str(e)}")
            import traceback
            traceback.print_exc()

    def _handle_time_out(self):
        """Handle time-out button click."""
        if not self.employee_id:
            QMessageBox.warning(self, "Error", "Employee ID not set.")
            return

        try:
            from models.timekeeping_model import time_out

            success, message, attendance_data = time_out(self.employee_id, user_id=self.user_id)

            if success:
                msg = f"{message}\n\n"
                if attendance_data:
                    msg += f"Hours Worked: {attendance_data.get('hours_worked', 0):.2f}\n"
                    if attendance_data.get('overtime_hours', 0) > 0:
                        msg += f"Overtime Hours: {attendance_data.get('overtime_hours', 0):.2f}\n"
                    if attendance_data.get('late_minutes', 0) > 0:
                        msg += f"Late: {attendance_data.get('late_minutes', 0)} minutes\n"
                QMessageBox.information(self, "Success", msg)
                self._load_today_attendance()
                self._load_recent_attendance()
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record time-out: {str(e)}")
            import traceback
            traceback.print_exc()

    def refresh_data(self):
        """Refresh the data display."""
        if self.employee_id:
            self._load_today_attendance()
            self._load_recent_attendance()

