import speech_recognition as sr
from langdetect import detect, DetectorFactory

# Fix randomness in language detection
DetectorFactory.seed = 0

def detect_and_print_speech():
    """Listen to speech, detect its language, and print the text."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        try:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)

            # Try recognizing in multiple languages
            for lang in ["pa-IN", "en-US"]:
                try:
                    recognized_text = recognizer.recognize_google(audio, language=lang)
                    detected_lang = detect(recognized_text)  # Detect language
                    print(f"Detected Language: {detected_lang.upper()}")
                    print(f"Recognized Text: {recognized_text}")
                    return detected_lang, recognized_text
                except sr.UnknownValueError:
                    continue  # Try the next language
            
            print("Could not understand the speech in any supported language.")
            return None, None

        except sr.RequestError as e:
            print(f"Speech recognition request error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    return None, None

# Call the function to test
detect_and_print_speech()
