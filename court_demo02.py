import os
from gtts import gTTS
import pygame
import time
import tkinter as tk
from tkinter import font, messagebox
from deep_translator import GoogleTranslator
import speech_recognition as sr

class TextToSpeech:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Subtitles")
        self.root.geometry("600x300")  # Set window size

        # Create a custom label to display subtitles
        self.subtitle_label = tk.Label(
            root,
            text="",
            font=font.Font(size=16, weight="bold"),
            fg="red",  # Text color: red
            bg="skyblue",  # Background color: sky blue
            wraplength=550,  # Wrap text to fit the window
            padx=10,  # Add padding for better appearance
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
            command=lambda: self.speak_text(self.text_input.get(), lang="en"),
            font=font.Font(size=14, weight="bold"),
            bg="lightgreen",  # Button background color
            fg="black",  # Button text color
        )
        self.english_button.pack(side="left", padx=5)

        self.hindi_button = tk.Button(
            self.button_frame,
            text="Speak Hindi",
            command=lambda: self.speak_text(self.translate_text(self.text_input.get(), source='en', target='hi'), lang="hi"),
            font=font.Font(size=14, weight="bold"),
            bg="lightgreen",  # Button background color
            fg="black",  # Button text color
        )
        self.hindi_button.pack(side="left", padx=5)

        self.punjabi_button = tk.Button(
            self.button_frame,
            text="Speak Punjabi",
            command=lambda: self.speak_text(self.translate_text(self.text_input.get(), source='en', target='pa'), lang="pa"),
            font=font.Font(size=14, weight="bold"),
            bg="lightgreen",  # Button background color
            fg="black",  # Button text color
        )
        self.punjabi_button.pack(side="left", padx=5)

        # Microphone button for voice input
        self.mic_button = tk.Button(
            root,
            text="🎤 Listen and Speak",
            command=self.listen_and_speak,
            font=font.Font(size=14, weight="bold"),
            bg="orange",  # Button background color
            fg="black",  # Button text color
        )
        self.mic_button.pack(pady=10)

        # Initialize translators
        self._translators = {}

    def translate_text(self, text, source, target):
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
                self.root.update()  # Update the GUI
                time.sleep(duration_per_word)  # Wait for the duration of the word

            # Clear the subtitle after the audio finishes
            self.subtitle_label.config(text="")
            self.root.update()

            # Wait until the audio finishes playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Add a small delay to avoid high CPU usage

            # Clean up
            pygame.mixer.quit()
        except Exception as e:
            print(f"Text-to-speech error: {e}")

    def listen_and_speak(self):
        """Listen to microphone input and speak the recognized text."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                # Adjust for ambient noise and listen to the user's voice
                recognizer.adjust_for_ambient_noise(source)
                self.subtitle_label.config(text="Listening...")
                self.root.update()
                audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds

                # Recognize speech using Google Web Speech API
                recognized_text = recognizer.recognize_google(audio)
                self.text_input.delete(0, tk.END)  # Clear the input box
                self.text_input.insert(0, recognized_text)  # Insert recognized text
                self.subtitle_label.config(text=f"Recognized: {recognized_text}")
                self.root.update()
                
                # Speak the recognized text in English
                self.speak_text(recognized_text, lang="en")
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand audio")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Could not request results; {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    tts = TextToSpeech(root)
    root.mainloop()

