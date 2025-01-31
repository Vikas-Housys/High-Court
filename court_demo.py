import os
from gtts import gTTS
import pygame
import time
import tkinter as tk
from tkinter import font
from deep_translator import GoogleTranslator

class TextToSpeech:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Subtitles")
        self.root.geometry("600x150")  # Set window size

        # Create a custom label to display subtitles
        self.subtitle_label = tk.Label(
            root,
            text="",
            font=font.Font(size=20, weight="bold"),
            fg="red",  # Text color: red
            bg="skyblue",  # Background color: sky blue
            wraplength=550,  # Wrap text to fit the window
            padx=10,  # Add padding for better appearance
            pady=10,
        )
        self.subtitle_label.pack(fill="both", expand=True)
    
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

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    tts = TextToSpeech(root)

    # Example usage
    def start_speech():
        tts.speak_text("Hello, how are you?", lang="en")  # English
        tts.speak_text("नमस्ते, आप कैसे हैं?", lang="hi")  # Hindi
        tts.speak_text("ਹੈਲੋ, ਤੁਸੀ ਕਿਵੇਂ ਹੋ?", lang="pa")  # Punjabi

    # Add a button to start the speech
    start_button = tk.Button(
        root,
        text="Start Speech",
        command=start_speech,
        font=font.Font(size=14, weight="bold"),
        bg="lightgreen",  # Button background color
        fg="black",  # Button text color
    )
    start_button.pack(pady=10)

    root.mainloop()

