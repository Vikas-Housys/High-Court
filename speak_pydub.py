import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

class TextToSpeech:
    def speak_text(self, text, lang="en"):
        try:
            # Remove existing file if it exists
            if os.path.exists("speech.mp3"):
                os.remove("speech.mp3")

            # Convert text to speech and save as MP3
            tts = gTTS(text=text, lang=lang)
            tts.save("speech.mp3")

            # Load and play the audio using pydub
            audio = AudioSegment.from_file("speech.mp3", format="mp3")
            play(audio)  # This plays the audio in the background
        except Exception as e:
            print(f"Text-to-speech error: {e}")

# Example usage
if __name__ == "__main__":
    tts = TextToSpeech()
    tts.speak_text("Hello, how are you?", lang="en")  # English
    tts.speak_text("नमस्ते, आप कैसे हैं?", lang="hi")  # Hindi
    tts.speak_text("ਹੈਲੋ, ਤੁਸੀ ਕਿਵੇਂ ਹੋ?", lang="pa")  # Punjabi