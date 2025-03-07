import sys
import threading
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from UI.FullDataPage import FullDataPage
from UI.ReferencePointPage import ReferencePointPage
from Threading.SerialThread import SerialThread

def setup_toggle_button(button, phrase1, phrase2, home_page_instance):
    button.setCheckable(True)

    def toggle_button():
        if button.isChecked():
            button.setStyleSheet("background-color: green")
            button.setText(phrase1)
            home_page_instance.start_serial_thread()

        else:
            button.setChecked(False)
            button.setStyleSheet("")
            button.setText(phrase2)
            home_page_instance.stop_serial_thread()

    button.clicked.connect(toggle_button)

class HomePage(QWidget):
    def __init__(self):
        # Create Window
        super().__init__()
        self.setGeometry(1200, 300, 750, 750)
        self.setWindowTitle("Microstrip Patch Antenna Home Screen")

        # Create VBox Layout
        hbox00 = QHBoxLayout()
        hbox01 = QHBoxLayout()

        # Add TextFields
        self.antennaLabel = QLabel("Antenna 1 Status: ", self)
        self.antennaLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.antennaLabel.setFixedSize(200, 30)
        self.antennaLabel.move(10,10)
        # hbox00.addWidget((self.antennaLabel))

        self.connectionLabel = QLabel("Not Connected", self)
        self.connectionLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.connectionLabel.setFixedSize(200,30)
        self.connectionLabel.move(250,10)
        # grid_layout.addWidget((self.connectionLabel))

        self.solutionLabel = QLabel("Select Solution Type:", self)
        self.solutionLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.solutionLabel.setFixedSize(200,30)
        self.solutionLabel.move(10,120)
        # hbox01.addWidget((self.solutionLabel))

        self.timeLastReadingLabel = QLabel("Time since last reading: xx:xx", self)
        self.timeLastReadingLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.timeLastReadingLabel.setFixedSize(250,30)
        self.timeLastReadingLabel.move(10,200)

        self.valueLastReadingLabel = QLabel("Value of last reading: x cm", self)
        self.valueLastReadingLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.valueLastReadingLabel.setFixedSize(250,30)
        self.valueLastReadingLabel.move(10,220)

        # Add checkbox
        self.connectionCheckbox = QCheckBox("", self)
        self.connectionCheckbox.setFixedSize(30,30)
        self.connectionCheckbox.move(200,10)
        # hbox00.addWidget((self.connectionCheckbox))

        # Check connection
        # self.connectionCheckbox.stateChanged.connect(self.check_connection)

        # Add Record Button
        self.record_btn = QPushButton("Start Recording Data", self)
        self.record_btn.setFixedSize(200, 50)
        self.record_btn.move(220, 150)
        setup_toggle_button(self.record_btn, "Stop Recording Data", "Start Recording Data", self)

        # Add View Full Data Button
        self.dataPage_btn = QPushButton("View Full Data", self)
        self.dataPage_btn.setFixedSize(200, 50)
        self.dataPage_btn.move(430, 150)
        self.dataPage_btn.clicked.connect(self.open_data_page)

        # Dropdown
        self.solutionDropdown = QComboBox(self)
        self.solutionDropdown.addItems(["Saline Solution", "Distilled Solution", "Tap Solution"])
        self.solutionDropdown.setFixedSize(200, 50)
        self.solutionDropdown.move(10, 150)

        # Enter Reference Point Button
        self.referencepoint_btn = QPushButton("Enter Reference Point", self)
        self.referencepoint_btn.setFixedSize(175, 50)
        self.referencepoint_btn.move(10, 55)
        self.referencepoint_btn.clicked.connect(self.open_reference_page)

        # Reference Point Label
        self.currentReferenceLabel = QLabel("Current Reference Point: xx cm", self)
        self.currentReferenceLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.currentReferenceLabel.setFixedSize(275,30)
        self.currentReferenceLabel.move(195,65)

        # Create a current reference point
        self.current_reference_point = "xx"

        # Start Serial Communication
        self.serial_thread = None
        self.thread = None
        # self.is_recording = False

        # Initialize FullDataPage
        self.full_data_page = None

    def update_checkbox(self, data):
        if data == b'\x41':
            self.connectionCheckbox.setChecked(True)
            self.connectionLabel.setText("Connected")
        elif data == b'\x42':
            self.connectionCheckbox.setChecked(False)
            self.connectionLabel.setText("Not Connected")
    
    def open_data_page(self):
        self.full_data_page = FullDataPage(self.current_reference_point)
        self.full_data_page.show()

    def update_table(self, water_level):
        if self.full_data_page:
            self.full_data_page.update_table(water_level)

    def update_full_data_page(self, water_level):
        if self.full_data_page:
            self.full_data_page.update_table(water_level)
    
    def open_reference_page(self):
        self.referencepoint_btn = ReferencePointPage()
        self.referencepoint_btn.referenceChanged.connect(self.update_reference_label)
        self.referencepoint_btn.show()

    def start_serial_thread(self):
        if self.serial_thread is None:
            self.serial_thread = True
            self.serial_thread = SerialThread()
            self.serial_thread.data_received.connect(self.update_table)
            self.thread = threading.Thread(target=self.serial_thread.run)
            self.thread.start()

    def stop_serial_thread(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.thread.join()
            self.serial_thread = None
            self.thread = None