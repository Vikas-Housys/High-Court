import customtkinter as ctk
import speech_recognition as sr
import re
from difflib import get_close_matches

class SpeechRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Case ID Listener")
        self.root.geometry("500x400")

        # CustomTkinter styling
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create a frame for the UI
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Label for instructions
        self.instruction_label = ctk.CTkLabel(self.frame, text="Please speak the case type, number, and year.", font=("Arial", 14))
        self.instruction_label.pack(pady=10)

        # Text input field to display recognized text
        self.text_input = ctk.CTkEntry(self.frame, width=300, font=("Arial", 12))
        self.text_input.pack(pady=10)

        # Subtitle label for feedback
        self.subtitle_label = ctk.CTkLabel(self.frame, text="", font=("Arial", 12))
        self.subtitle_label.pack(pady=10)

        # Start button to initiate listening
        self.start_button = ctk.CTkButton(self.frame, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=20)

    def number_to_words(self, text):
        self.number_words = {
            "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
            "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"
        }
        for num, word in self.number_words.items():
            text = text.replace(num, word)
        return text

    def map_spoken_numbers(self, text, lang='en'):
        # Mapping for Punjabi numbers
        self.punjabi_numbers = {
            "੦": "0", "੧": "1", "੨": "2", "੩": "3", "੪": "4",
            "੫": "5", "੬": "6", "੭": "7", "੮": "8", "੯": "9",
            "ਸਿਫਰ": "0", "ਇੱਕ": "1", "ਦੋ": "2", "ਤਿੰਨ": "3", "ਚਾਰ": "4",
            "ਪੰਜ": "5", "ਛੇ": "6", "ਸੱਤ": "7", "ਅੱਠ": "8", "ਨੌਂ": "9"
        }

        # Mapping for Hindi numbers
        self.hindi_numbers = {
            "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
            "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
            "शून्य": "0", "एक": "1", "दो": "2", "तीन": "3", "चार": "4",
            "पांच": "5", "छह": "6", "सात": "7", "आठ": "8", "नौ": "9"
        }

        # Mapping for English numbers
        self.english_numbers = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
        }

        # Combine all mappings based on the language
        if lang == 'pa':
            number_mapping = self.punjabi_numbers
        elif lang == 'hi':
            number_mapping = self.hindi_numbers
        else:
            number_mapping = self.english_numbers

        # Replace spoken numbers with their numeric equivalents
        for word, num in number_mapping.items():
            text = text.replace(word, num)

        return text

    def listen_case_type(self, case_types):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Please say the case type: ")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            try:
                # Recognize the speech input
                recognized_text = recognizer.recognize_google(audio)
                print(f"Recognized case type: {recognized_text}")

                # Convert recognized text to uppercase for case-insensitive matching
                recognized_text = recognized_text.upper()

                # Find the closest match in the case_types dictionary
                closest_match = get_close_matches(recognized_text, case_types.keys(), n=1, cutoff=0.6)

                if closest_match:
                    # Return the closest match (abbreviation)
                    return closest_match[0]
                else:
                    # If no close match is found, check if the recognized text matches any full form
                    for key, value in case_types.items():
                        if recognized_text == value.upper():
                            return key  # Return the abbreviation (key)

                    # If no match is found, display an error message
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
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            try:
                # Recognize the speech input
                recognized_text = recognizer.recognize_google(audio, language=lang)
                print(f"Recognized case number: {recognized_text}")

                # Map spoken numbers to numeric equivalents
                recognized_text = self.map_spoken_numbers(recognized_text, lang)

                # Replace common misinterpretations (e.g., "O" with "0")
                recognized_text = recognized_text.replace("O", "0").replace("o", "0")

                # Replace spaces with a dash to handle cases like "2743 lpa" -> "2743-lpa"
                recognized_text = recognized_text.replace(" ", "-")

                # Extract the numeric part (digits) and alphanumeric part (letters/numbers)
                parts = recognized_text.split("-")

                # Initialize variables for numeric and alphanumeric parts
                numeric_part = ""
                alphanumeric_part = ""

                # Iterate through the parts to identify numeric and alphanumeric parts
                for part in parts:
                    if part.isdigit():
                        numeric_part = part  # Assign the numeric part
                    else:
                        alphanumeric_part = part.upper()  # Assign the alphanumeric part and convert to uppercase

                # If no numeric part is found, return None
                if not numeric_part:
                    print(f"Invalid case number: {recognized_text}. Numeric part is missing.")
                    return None

                # Combine the numeric part and alphanumeric part with a dash
                structured_case_number = f"{numeric_part}-{alphanumeric_part}" if alphanumeric_part else numeric_part

                # Validate the case number format (digits followed by optional dash and letters/numbers)
                # Example: "10925-CII", "1551-CI", "2357-LPA", or "2357"
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
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            try:
                # Recognize the speech input
                recognized_text = recognizer.recognize_google(audio, language=lang)

                # Map spoken numbers to numeric equivalents
                recognized_text = self.map_spoken_numbers(recognized_text, lang)

                # Replace common misinterpretations (e.g., "O" with "0")
                recognized_text = recognized_text.replace("O", "0").replace("o", "0")
                print(f"Case Year: {recognized_text}")

                # Validate the case year (must be numeric and 4 digits)
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
        # Listen for the case type
        self.subtitle_label.configure(text="Listening Case Type...")
        self.root.update()
        case_type = self.listen_case_type(case_types)
        if case_type:
            self.text_input.delete(0, ctk.END)
            self.text_input.insert(0, str(case_type))
            self.root.update()
        else:
            return None

        # Listen for the case number
        self.subtitle_label.configure(text="Listening Case Number...")
        self.root.update()
        case_number = self.listen_case_number(lang)
        if case_number:
            self.text_input.delete(0, ctk.END)
            self.text_input.insert(0, f"{case_type}-{case_number}")
            self.root.update()
        else:
            return None

        # Listen for the case year
        self.subtitle_label.configure(text="Listening Case Year...")
        self.root.update()
        case_year = self.listen_case_year(lang)
        if case_year:
            self.text_input.delete(0, ctk.END)
            self.text_input.insert(0, f"{case_type}-{case_number}-{case_year}")
            self.root.update()
        else:
            return None

        # Return the combined case ID
        case_id = f"{case_type}-{case_number}-{case_year}"
        print(f"Valid Case ID: {case_id}")

        return case_id

    def start_listening(self):
        # Define case types (abbreviation: full form)
        self.case_types = {
            "CWP": "CIVIL WRIT PETITION", "CRM-M": "CRIMINAL MAIN", "CR": "CIVIL REVISION",
            "RSA": "REGULAR SECOND APPEAL", "CRR": "CRIMINAL REVISION", "CRA-S": "CRIMINAL APPEAL SB",
            "FAO": "FIRST APPEAL ORDER", "CM": "CIVIL MISC", "CRM": "CRIMINAL MISCELLANEOUS PETITION",
            "ARB": "ARBITRATION ACT CASE (WEF 15/10/03)", "ARB-DC": "ARBITRATION CASE (DOMESTIC COMMERCIAL)", "ARB-ICA": "ARBITRATION CASE (INTERNATIONAL COMM ARBITRATION)",
            "CA": "CIVIL APPEAL/COMPANY APPLICATION", "CA-CWP": "COMMERCIAL APPEAL (WRIT)", "CA-MISC": "COMMERCIAL APPEAL (MISC)",
            "CACP": "CONTEMPT APPEALS", "CAPP": "COMPANY APPEAL", "CCEC": "CUSTOM CENTRAL EXCISE CASE",
            "CCES": "CCES", "CEA": "CENTRAL EXCISE APPEAL (WEF 10-11-2003)", "CEC": "CENTRAL EXCISE CASE",
            "CEGC": "CENTRAL EXCISE GOLD CASE", "CESR": "CENTRAL EXCISE AND SALT REFERENCE", "CLAIM": "CLAIMS",
            "CM-INCOMP": "Misc Appl. in Incomplete Case", "CMA": "COMPANY MISC. APPLICATION", "CMM": "HMA CASES U/S 24",
            "CO": "CIVIL ORIGINAL", "CO-COM": "CIVIL ORIGINAL (COMMERCIAL)", "COA": "COMPANY APPLICATION",
            "COCP": "CIVIL ORIGINAL CONTEMPT PETITION", "COMM-PET-M": "COMMERCIAL PETITION MAIN", "CP": "COMPANY PETITIONS",
            "CP-MISC": "COMMERCIAL PETITION (MISC)", "CR-COM": "CIVIL REVISION (COMMERCIAL)", "CRA": "CRIMINAL APPEAL",
            "CRA-AD": "CRIMINAL APPEAL ACQUITTAL DB", "CRA-AS": "CRIMINAL APPEAL ACQUITTAL SB", "CRA-D": "CRIMINAL APPEAL DB",
            "CRACP": "CRIMINAL APPEAL CONTEMPT PETITION", "CREF": "CIVIL REFERENCE", "CRM-A": "AGAINST ACQUITTALS",
            "CRM-CLT-OJ": "CRIMINAL COMPLAINT (ORIGINAL SIDE)", "CRM-W": "CRM IN CRWP", "CROCP": "CRIMINAL ORIGINAL CONTEMPT PETITION",
            "CRR(F)": "CRIMINAL REVISION (FAMILY COURT)", "CRREF": "CRIMINAL REFERENCE", "CRWP": "CRIMINAL WRIT PETITION",
            "CS": "CIVIL SUIT", "CS-OS": "CIVIL SUIT-ORIGINAL SIDE", "CUSAP": "CUSTOM APPEAL (WEF 17/7/2004)",
            "CWP-COM": "CIVIL WRIT PETITION (COMMERCIAL)", "CWP-PIL": "CIVIL WRIT PETITION PUBLIC INTEREST LITIGATION", "DP": "DIVORCE PETITION",
            "EA": "EXECUTION APPL", "EDC": "ESTATE DUTY CASE", "EDREF": "ESTATE DUTY REFERENCE",
            "EFA": "EXECUTION FIRST APPEAL", "EFA-COM": "EXECUTION FIRST APPEAL (COMMERCIAL)", "EP": "ELECTION PETITIONS",
            "EP-COM": "EXECUTION PETITION (COMMERCIAL)", "ESA": "EXECUTION SECOND APPEAL", "FAO(FC)": "FAO (FAMILY COURT)",
            "FAO-C": "FAO (CUS AND MTC)", "FAO-CARB": "FIRST APPEAL FROM ORDER (COMMERCIAL ARBITRATION)", "FAO-COM": "FIRST APPEAL FROM ORDER (COMMERCIAL)",
            "FAO-ICA": "FIRST APPEAL FROM ORDER (INTERNATIONAL COMM ARBI.)", "FAO-M": "FIRST APPEAL ORDER-MATRIMONIAL", "FEMA-APPL": "FEMA APPEAL",
            "FORM-8A": "FORM-8A", "GCR": "GOLD CONTROL REFERENCE", "GSTA": "GOODS AND SERVICES TAX APPEAL",
            "GSTR": "GENERAL SALES TAX REFERENCE", "GTA": "GIFT TAX APPEAL", "GTC": "GIFT TAX CASE",
            "GTR": "GIFT TAX REFERENCE", "GVATR": "GENERAL VAT REFERENCES", "INCOMP": "INCOMPLETE OBJECTION CASE",
            "INTTA": "INTEREST TAX APPEAL", "IOIN": "INTERIM ORDER IN", "ITA": "INCOME TAX APPEAL",
            "ITC": "INCOME TAX CASES", "ITR": "INCOME TAX REFERENCE", "LPA": "LATTER PATENT APPEALS",
            "LR": "LIQUIDATOR REPORT", "MATRF": "MATROMONIAL REFERENCE", "MRC": "MURDER REFERENCE CASE",
            "O&M": "ORIGINAL & MISCELLANEOUS", "OLR": "OFFICIAL LIQUIDATOR REPORT", "PBPT-APPL": "PROHIBITION OF BENAMI PROPERTY TRANSACTION APPEAL",
            "PBT": "PROBATE", "PMLA-APPL": "PREVENTION OF MONEY LAUNDERING APPEAL", "PVR": "PB VAT REVISION",
            "RA": "REVIEW APPL", "RA-CA": "REVIEW IN COMPANY APPEAL", "RA-CP": "REVIEW IN COMPANY PETITION",
            "RA-CR": "REVIEW IN CR", "RA-CW": "REVIEW IN CWP", "RA-LP": "REVIEW IN LPA",
            "RA-RF": "REVIEW APPLICATION IN RFA", "RA-RS": "REVIEW IN RSA", "RCRWP": "REVIEW IN CRCWP",
            "RERA-APPL": "RERA APPEAL", "RFA": "REGULAR FIRST APPEAL", "RFA-COM": "REGULAR FIRST APPEAL (COMMERCIAL)",
            "RP": "RECRIMINATION PETITION", "SA": "SERVICE APPEAL", "SAO": "SECOND APPEAL ORDER",
            "SAO(FS)": "SAO FOOD SAFETY", "SDR": "STATE DUTY REFERENCE", "STA": "SALES TAX APPEAL",
            "STC": "SALES TAX CASES", "STR": "SALE TAX REFERENCE", "TA": "TRANSFER APPLICATION",
            "TA-COM": "TRANSFER APPLICATION (COMMERCIAL)", "TC": "TAKENUP CASES", "TCRIM": "TRANSFER CRIMINAL PETITION",
            "TEST": "TEST", "UVA": "UT VAT APPEAL", "UVR": "UT VAT REVISION", "VATAP": "VAT APPEAL",
            "VATCASE": "VALUE ADDED TAX CASE", "VATREF": "VAT REFERENCE",
            "WTA": "WEALTH TAX APPEAL", "WTC": "WEALTH TAX CASES",
            "WTR": "WEALTH TAX REFERENCE", "XOBJ": "CROSS OBJECTION", "XOBJC": "CROSS OBJECTION IN CR",
            "XOBJL": "CROSS OBJECTION IN LPA", "XOBJR": "CROSS OBJECTION IN RFA", "XOBJS": "CROSS OBJECTION IN RSA",
        }

        # Start listening for the case ID
        case_id = self.listen_case_id(self.case_types)
        if case_id:
            self.subtitle_label.configure(text=f"Case ID recognized: {case_id}")
        else:
            self.subtitle_label.configure(text="Failed to recognize a valid Case ID.")

# Main application
if __name__ == "__main__":
    root = ctk.CTk()
    app = SpeechRecognitionApp(root)
    root.mainloop()
