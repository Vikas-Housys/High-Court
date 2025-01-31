import os
import json
from gtts import gTTS
import pygame
import time
import tkinter as tk
from tkinter import font, messagebox
from deep_translator import GoogleTranslator
import speech_recognition as sr

class HighCourt:
    def __init__(self, root):
        self.root = root
        self.root.title("Court Case Information System")
        self.root.geometry("600x300")

        # Load court database
        self.load_court_database()

        # Create a custom label to display subtitles
        self.subtitle_label = tk.Label(
            root,
            text="",
            font=font.Font(size=16, weight="bold"),
            fg="red",
            bg="skyblue",
            wraplength=550,
            padx=10,
            pady=10,
        )
        self.subtitle_label.pack(fill="both", expand=True)

        # Text input box
        self.text_input = tk.Entry(root, font=font.Font(size=14), width=50)
        self.text_input.pack(pady=10)

        # Buttons for speaking in different languages
        self.button_frame = tk.Frame(root)
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
            root,
            text="🎤 Speak Case Number",
            command=self.listen_and_speak,
            font=font.Font(size=14, weight="bold"),
            bg="orange",
            fg="black",
        )
        self.mic_button.pack(pady=10)

        # Initialize translators
        self._translators = {}

    def load_court_database(self):
        try:
            with open('case_database.json', 'r') as file:
                self.court_database = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load court database: {e}")
            self.court_database = []

    def find_case_details(self, case_number):
        # Check if input is empty or only whitespace
        if not case_number or case_number.isspace():
            return "Please enter a valid case number."
            
        # Remove any non-digit characters from the input
        digits_only = ''.join(filter(str.isdigit, case_number))
        
        # Check if we have any digits
        if not digits_only:
            return "Please enter a valid case number."
        
        # Format the case number to match database format
        formatted_number = f"2025-{digits_only.zfill(3)}"
        
        # Check if the case number exists in database
        for case in self.court_database:
            if case['case_number'] == formatted_number:
                return (f"Case number {formatted_number}. "
                       f"Case: {case['case']}. "
                       f"Court number {case['court_number']}. "
                       f"Presiding judge: {case['judge_name']}.")
        
        # If no case is found, return the error message
        return "Please enter a valid case number."

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



