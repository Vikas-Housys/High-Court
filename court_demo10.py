import os
import json
import sys
from gtts import gTTS
import pygame
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon
from deep_translator import GoogleTranslator
import speech_recognition as sr


class HighCourt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Court Case Information System")
        self.setMinimumSize(1000, 1900)  # Set the window size to 1000x1900

        # Initialize pygame mixer
        pygame.mixer.init()

        # Load court database
        self.load_court_database()

        # Initialize translators
        self._translators = {}

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Create an outer frame with fixed size
        outer_frame = QFrame()
        outer_frame.setFixedSize(1000, 1900)  # Set the fixed size of the outer frame
        outer_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 5px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.main_layout.addWidget(outer_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Create a layout for the outer frame
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align everything to the top

        ### Add heading
        heading_label = QLabel("High Court Case Management System")
        heading_label.setStyleSheet("""
            QLabel {
                color: blue;
                font-size: 38px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.addWidget(heading_label)

        ### Add header image
        self.image_label = QLabel()
        try:
            pixmap = QPixmap("images/court02.jpg")
            scaled_pixmap = pixmap.scaled(900, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.image_label.setStyleSheet("""
                QLabel {
                    background: none;
                    border: 5px solid yellow;
                    border-radius: 25px;
                    padding: 5px;
                }
            """)
        except Exception as e:
            print(f"Could not load image: {e}")
            self.image_label.setText("Header Image")
        outer_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        ### Input section
        input_label = QLabel("Enter Case Number")
        input_label.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")
        input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.addWidget(input_label)

        # Input layout with text field and mic button
        input_layout = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                padding: 5px;
                border: 5px solid #573AC0;
                border-radius: 20px;
                min-height: 60px;
            }
        """)
        self.text_input.textChanged.connect(self.on_text_change)
        input_layout.addWidget(self.text_input)

        # Mic button
        self.mic_button = QPushButton()
        mic_icon = QIcon("images/mic2.png")
        self.mic_button.setIcon(mic_icon)
        self.mic_button.setFixedSize(120, 50)
        self.mic_button.clicked.connect(self.listen_and_speak)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        input_layout.addWidget(self.mic_button)
        outer_layout.addLayout(input_layout)

        # Language buttons
        button_layout = QHBoxLayout()
        language_buttons = [
            ("Speak English", lambda: self.process_case_number(self.text_input.text(), "en")),
            ("हिंदी बोलें", lambda: self.process_case_number(self.translate_text(self.text_input.text(), 'en', 'hi'), "hi")),
            ("ਹਿੰਦੀ ਬੋਲੋ", lambda: self.process_case_number(self.translate_text(self.text_input.text(), 'en', 'pa'), "pa"))
        ]

        for text, callback in language_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #573AC0;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    min-height: 80px;
                    min-width: 240px;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background-color: #4527A0;
                }
            """)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)

        outer_layout.addLayout(button_layout)

        # Subtitle frame
        subtitle_frame = QFrame()
        subtitle_frame.setFixedSize(900, 100)  # Set fixed width and height
        subtitle_frame.setStyleSheet("""
            QFrame {
                background-color: skyblue;
                border: 3px solid green;
                border-radius: 5px;
            }
        """)

        # Layout for the subtitle frame
        subtitle_layout = QVBoxLayout(subtitle_frame)
        subtitle_layout.setContentsMargins(10, 10, 10, 10)  # Optional padding inside the box
        subtitle_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center-align content

        # Add the subtitle frame to the main layout
        self.main_layout.addWidget(subtitle_frame, alignment=Qt.AlignmentFlag.AlignCenter)


        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: red;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_layout.addWidget(self.subtitle_label)

        outer_layout.addWidget(subtitle_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Case Number", "Case Title", "Court Number", "Judge Name"])
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                font-weight: bold;
                padding: 5px;
            }
        """)
        outer_layout.addWidget(self.table)

        # Map button
        self.map_button = QPushButton("Map")
        self.map_button.setStyleSheet("""
            QPushButton {
                background-color: teal;
                color: white;
                font-size: 14px;
                font-weight: bold;
                min-height: 60px;
                min-width: 240px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
        """)
        self.map_button.clicked.connect(self.open_map)
        outer_layout.addWidget(self.map_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def load_court_database(self):
        try:
            with open("case_database.json", "r", encoding="utf-8") as file:
                self.court_database = json.load(file)
        except FileNotFoundError:
            print("Court database file not found. Using a sample database.")
            self.court_database = [
                {
                    "case_number": "2025-001",
                    "case": "John Doe vs. State",
                    "court_number": "Court 1",
                    "judge_name": "Judge Smith"
                },
                {
                    "case_number": "2025-002",
                    "case": "Jane Doe vs. State",
                    "court_number": "Court 2",
                    "judge_name": "Judge Brown"
                }
            ]

    def on_text_change(self):
        self.update_table(self.text_input.text())

    def update_table(self, search_case_number):
        self.table.setRowCount(0)
        if not search_case_number:
            return

        digits_only = ''.join(filter(str.isdigit, search_case_number))
        if not digits_only:
            return

        formatted_number = f"2025-{digits_only.zfill(3)}"

        for case in self.court_database:
            if case['case_number'] == formatted_number:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(case['case_number']))
                self.table.setItem(row_position, 1, QTableWidgetItem(case['case']))
                self.table.setItem(row_position, 2, QTableWidgetItem(case['court_number']))
                self.table.setItem(row_position, 3, QTableWidgetItem(case['judge_name']))
                break

    def find_case_details(self, case_number):
        digits_only = ''.join(filter(str.isdigit, case_number))
        if not digits_only:
            return None

        formatted_number = f"2025-{digits_only.zfill(3)}"
        for case in self.court_database:
            if case['case_number'] == formatted_number:
                return f"Case Number: {case['case_number']}, Case Title: {case['case']}, Court Number: {case['court_number']}, Judge Name: {case['judge_name']}"
        return None

    def translate_text(self, text, source, target):
        key = (source, target)
        if key not in self._translators:
            self._translators[key] = GoogleTranslator(source=source, target=target)
        try:
            return self._translators[key].translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def process_case_number(self, case_number, lang="en"):
        case_details = self.find_case_details(case_number)
        if case_details:
            case_details = self.translate_text(case_details, source='en', target=lang)
            self.speak_text(case_details, lang)
        else:
            self.speak_text("Case not found.", lang)
        self.update_table(case_number)

    def speak_text(self, text, lang="en"):
        try:
            if os.path.exists("speech.mp3"):
                os.remove("speech.mp3")

            tts = gTTS(text=text, lang=lang)
            tts.save("speech.mp3")

            pygame.mixer.music.load("speech.mp3")
            audio = pygame.mixer.Sound("speech.mp3")
            total_duration = audio.get_length()
            words = text.split()
            num_words = len(words)
            duration_per_word = total_duration / num_words

            pygame.mixer.music.play()

            self.subtitle_label.setText("")
            current_text = ""

            for word in words:
                current_text += f" {word}"
                self.subtitle_label.setText(current_text)
                QApplication.processEvents()
                time.sleep(duration_per_word)

            while pygame.mixer.music.get_busy():
                QApplication.processEvents()

            self.subtitle_label.setText("")
            pygame.mixer.quit()
            pygame.mixer.init()

        except Exception as e:
            print(f"Text-to-speech error: {e}")

    def listen_and_speak(self):
        self.speak_text("Kindly tell me your case number.", lang='en')
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source)
                self.subtitle_label.setText("Listening for case number...")
                QApplication.processEvents()
                audio = recognizer.listen(source, timeout=5)

                recognized_text = recognizer.recognize_google(audio)
                self.text_input.setText(recognized_text)
                self.subtitle_label.setText("")
                self.process_case_number(recognized_text, "en")
            except sr.UnknownValueError:
                self.subtitle_label.setText("Could not understand audio")
            except sr.RequestError as e:
                self.subtitle_label.setText(f"Could not request results: {e}")
            except Exception as e:
                self.subtitle_label.setText(f"An error occurred: {e}")

    def open_map(self):
        case_number = self.text_input.text()
        if not case_number:
            self.subtitle_label.setText("Please enter a case number.")
            return

        digits_only = ''.join(filter(str.isdigit, case_number))
        if not digits_only:
            self.subtitle_label.setText("Invalid case number.")
            return

        formatted_number = f"2025-{digits_only.zfill(3)}"
        map_filename = f"images/map_{formatted_number}.jpg"

        if not os.path.exists(map_filename):
            self.subtitle_label.setText(f"Map file not found for case number: {formatted_number}")
            return

        from PyQt6.QtWidgets import QDialog
        map_window = QDialog(self)
        map_window.setWindowTitle(f"Map for Case {formatted_number}")
        map_window.setMinimumSize(720, 480)

        layout = QVBoxLayout(map_window)
        map_label = QLabel()
        try:
            pixmap = QPixmap(map_filename)
            scaled_pixmap = pixmap.scaled(720, 480, Qt.AspectRatioMode.KeepAspectRatio)
            map_label.setPixmap(scaled_pixmap)
            layout.addWidget(map_label)
            map_window.exec()
        except Exception as e:
            self.subtitle_label.setText(f"Could not load map image: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HighCourt()
    window.show()
    sys.exit(app.exec())