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
        self.root.geometry("800x600")  # Increased size to accommodate table

        # Load court database
        self.load_court_database()
        
        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Add heading above the title
        self.heading_label = tk.Label(
            self.main_frame,
            text="High Court Case Management System",
            font=font.Font(size=20, weight="bold"),
            fg="blue",  # Blue color
            bg="lightgray",  # Light gray background
            padx=10,
            pady=10,
        )
        self.heading_label.pack(fill="x", pady=10)

        # Add header image
        try:
            image = Image.open("images/court02.jpg")
            image = image.resize((1080, 480), Image.Resampling.LANCZOS)
            self.header_image = ImageTk.PhotoImage(image)
            self.image_label = tk.Label(self.main_frame, image=self.header_image)
            self.image_label.pack(pady=10)
        except Exception as e:
            print(f"Could not load image: {e}")
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
        
        # Bind the Entry widget to update table on text change
        self.text_input.bind('<KeyRelease>', self.on_text_change)

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
            command=lambda: self.process_case_number(self.translate_text(self.text_input.get(), source='en', target='hi'), "hi"),
            font=font.Font(size=14, weight="bold"),
            bg="lightgreen",
            fg="black",
        )
        self.hindi_button.pack(side="left", padx=5)

        self.punjabi_button = tk.Button(
            self.button_frame,
            text="Speak Punjabi",
            command=lambda: self.process_case_number(self.translate_text(self.text_input.get(), source='en', target='pa'), "pa"),
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

        # Map button to open map image
        self.map_button = tk.Button(
            self.main_frame,
            text="🗺️ Open Map",
            command=self.open_map,
            font=font.Font(size=14, weight="bold"),
            bg="lightblue",
            fg="black",
        )
        self.map_button.pack(pady=10)

        # Add table for case details
        self.create_case_table()

        # Initialize translators
        self._translators = {}

    def load_court_database(self):
        """Load the court database from a JSON file."""
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
                },
                {
                    "case_number": "2025-003",
                    "case": "Alice vs. Bob",
                    "court_number": "Court 3",
                    "judge_name": "Judge White"
                }
            ]

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
            self.tree.column(col, width=200)

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

    def on_text_change(self, event=None):
        """Update table when text input changes"""
        case_number = self.text_input.get()
        self.update_table(case_number)

    def update_table(self, search_case_number=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not search_case_number:
            return

        # Format the search number
        digits_only = ''.join(filter(str.isdigit, search_case_number))
        if not digits_only:
            return
        
        formatted_number = f"2025-{digits_only.zfill(3)}"

        # Add only the matching case
        for case in self.court_database:
            if case['case_number'] == formatted_number:
                self.tree.insert("", "end", values=(
                    case['case_number'],
                    case['case'],
                    case['court_number'],
                    case['judge_name']
                ))
                break

    def process_case_number(self, case_number, lang="en"):
        case_details = self.find_case_details(case_number)
        if case_details:
            case_details = self.translate_text(case_details, source='en', target=lang)
            self.speak_text(case_details, lang)
        else:
            self.speak_text("Case not found.", lang)
        # Update the table when processing a case number
        self.update_table(case_number)

    def find_case_details(self, case_number):
        """Find case details based on the case number."""
        digits_only = ''.join(filter(str.isdigit, case_number))
        if not digits_only:
            return None
        
        formatted_number = f"2025-{digits_only.zfill(3)}"
        for case in self.court_database:
            if case['case_number'] == formatted_number:
                return f"Case Number: {case['case_number']}, Case Title: {case['case']}, Court Number: {case['court_number']}, Judge Name: {case['judge_name']}"
        return None

    def translate_text(self, text, source, target):
        """Translate text from source language to target language."""
        key = (source, target)
        if key not in self._translators:
            self._translators[key] = GoogleTranslator(source=source, target=target)
        try:
            return self._translators[key].translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text

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
        self.speak_text("Kindly tell me your case number: ", lang='en')
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
                self.root.update()
                
                # Process the recognized case number
                self.process_case_number(recognized_text, "en")
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand audio")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Could not request results; {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def open_map(self):
        """Open the map image corresponding to the case number."""
        case_number = self.text_input.get()
        if not case_number:
            messagebox.showwarning("Warning", "Please enter a case number.")
            return

        # Format the case number
        digits_only = ''.join(filter(str.isdigit, case_number))
        if not digits_only:
            messagebox.showwarning("Warning", "Invalid case number.")
            return
        
        formatted_number = f"2025-{digits_only.zfill(3)}"
        map_filename = f"images/map_{formatted_number}.jpg"

        if not os.path.exists(map_filename):
            messagebox.showerror("Error", f"Map file not found for case number: {formatted_number}")
            return

        # Open the map image in a new window
        map_window = tk.Toplevel(self.root)
        map_window.title(f"Map for Case {formatted_number}")
        try:
            map_image = Image.open(map_filename)
            map_image = map_image.resize((720, 480), Image.Resampling.LANCZOS)
            map_photo = ImageTk.PhotoImage(map_image)
            map_label = tk.Label(map_window, image=map_photo)
            map_label.image = map_photo  # Keep a reference to avoid garbage collection
            map_label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load map image: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    tts = HighCourt(root)
    root.mainloop()

