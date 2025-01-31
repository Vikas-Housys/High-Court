import os
from gtts import gTTS
import pygame
import time

class TextToSpeech:
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

            # Get the total duration of the audio
            audio = pygame.mixer.Sound("speech.mp3")
            total_duration = audio.get_length()  # Total duration in seconds

            # Split the text into words
            words = text.split()
            num_words = len(words)

            # Calculate the duration per word
            duration_per_word = total_duration / num_words

            # Start playing the audio
            pygame.mixer.music.play()

            # Print words in real-time
            for word in words:
                print(word, end=" ", flush=True)  # Print word by word
                time.sleep(duration_per_word)  # Wait for the duration of the word

            print()  # New line after the sentence

            # Wait until the audio finishes playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Add a small delay to avoid high CPU usage

            # Clean up
            pygame.mixer.quit()
        except Exception as e:
            print(f"Text-to-speech error: {e}")

# Example usage
if __name__ == "__main__":
    tts = TextToSpeech()
    tts.speak_text("Hello, how are you?", lang="en")  # English
    tts.speak_text("नमस्ते, आप कैसे हैं?", lang="hi")  # Hindi
    tts.speak_text("ਹੈਲੋ, ਤੁਸੀ ਕਿਵੇਂ ਹੋ?", lang="pa")  # Punjabi

