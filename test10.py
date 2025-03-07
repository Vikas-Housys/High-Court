import speech_recognition as sr
import re
import customtkinter as ctk
from difflib import get_close_matches

class CaseListener:
    def __init__(self, root, subtitle_label, text_input, case_types):
        self.root = root
        self.subtitle_label = subtitle_label
        self.text_input = text_input
        self.case_types = case_types

    def number_to_words(self, text):
        self.number_words = {
            "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
            "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"
        }
        for num, word in self.number_words.items():
            text = text.replace(num, word)
        return text

    def map_spoken_numbers(self, text, lang='en'):
        self.punjabi_numbers = {
            "੦": "0", "੧": "1", "੨": "2", "੩": "3", "੪": "4",
            "੫": "5", "੬": "6", "੭": "7", "੮": "8", "੯": "9",
            "ਸਿਫਰ": "0", "ਇੱਕ": "1", "ਦੋ": "2", "ਤਿੰਨ": "3", "ਚਾਰ": "4",
            "ਪੰਜ": "5", "ਛੇ": "6", "ਸੱਤ": "7", "ਅੱਠ": "8", "ਨੌਂ": "9"
        }

        self.hindi_numbers = {
            "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
            "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
            "शून्य": "0", "एक": "1", "दो": "2", "तीन": "3", "चार": "4",
            "पांच": "5", "छह": "6", "सात": "7", "आठ": "8", "नौ": "9"
        }

        self.english_numbers = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
        }

        if lang == 'pa':
            number_mapping = self.punjabi_numbers
        elif lang == 'hi':
            number_mapping = self.hindi_numbers
        else:
            number_mapping = self.english_numbers

        for word, num in number_mapping.items():
            text = text.replace(word, num)

        return text

    def listen_case_type(self, case_types):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Please say the case type: ")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

            try:
                recognized_text = recognizer.recognize_google(audio)
                recognized_text = recognized_text.upper()
                print(f"Recognized case type: {recognized_text}")

                closest_match = get_close_matches(recognized_text, case_types.keys(), n=1, cutoff=0.6)

                if closest_match:
                    return closest_match[0]
                else:
                    for key, value in case_types.items():
                        if recognized_text == value.upper():
                            return key

                    print(f"Invalid case type: {recognized_text}. Valid case types are: {list(case_types.keys())}")
                    return None

            except sr.UnknownValueError:
                self.subtitle_label.configure(text="Sorry, I could not understand the audio."); self.root.update()
            except sr.RequestError as e:
                self.subtitle_label.configure(text=f"Could not request results from the speech recognition service; {e}"); self.root.update()
            except Exception as e:
                self.subtitle_label.configure(text=f"An error occurred: {e}"); self.root.update()

            return None

    def listen_case_number(self, lang='en'):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print(f"Please say the case number: ")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

            try:
                recognized_text = recognizer.recognize_google(audio, language=lang)
                print(f"Recognized case number: {recognized_text}")

                recognized_text = self.map_spoken_numbers(recognized_text, lang)
                recognized_text = recognized_text.replace("O", "0").replace("o", "0")
                recognized_text = recognized_text.replace(" ", "-")

                parts = recognized_text.split("-")
                numeric_part = ""
                alphanumeric_part = ""

                for part in parts:
                    if part.isdigit():
                        numeric_part = part
                    else:
                        alphanumeric_part = part.upper()

                if not numeric_part:
                    print(f"Invalid case number: {recognized_text}. Numeric part is missing.")
                    return None

                structured_case_number = f"{numeric_part}-{alphanumeric_part}" if alphanumeric_part else numeric_part

                if re.match(r'^\d+(-\w+)?$', structured_case_number):
                    return structured_case_number
                else:
                    print(f"Invalid case number: {structured_case_number}. Case number must be in the format 'XXXX-XXX' or 'XXXX'.")
                    return None

            except sr.UnknownValueError:
                self.subtitle_label.configure(text="Sorry, I could not understand the audio."); self.root.update()
            except sr.RequestError as e:
                self.subtitle_label.configure(text=f"Could not request results from the speech recognition service; {e}"); self.root.update()
            except Exception as e:
                print()
                self.subtitle_label.configure(text=f"An error occurred: {e}"); self.root.update()

            return None

    def listen_case_year(self, lang='en'):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

            try:
                recognized_text = recognizer.recognize_google(audio, language=lang)
                recognized_text = self.map_spoken_numbers(recognized_text, lang)
                recognized_text = recognized_text.replace("O", "0").replace("o", "0")
                print(f"Case Year: {recognized_text}")

                if recognized_text.isdigit() and len(recognized_text) == 4:
                    return recognized_text
                else:
                    print(f"Invalid case year: {recognized_text}. Case year must be a 4-digit number.")
                    return None

            except sr.UnknownValueError:
                self.subtitle_label.configure(text="Sorry, I could not understand the audio."); self.root.update()
            except sr.RequestError as e:
                self.subtitle_label.configure(text=f"Could not request results from the speech recognition service; {e}"); self.root.update()
            except Exception as e:
                self.subtitle_label.configure(text=f"An error occurred: {e}"); self.root.update()

            return None

    def listen_case_id(self, case_types, lang='en'):
        self.subtitle_label.configure(text="Listening Case Type...")
        self.root.update()
        case_type = self.listen_case_type(case_types)
        if case_type:
            self.text_input.delete(0, ctk.END)
            self.text_input.insert(0, str(case_type))
            self.root.update()
        else:
            return None

        self.subtitle_label.configure(text="Listening Case Number...")
        self.root.update()
        case_number = self.listen_case_number(lang)
        if case_number:
            self.text_input.delete(0, ctk.END)
            self.text_input.insert(0, f"{case_type}-{case_number}")
            self.root.update()
        else:
            return None

        self.subtitle_label.configure(text="Listening Case Year...")
        self.root.update()
        case_year = self.listen_case_year(lang)
        if case_year:
            self.text_input.delete(0, ctk.END)
            self.text_input.insert(0, f"{case_type}-{case_number}-{case_year}")
            self.root.update()
        else:
            return None

        case_id = f"{case_type}-{case_number}-{case_year}"
        print(f"Valid Case ID: {case_id}")

        return case_id

    def conversation(self, lang="en"):
        case_types = self.case_types
        search_type = "case search"  # remove it later

        if search_type == 'case search':
            self.speak_text("Kindly speak case number. ", lang=lang)
            case_id = self.listen_case_id(case_types, lang=lang)
            self.speak_text(f"Your case number is {case_id}.")
            if case_id:
                self.text_input.delete(0, ctk.END)
                self.text_input.insert(0, case_id)
                self.root.update()

                self.process_case_details(case_id, lang)
        else:
            self.speak_text("No case found.")

    def speak_text(self, text, lang='en'):
        # Placeholder for text-to-speech functionality
        print(f"Speaking: {text}")

    def process_case_details(self, case_id, lang='en'):
        # Placeholder for processing case details
        print(f"Processing case details for: {case_id}")


# Create the main application window
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Case Listener Test")
        self.root.geometry("400x300")

        # Create a label for subtitles
        self.subtitle_label = ctk.CTkLabel(root, text="Subtitles will appear here", font=("Arial", 12))
        self.subtitle_label.pack(pady=10)

        # Create a text input field
        self.text_input = ctk.CTkEntry(root, width=300, font=("Arial", 12))
        self.text_input.pack(pady=10)

        # Create a button to start the conversation
        self.start_button = ctk.CTkButton(root, text="Start Conversation", command=self.start_conversation)
        self.start_button.pack(pady=10)

        # Define case types
        self.case_types = {
            "CIV": "Civil",
            "CRIM": "Criminal",
            "FAM": "Family",
            "PROB": "Probate"
        }

        # Initialize CaseListener
        self.case_listener = CaseListener(root, self.subtitle_label, self.text_input, self.case_types)

    def start_conversation(self):
        # Start the conversation in English
        self.case_listener.conversation(lang="en")


# Run the application
if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()


