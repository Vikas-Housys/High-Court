import customtkinter as ctk
import os
import cv2
import json
import time
import psutil
import speech_recognition as sr
from PIL import Image
from gtts import gTTS
from mutagen.mp3 import MP3
from deep_translator import GoogleTranslator
import pygame

# Set the appearance mode and default color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Conversation:
    def __init__(self):
        self._translators = {}
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
    
    def get_audio_length(self, file_path="speech.mp3"):
        try:
            audio = MP3(file_path)
            return audio.info.length
        except Exception as e:
            print(f"Audio length error: {e}")
            return 3 

    def speak_text(self, text, lang="en"):
        try:
            # Remove existing file if it exists
            if os.path.exists("speech.mp3"):
                os.remove("speech.mp3")

            # Convert text to speech and save as MP3
            tts = gTTS(text=text, lang=lang)
            tts.save("speech.mp3")

            # Initialize pygame mixer
            pygame.mixer.init()
            pygame.mixer.music.load("speech.mp3")
            pygame.mixer.music.play()

            # Wait until the audio finishes playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Add a small delay to avoid high CPU usage

            # Clean up
            pygame.mixer.quit()
        except Exception as e:
            print(f"Text-to-speech error: {e}")
    
    def recognize_speech(self, language="en-US", timeout=10):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
                text = self.recognizer.recognize_google(audio, language=language)
                print(f"Recognized: {text}")
                return text
        except sr.WaitTimeoutError:
            print("No speech detected within timeout.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except Exception as e:
            print(f"Speech recognition error: {e}")
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

class CourtApplication:
    def __init__(self):
        self.root = ctk.CTk()
        self.cap = None
        with open('case_db.json', 'r', encoding='utf-8') as f:
            self.case_db = json.load(f)
        
        self.conversation = Conversation()
        self.case_number_entry = None
        self.text_area = None
        self.is_full_screen = False
        self.setup_window()
        
    def setup_window(self):
        self.root.title("Case Search Application")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{1100}x{900}")
        self.root.resizable(True, True)

    def get_case_description(self, case_number):
        return next((case['case'] for case in self.case_db if case['case number'] == case_number), None)

    def update_text_area(self, message):
        self.text_area.delete("0.0", "end")
        self.text_area.insert("0.0", message)

    def cleanup_resources(self):
        if self.cap:
            self.cap.release()
        
        [proc.terminate() for proc in psutil.process_iter(['name']) 
         if proc.info['name'] in ['speech.mp3', 'python.exe']]
        
        cv2.destroyAllWindows()
        self.text_area.delete("0.0", "end")
        self.case_number_entry.delete(0, "end")

    def on_button_click(self, language):
        case_number = self.case_number_entry.get()
        if not case_number.isdigit():
            self.update_text_area("Please enter a valid case number.\n")
            return
        
        case_description = self.get_case_description(case_number)
        if case_description:
            message = f"Case number {case_number}: {case_description}"
            translated_message = self.conversation.translate_text(message, 'en', language)
            self.update_text_area(translated_message)
            self.conversation.speak_text(translated_message, language)
        else:
            self.update_text_area(f"No case found for case number {case_number}.\n")
            self.conversation.speak_text(f"No case found for case number {case_number}.", language)
    
    def manual_voice_input(self):
        try:
            message = self.conversation.translate_text("Kindly speak your case number.", source='en', target='pa')
            self.conversation.speak_text(message, lang='pa')
            # time.sleep(self.conversation.get_audio_length())
            case_number = self.conversation.recognize_speech(language="en-US", timeout=10)
            
            if case_number and case_number.isdigit():
                self.case_number_entry.delete(0, "end")
                self.case_number_entry.insert(0, case_number)
                self.on_button_click('pa')  # Default to Punjabi
            else:
                self.update_text_area("Invalid input. Please say a valid case number.")
                self.conversation.speak_text("Please say a valid case number.", lang="en")
        
        except Exception as e:
            print(f"Manual voice input error: {e}")
            self.update_text_area("Error in voice input.")

    def create_gui(self):
        # Main container
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(padx=20, pady=20, fill="both", expand=True)

        # Header
        header_label = ctk.CTkLabel(
            main_container,
            text="Case Search Portal",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header_label.pack(pady=20)

        # Image Section
        try:
            court_image = ctk.CTkImage(
                light_image=Image.open("images/court01.jpg"),
                dark_image=Image.open("images/court01.jpg"),
                size=(480, 240)
            )
            image_label = ctk.CTkLabel(main_container, image=court_image, text="")
            image_label.pack(pady=20)
        except Exception as e:
            print(f"Error loading image: {e}")

        # Case Number Entry Frame
        entry_frame = ctk.CTkFrame(main_container)
        entry_frame.pack(pady=20)

        self.case_number_entry = ctk.CTkEntry(
            entry_frame,
            width=300,
            placeholder_text="Enter Case Number",
            font=ctk.CTkFont(size=14)
        )
        self.case_number_entry.pack(side="left", padx=10)

        # Mic Button
        mic_button = ctk.CTkButton(
            entry_frame,
            text="🎤 Mic",
            width=120,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.manual_voice_input,
            fg_color="#800000",
            hover_color="#600000"
        )
        mic_button.pack(side="left", padx=10)

        # Language Buttons Frame
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(pady=20)

        languages = [('Hindi', 'hi'), ('English', 'en'), ('Punjabi', 'pa')]
        for text, lang in languages:
            ctk.CTkButton(
                button_frame,
                text=text,
                width=120,
                font=ctk.CTkFont(size=14),
                command=lambda l=lang: self.on_button_click(l)
            ).pack(side="left", padx=5)

        # Text Area
        self.text_area = ctk.CTkTextbox(
            main_container,
            width=600,
            height=200,
            font=ctk.CTkFont(size=14)
        )
        self.text_area.pack(pady=20)

        # Bottom Buttons Frame
        bottom_frame = ctk.CTkFrame(main_container)
        bottom_frame.pack(pady=20)

        # Close Button
        ctk.CTkButton(
            bottom_frame,
            text="Close",
            width=120,
            font=ctk.CTkFont(size=14),
            command=self.root.quit,
            fg_color="#DC143C",
            hover_color="#B01030"
        ).pack(side="left", padx=10)

        # Reset Button
        ctk.CTkButton(
            bottom_frame,
            text="Reset",
            width=120,
            font=ctk.CTkFont(size=14),
            command=self.reset_fields,
            fg_color="#228B22",
            hover_color="#1A691A"
        ).pack(side="left", padx=10)

    def reset_fields(self):
        """Reset the case number entry and text area."""
        self.case_number_entry.delete(0, "end")
        self.text_area.delete("0.0", "end")

    def run(self):
        self.create_gui()
        self.root.mainloop()

def main():
    app = CourtApplication()
    app.run()

if __name__ == "__main__":
    main()