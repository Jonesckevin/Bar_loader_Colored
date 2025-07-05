"""
Tools and utilities for the Barbell Calculator application.
Contains stopwatch, timer, and other tool-related functions.
"""

import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSpinBox, QWidget, QFrame
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont


class StopwatchDialog(QDialog):
    """A popup stopwatch dialog with start, stop, reset functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⏱️ Stopwatch")
        self.setModal(False)
        self.resize(300, 200)
        self.setMinimumSize(250, 150)
        
        # Timer state
        self.start_time = 0
        self.elapsed_time = 0
        self.is_running = False
        
        # Timer object
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.setInterval(10)  # Update every 10ms for precision
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Time display
        self.time_label = QLabel("00:00:00.00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.time_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        layout.addWidget(self.time_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_stop_btn = QPushButton("▶️ Start")
        self.start_stop_btn.clicked.connect(self.toggle_start_stop)
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_stopwatch)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ffb74d;
            }
            QPushButton:pressed {
                background-color: #f57c00;
            }
        """)
        
        button_layout.addWidget(self.start_stop_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)
        
    def toggle_start_stop(self):
        if self.is_running:
            self.stop_stopwatch()
        else:
            self.start_stopwatch()
            
    def start_stopwatch(self):
        self.start_time = time.time() - self.elapsed_time
        self.is_running = True
        self.timer.start()
        self.start_stop_btn.setText("⏸️ Stop")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ef5350;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
        """)
        
    def stop_stopwatch(self):
        self.timer.stop()
        self.is_running = False
        self.start_stop_btn.setText("▶️ Start")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        
    def reset_stopwatch(self):
        self.timer.stop()
        self.is_running = False
        self.elapsed_time = 0
        self.start_time = 0
        self.time_label.setText("00:00:00.00")
        self.start_stop_btn.setText("▶️ Start")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        
    def update_display(self):
        if self.is_running:
            self.elapsed_time = time.time() - self.start_time
        
        # Convert to hours, minutes, seconds, centiseconds
        total_centiseconds = int(self.elapsed_time * 100)
        hours = total_centiseconds // 360000
        minutes = (total_centiseconds % 360000) // 6000
        seconds = (total_centiseconds % 6000) // 100
        centiseconds = total_centiseconds % 100
        
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        self.time_label.setText(time_text)


class TimerDialog(QDialog):
    """A popup countdown timer dialog with customizable time."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⏰ Timer")
        self.setModal(False)
        self.resize(300, 250)
        self.setMinimumSize(250, 200)
        
        # Timer state
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False
        
        # Timer object
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.setInterval(1000)  # Update every second
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Time input controls
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Hours:"))
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 23)
        self.hours_spin.setValue(0)
        input_layout.addWidget(self.hours_spin)
        
        input_layout.addWidget(QLabel("Minutes:"))
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setValue(5)  # Default 5 minutes
        input_layout.addWidget(self.minutes_spin)
        
        input_layout.addWidget(QLabel("Seconds:"))
        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setValue(0)
        input_layout.addWidget(self.seconds_spin)
        
        layout.addLayout(input_layout)
        
        # Time display
        self.time_label = QLabel("00:05:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.time_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #ffaa00;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        layout.addWidget(self.time_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_stop_btn = QPushButton("▶️ Start")
        self.start_stop_btn.clicked.connect(self.toggle_start_stop)
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ffb74d;
            }
            QPushButton:pressed {
                background-color: #f57c00;
            }
        """)
        
        button_layout.addWidget(self.start_stop_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)
        
        # Connect spinbox changes to update display
        self.hours_spin.valueChanged.connect(self.update_time_from_inputs)
        self.minutes_spin.valueChanged.connect(self.update_time_from_inputs)
        self.seconds_spin.valueChanged.connect(self.update_time_from_inputs)
        
    def update_time_from_inputs(self):
        if not self.is_running:
            hours = self.hours_spin.value()
            minutes = self.minutes_spin.value()
            seconds = self.seconds_spin.value()
            self.total_seconds = hours * 3600 + minutes * 60 + seconds
            self.remaining_seconds = self.total_seconds
            self.update_display()
        
    def toggle_start_stop(self):
        if self.is_running:
            self.stop_timer()
        else:
            self.start_timer()
            
    def start_timer(self):
        if self.remaining_seconds <= 0:
            self.update_time_from_inputs()
        
        if self.remaining_seconds > 0:
            self.is_running = True
            self.timer.start()
            self.start_stop_btn.setText("⏸️ Stop")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #ef5350;
                }
                QPushButton:pressed {
                    background-color: #d32f2f;
                }
            """)
        
    def stop_timer(self):
        self.timer.stop()
        self.is_running = False
        self.start_stop_btn.setText("▶️ Start")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        
    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.update_time_from_inputs()
        self.start_stop_btn.setText("▶️ Start")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        
    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()
        else:
            # Timer finished
            self.timer.stop()
            self.is_running = False
            self.start_stop_btn.setText("▶️ Start")
            self.time_label.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    color: #ff0000;
                    border: 2px solid #ff0000;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
            self.time_label.setText("TIME'S UP!")
        
    def update_display(self):
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_label.setText(time_text)
        
        # Change color as time runs out
        if self.remaining_seconds <= 10 and self.remaining_seconds > 0:
            self.time_label.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    color: #ff0000;
                    border: 2px solid #333333;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
        elif self.remaining_seconds <= 60:
            self.time_label.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    color: #ff8800;
                    border: 2px solid #333333;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
        else:
            self.time_label.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    color: #ffaa00;
                    border: 2px solid #333333;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }
            """)


def get_powerlifting_rules_url(federation="IPF") -> str:
    """Get the rules URL for different powerlifting federations."""
    rules_urls = {
        "IPF": "https://www.powerlifting.sport/rules/codes/info/technical-rules",
        "USPAL": "https://www.usapowerlifting.com/rules-bylaws/",
        "RPS": "https://www.revolutionpowerlifting.com/rulebook/",
        "SPF": "https://www.southernpowerlifting.com/spf-rule-book/",
        "IPA": "https://ipapower.com/ipa-rules/",
        "NASA": "https://nasa-sports.com/rulebook/"
    }
    return rules_urls.get(federation, rules_urls["IPF"])


def open_rules_link(federation="IPF"):
    """Open the powerlifting rules URL in the default browser."""
    from PyQt6.QtGui import QDesktopServices
    from PyQt6.QtCore import QUrl
    
    url = get_powerlifting_rules_url(federation)
    QDesktopServices.openUrl(QUrl(url))
