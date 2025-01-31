import os
import json
from gtts import gTTS
import pygame
import time
import tkinter as tk
from tkinter import font, messagebox, ttk
from deep_translator import GoogleTranslator
import speech_recognition as sr
from PIL import Image, ImageTk

class HighCourt:
    def __init__(self, root):
        self.root = root
        self.root.title("Court Case Information System")
        self.root.geometry("1000x800")  # Increased size to accommodate table

        # Load court database
        self.load_court_database()

        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Add header image
        try:
            # Load and resize the image
            image = Image.open("images/court01.jpg")  # Make sure to have this image in your directory
            image = image.resize((950, 480), Image.Resampling.LANCZOS)
            self.header_image = ImageTk.PhotoImage(image)
            self.image_label = tk.Label(self.main_frame, image=self.header_image)
            self.image_label.pack(pady=10)
        except Exception as e:
            print(f"Could not load image: {e}")
            # Fallback colored rectangle if image fails to load
            self.image_label = tk.Label(self.main_frame, bg="skyblue", height=10)
            self.image_label.pack(fill="x", pady=10)

        # Create a custom label to display subtitles
        self.subtitle_label = tk.Label(
            self.main_frame,
            text="",
            font=font.Font(size=16, weight="bold"),
            fg="red",
            bg="skyblue",
            wraplength=550,
            padx=10,
            pady=10,
        )
        self.subtitle_label.pack(fill="x", pady=10)

        # Text input box
        self.text_input = tk.Entry(self.main_frame, font=font.Font(size=14), width=50)
        self.text_input.pack(pady=10)

        # Buttons for speaking in different languages
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        self.english_button = tk.Button(
            self.button_frame,
            text="Speak English",
            command=lambda: self.process_case_number(self.text_input.get(), "en"),
            font=font.Font(size=14, weight="bold"),
            bg="lightgreen",
            fg="black",
        )
        self.english_button.pack(side="left", padx=5)

        self.hindi_button = tk.Button(
            self.button_frame,
            text="Speak Hindi",
            command=lambda: self.process_case_number(self.text_input.get(), "hi"),
            font=font.Font(size=14, weight="bold"),
            bg="lightgreen",
            fg="black",
        )
        self.hindi_button.pack(side="left", padx=5)

        self.punjabi_button = tk.Button(
            self.button_frame,
            text="Speak Punjabi",
            command=lambda: self.process_case_number(self.text_input.get(), "pa"),
            font=font.Font(size=14, weight="bold"),
            bg="lightgreen",
            fg="black",
        )
        self.punjabi_button.pack(side="left", padx=5)

        # Microphone button for voice input
        self.mic_button = tk.Button(
            self.main_frame,
            text="🎤 Speak Case Number",
            command=self.listen_and_speak,
            font=font.Font(size=14, weight="bold"),
            bg="orange",
            fg="black",
        )
        self.mic_button.pack(pady=10)

        # Add table for case details
        self.create_case_table()

        # Initialize translators
        self._translators = {}

    def create_case_table(self):
        # Create frame for table
        table_frame = tk.Frame(self.main_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create table with Treeview
        columns = ("Case Number", "Case Title", "Court Number", "Judge Name")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        # Configure column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)  # Adjust column width

        # Style the table
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        style.configure("Treeview", font=('Helvetica', 10), rowheight=25)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack the table and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate table with data from database
        self.update_table()

    def update_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add data from database
        for case in self.court_database:
            self.tree.insert("", "end", values=(
                case['case_number'],
                case['case'],
                case['court_number'],
                case['judge_name']
            ))

    # [Rest of your existing methods remain the same]
    def load_court_database(self):
        try:
            with open('case_database.json', 'r') as file:
                self.court_database = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load court database: {e}")
            self.court_database = []

    def find_case_details(self, case_number):
        if not case_number or case_number.isspace():
            return "Please enter a valid case number."
        digits_only = ''.join(filter(str.isdigit, case_number))
        if not digits_only:
            return "Please enter a valid case number."
        formatted_number = f"2025-{digits_only.zfill(3)}"
        for case in self.court_database:
            if case['case_number'] == formatted_number:
                return (f"Case number {formatted_number}. "
                       f"Case: {case['case']}. "
                       f"Court number {case['court_number']}. "
                       f"Presiding judge: {case['judge_name']}.")
        return "Please enter a valid case number."

    # [Keep all other existing methods exactly as they are]
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
        case_details = self.translate_text(case_details, source='en', target=lang)
        self.speak_text(case_details, lang)

    def speak_text(self, text, lang="en"):
        try:
            if os.path.exists("speech.mp3"):
                os.remove("speech.mp3")
            tts = gTTS(text=text, lang=lang)
            tts.save("speech.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("speech.mp3")
            audio = pygame.mixer.Sound("speech.mp3")
            total_duration = audio.get_length()
            words = text.split()
            num_words = len(words)
            duration_per_word = total_duration / num_words
            pygame.mixer.music.play()

            # Print words in real-time and update the GUI
            for word in words:
                self.subtitle_label.config(text=self.subtitle_label.cget("text") + " " + word)
                self.root.update()
                time.sleep(duration_per_word)

            # Clear the subtitle after the audio finishes
            self.subtitle_label.config(text="")
            self.root.update()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.quit()
        except Exception as e:
            print(f"Text-to-speech error: {e}")

    def listen_and_speak(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source)
                self.subtitle_label.config(text="Listening for case number...")
                self.root.update()
                audio = recognizer.listen(source, timeout=5)

                recognized_text = recognizer.recognize_google(audio)
                self.text_input.delete(0, tk.END)
                self.text_input.insert(0, recognized_text)
                # self.subtitle_label.config(text=f"Recognized: {recognized_text}")
                self.root.update()
                
                # Process the recognized case number
                self.process_case_number(recognized_text, "en")
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand audio")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Could not request results; {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    tts = HighCourt(root)
    root.mainloop()


