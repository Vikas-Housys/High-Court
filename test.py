import customtkinter as ctk
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
        self.is_full_screen = True
        self.root.attributes('-fullscreen', self.is_full_screen)
        
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
        self.text_area.delete(1.0, ctk.END)
        self.text_area.insert(ctk.END, message)

    async def cleanup_resources(self):
        if self.cap:
            self.cap.release()
        
        [proc.terminate() for proc in psutil.process_iter(['name']) 
         if proc.info['name'] in ['speech.mp3', 'python.exe']]
        
        cv2.destroyAllWindows()
        self.text_area.delete(1.0, ctk.END)
        self.case_number_entry.delete(0, ctk.END)

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
                self.case_number_entry.delete(0, ctk.END)
                self.case_number_entry.insert(ctk.END, case_number)
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
        main_container = ctk.CTkFrame(
            self.root, 
            fg_color="#FFFFFF", 
            corner_radius=20,
            width=100, 
            height=100, 
            border_width=4,
            border_color="#C0C0C0"
        )

        # Center the container
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        container_width = 80
        container_height = 80
        x_position = (screen_width - container_width) // 2
        y_position = (screen_height - container_height) // 2

        main_container.place(x=x_position, y=y_position)

        # Header
        header_label = ctk.CTkLabel(
            main_container, 
            text="Case Search Portal", 
            font=("Arial", 20, "bold"), 
            text_color="#D2691E",
            corner_radius=10
        )
        header_label.pack(pady=10, fill=ctk.X, padx=20)

        # Case Number Entry Frame
        entry_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15)
        entry_frame.pack(pady=10)

        # Case Number Entry
        self.case_number_entry = ctk.CTkEntry(
            entry_frame,
            width=200,
            height=40, 
            font=("Arial", 14, "bold"), 
            border_width=2, 
            corner_radius=15
        )
        self.case_number_entry.pack(side=ctk.LEFT, padx=(0, 10))

        # Mic Button Frame
        mic_button_frame = ctk.CTkFrame(main_container, fg_color="#228B22", corner_radius=15, border_width=2, border_color="#C0C0C0")
        mic_button_frame.pack(pady=10)

        # Mic Button inside the new frame
        mic_button = ctk.CTkButton(
            mic_button_frame, 
            text="🎤 Mic", 
            width=12, 
            font=("Arial", 14, "bold"), 
            fg_color="#800000", 
            text_color="white", 
            corner_radius=10, 
            command=self.manual_voice_input
        )
        mic_button.pack()

        # Language Buttons Frame
        button_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=10)
        button_frame.pack(pady=10)

        languages = [('Hindi', 'hi'), ('English', 'en'), ('Punjabi', 'pa')]
        for text, lang in languages:
            btn = ctk.CTkButton(
                button_frame, 
                text=text, 
                width=50,
                height=20,
                font=("Arial", 12, "bold"), 
                fg_color="#4169E1", 
                text_color="white", 
                corner_radius=10,
                command=lambda lang=lang: asyncio.run(self.on_button_click(lang))
            )
            btn.pack(side=ctk.LEFT, padx=5)

        # Text Area
        self.text_area = ctk.CTkTextbox(
            main_container, 
            width=50, 
            height=8, 
            font=("Arial", 12),
            border_width=2, 
            corner_radius=10
        )
        self.text_area.pack(pady=10)

        # Frame for Close and Reset Buttons
        button_frame_bottom = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15)
        button_frame_bottom.pack(pady=10)

        # Close Button
        close_button = ctk.CTkButton(
            button_frame_bottom, 
            text="Close", 
            width=12, 
            font=("Arial", 12, "bold"), 
            fg_color="#DC143C", 
            text_color="white", 
            corner_radius=15, 
            command=self.root.quit
        )
        close_button.pack(side=ctk.LEFT, padx=10)

        # Reset Button
        reset_button = ctk.CTkButton(
            button_frame_bottom, 
            text="Reset", 
            width=12,
            font=("Arial", 12, "bold"), 
            fg_color="#228B22", 
            text_color="white", 
            corner_radius=15, 
            command=self.reset_fields
        )
        reset_button.pack(side=ctk.LEFT, padx=10)

    def reset_fields(self):
        """This method will reset the case number entry and text area."""
        self.case_number_entry.delete(0, ctk.END)
        self.text_area.delete(1.0, ctk.END)


def main():
    root = ctk.CTk()
    app = CourtApplication(root)
    app.create_gui()
    root.mainloop()

if __name__ == "__main__":
    main()
