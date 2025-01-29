import tkinter as tk
import asyncio
import os
import cv2
import json
import time
import psutil
import winsound
import subprocess
import speech_recognition as sr
from PIL import Image, ImageTk
from gtts import gTTS
from mutagen.mp3 import MP3
from deep_translator import GoogleTranslator

class Conversation:
    def __init__(self):
        self._translators = {}
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        
        self.start_sound = "C:\\Windows\\Media\\chimes.wav"
        self.end_sound = "C:\\Windows\\Media\\notify.wav"

    def get_audio_length(self, file_path="speech.mp3"):
        try:
            audio = MP3(file_path)
            return audio.info.length
        except Exception as e:
            print(f"Audio length error: {e}")
            return 3  # Default to 3 seconds if error occurs

    async def speak_text(self, text, lang="en"):
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save("speech.mp3")
            subprocess.Popen(["start", "speech.mp3"], shell=True)
            await asyncio.sleep(self.get_audio_length("speech.mp3"))
            os.remove("speech.mp3")
        except Exception as e:
            print(f"Text-to-speech error: {e}")

    async def recognize_speech(self, language="en-US", timeout=10):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                winsound.PlaySound(self.start_sound, winsound.SND_FILENAME)
                
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
    def __init__(self, root):
        self.root = root
        self.cap = None
        with open('case_db.json', 'r', encoding='utf-8') as f:
            self.case_db = json.load(f)
        
        self.conversation = Conversation()
        self.case_number_entry = None
        self.text_area = None
        self.is_full_screen = False
        
    def toggle_full_screen(self, event=None):
        self.is_full_screen = not self.is_full_screen
        self.root.attributes('-fullscreen', self.is_full_screen)
        if not self.is_full_screen:
            self.root.state('normal')

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_left = int(screen_width / 2 - width / 2)
        self.root.geometry(f'{width}x{height}+{position_left}+{position_top}')

    def get_case_description(self, case_number):
        return next((case['case'] for case in self.case_db if case['case number'] == case_number), None)

    def update_text_area(self, message):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, message)

    async def cleanup_resources(self):
        if self.cap:
            self.cap.release()
        
        [proc.terminate() for proc in psutil.process_iter(['name']) 
         if proc.info['name'] in ['speech.mp3', 'python.exe']]
        
        cv2.destroyAllWindows()
        self.text_area.delete(1.0, tk.END)
        self.case_number_entry.delete(0, tk.END)

    async def on_button_click(self, language):
        case_number = self.case_number_entry.get()
        if not case_number.isdigit():
            self.update_text_area("Please enter a valid case number.\n")
            return
        
        case_description = self.get_case_description(case_number)
        if case_description:
            message = f"Case number {case_number}: {case_description}"
            translated_message = self.conversation.translate_text(message, 'en', language)
            self.update_text_area(translated_message)
            await self.conversation.speak_text(translated_message, language)
        else:
            self.update_text_area(f"No case found for case number {case_number}.\n")
            await self.conversation.speak_text(f"No case found for case number {case_number}.", language)

    def manual_voice_input(self):
        asyncio.run(self.manual_voice_input_async())
    
    async def manual_voice_input_async(self):
        try:
            case_number = await self.conversation.recognize_speech(language="en-US", timeout=10)
            
            if case_number and case_number.isdigit():
                self.case_number_entry.delete(0, tk.END)
                self.case_number_entry.insert(tk.END, case_number)
                await self.on_button_click('pa')  # Default to Punjabi
            else:
                self.update_text_area("Invalid input. Please say a valid case number.")
                await self.conversation.speak_text("Please say a valid case number.", lang="en")
        
        except Exception as e:
            print(f"Manual voice input error: {e}")
            self.update_text_area("Error in voice input.")

    def create_gui(self):
        # Set up root window
        self.root.title("Case Search Application")
        self.root.configure(bg="#E6E6FA")  # Light lavender background

        # Create main container with 3D effect
        main_container = tk.Frame(
            self.root, 
            bd=10, 
            relief="raised", 
            bg="#FFFFFF", 
            highlightthickness=2, 
            highlightbackground="#C0C0C0"
        )

        # Center the container
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        container_width = 800
        container_height = 600
        x_position = (screen_width - container_width) // 2
        y_position = (screen_height - container_height) // 2

        main_container.place(x=x_position, y=y_position, width=container_width, height=container_height)

        # Header
        header_label = tk.Label(
            main_container, 
            text="Case Search Portal", 
            font=("Arial", 20, "bold"), 
            bg="#FFFFFF", 
            fg="#4A4A4A",
            relief="groove",
            bd=2
        )
        header_label.pack(pady=10, fill=tk.X, padx=20)

        # Image Section
        try:
            phone_court_image = Image.open("images/court01.jpg")
            phone_court_image = phone_court_image.resize((480, 240), Image.Resampling.LANCZOS)
            phone_court_img_tk = ImageTk.PhotoImage(phone_court_image)

            img_label = tk.Label(
                main_container, 
                image=phone_court_img_tk, 
                bg="#FFFFFF", 
                relief="sunken", 
                bd=2
            )
            img_label.image = phone_court_img_tk
            img_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading image: {e}")

        # Case Number Entry Frame
        entry_frame = tk.Frame(main_container, bg="#FFFFFF")
        entry_frame.pack(pady=10)

        # Case Number Entry
        self.case_number_entry = tk.Entry(
            entry_frame, 
            width=40, 
            font=("Arial", 14), 
            bd=2, 
            relief="ridge"
        )
        self.case_number_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Mic Button
        mic_button = tk.Button(
            entry_frame, 
            text="🎤", 
            font=("Arial", 14), 
            bg="#F0F0F0", 
            relief="raised",
            bd=2, 
            command=self.manual_voice_input  # Use the normal function (no async needed here)
        )
        mic_button.pack(side=tk.LEFT)

        # Language Buttons Frame
        button_frame = tk.Frame(main_container, bg="#FFFFFF")
        button_frame.pack(pady=10)

        languages = [('Hindi', 'hi'), ('English', 'en'), ('Punjabi', 'pa')]
        for text, lang in languages:
            btn = tk.Button(
                button_frame, 
                text=text, 
                font=("Arial", 12), 
                bg="#4169E1", 
                fg="white", 
                relief="raised",
                bd=3,
                command=lambda lang=lang: asyncio.run(self.on_button_click(lang))  # Use lambda to pass argument
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Text Area
        self.text_area = tk.Text(
            main_container, 
            width=50, 
            height=8, 
            font=("Arial", 12),
            bd=2,
            relief="sunken"
        )
        self.text_area.pack(pady=10)

        # Close Button
        close_button = tk.Button(
            main_container, 
            text="Close", 
            font=("Arial", 12, "bold"), 
            bg="#DC143C", 
            fg="white", 
            relief="raised",
            bd=3,
            command=self.root.quit  # Use quit for closing the application
        )
        close_button.pack(pady=10)

def main():
    root = tk.Tk()
    app = CourtApplication(root)
    app.create_gui()
    root.mainloop()

if __name__ == "__main__":
    main()
