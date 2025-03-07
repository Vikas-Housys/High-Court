import speech_recognition as sr
import customtkinter as ctk
from tkinter import messagebox
import os
import time
import pygame
from gtts import gTTS
from deep_translator import GoogleTranslator

class VoiceAssistant:
    def __init__(self, root):
        self.root = root
        self._translators = {}
        self.subtitle_label = ctk.CTkLabel(root, text="")
        self.text_input = ctk.CTkEntry(root)
        
        # Mapping for Hindi & Punjabi numerals to English digits
        self.hindi_punjabi_digit_map = {
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', 
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
            '੦': '0', '੧': '1', '੨': '2', '੩': '3', '੪': '4', 
            '੫': '5', '੬': '6', '੭': '7', '੮': '8', '੯': '9'
        }

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

    def speak_text(self, text, lang="pa"):
        """Convert text to speech and play it."""
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
            duration_per_word = total_duration / max(num_words, 1)

            pygame.mixer.music.play()
            self.subtitle_label.configure(text="")
            start_time = time.time()

            for word in words:
                self.subtitle_label.configure(text=self.subtitle_label.cget("text") + " " + word)
                self.root.update()

                elapsed_time = time.time() - start_time
                expected_time = duration_per_word * (words.index(word) + 1)
                sleep_time = max(0, expected_time - elapsed_time)
                time.sleep(sleep_time)

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.quit()
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            messagebox.showerror("TTS Error", f"Could not speak the text: {e}")

    def convert_to_english_digits(self, text):
        """Convert Hindi & Punjabi numerals to standard English digits."""
        return ''.join(self.hindi_punjabi_digit_map.get(char, char) for char in text)

    def listen(self):
        """Listen for user input and try different languages if needed."""
        recognizer = sr.Recognizer()
        
        # List of languages to try in order of preference
        languages = ["pa-IN", "hi-IN", "en-IN", "en-US"]
        
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source)
                self.subtitle_label.configure(text="Listening...")
                self.root.update()
                
                audio = recognizer.listen(source, timeout=5)
                
                # Try each language until one works
                recognized_text = None
                for lang in languages:
                    try:
                        text = recognizer.recognize_google(audio, language=lang)
                        print(f"Recognized with {lang}: {text}")
                        recognized_text = text
                        break
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        print(f"Error with {lang}: {e}")
                        continue
                
                if recognized_text is None:
                    messagebox.showerror("Error", "Could not understand audio in any language.")
                    return ""
                
                # Convert any Hindi/Punjabi numerals to English
                converted_text = self.convert_to_english_digits(recognized_text)
                print(f"Converted text: {converted_text}")
                
                return converted_text
                
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand audio.")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Could not request results; {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                
        return ""

    def process_case_number(self, case_number, lang="en"):
        """Process the case number from user input."""
        # Placeholder for your case processing logic
        response = f"Processing case number: {case_number}"
        translated_response = self.translate_text(response, source="en", target=lang)
        self.speak_text(translated_response, lang=lang)

    def conversation(self, lang="pa"):
        """Engage in a conversation based on user input."""
        prompt_text = """
            Kindly tell me, how would you like to get the details?
            1. Case Search
            2. Judgment Search
            3. Filing Search
        """

        # Translate prompt if needed
        translated_prompt = self.translate_text(prompt_text, source="en", target=lang)
        self.speak_text(translated_prompt, lang=lang)

        # Listen for user input
        user_response = self.listen()
        if not user_response:
            return
            
        # Display the recognized response
        self.text_input.delete(0, ctk.END)
        self.text_input.insert(0, user_response)
        self.root.update()
        
        # Extract any digits from the response
        digits_only = ''.join(filter(str.isdigit, user_response))

        if digits_only:
            if digits_only == "1":
                self.handle_case_search(lang)
            elif digits_only == "2":
                self.handle_judgment_search(lang)
            elif digits_only == "3":
                self.handle_filing_search(lang)
            else:
                response = "I didn't understand your choice. Please try again."
                translated_response = self.translate_text(response, source="en", target=lang)
                self.speak_text(translated_response, lang=lang)
        else:
            # Try to identify the option from text
            response_lower = user_response.lower()
            if "case" in response_lower or "one" in response_lower or "1" in response_lower:
                self.handle_case_search(lang)
            elif "judgment" in response_lower or "two" in response_lower or "2" in response_lower:
                self.handle_judgment_search(lang)
            elif "filing" in response_lower or "three" in response_lower or "3" in response_lower:
                self.handle_filing_search(lang)
            else:
                response = "I couldn't understand your choice. Please try again."
                translated_response = self.translate_text(response, source="en", target=lang)
                self.speak_text(translated_response, lang=lang)

    def handle_case_search(self, lang):
        """Handle the case search option."""
        prompt = "Please say the case number."
        translated_prompt = self.translate_text(prompt, source="en", target=lang)
        self.speak_text(translated_prompt, lang=lang)
        
        case_number = self.listen()
        if case_number:
            # Convert any Hindi/Punjabi digits
            case_number = self.convert_to_english_digits(case_number)
            # Extract digits
            digits_only = ''.join(filter(str.isdigit, case_number))
            if digits_only:
                self.process_case_number(digits_only, lang)
            else:
                response = "No valid case number found. Please try again."
                translated_response = self.translate_text(response, source="en", target=lang)
                self.speak_text(translated_response, lang=lang)

    def handle_judgment_search(self, lang):
        """Handle the judgment search option."""
        response = "Judgment search selected. This feature is coming soon."
        translated_response = self.translate_text(response, source="en", target=lang)
        self.speak_text(translated_response, lang=lang)

    def handle_filing_search(self, lang):
        """Handle the filing search option."""
        response = "Filing search selected. This feature is coming soon."
        translated_response = self.translate_text(response, source="en", target=lang)
        self.speak_text(translated_response, lang=lang)
