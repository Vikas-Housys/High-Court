import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import re

def number_to_words(text):
    number_words = {
        "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
        "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"
    }
    for num, word in number_words.items():
        text = text.replace(num, word)
    return text


def map_spoken_numbers(text, lang='en'):
    # Mapping for Punjabi numbers
    punjabi_numbers = {
        "੦": "0", "੧": "1", "੨": "2", "੩": "3", "੪": "4",
        "੫": "5", "੬": "6", "੭": "7", "੮": "8", "੯": "9",
        "ਸਿਫਰ": "0", "ਇੱਕ": "1", "ਦੋ": "2", "ਤਿੰਨ": "3", "ਚਾਰ": "4",
        "ਪੰਜ": "5", "ਛੇ": "6", "ਸੱਤ": "7", "ਅੱਠ": "8", "ਨੌਂ": "9"
    }

    # Mapping for Hindi numbers
    hindi_numbers = {
        "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
        "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
        "शून्य": "0", "एक": "1", "दो": "2", "तीन": "3", "चार": "4",
        "पांच": "5", "छह": "6", "सात": "7", "आठ": "8", "नौ": "9"
    }

    # Mapping for English numbers
    english_numbers = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
    }

    # Combine all mappings based on the language
    if lang == 'pa':
        number_mapping = punjabi_numbers
    elif lang == 'hi':
        number_mapping = hindi_numbers
    else:
        number_mapping = english_numbers

    # Replace spoken numbers with their numeric equivalents
    for word, num in number_mapping.items():
        text = text.replace(word, num)

    return text

case_types_names = ['CWP', 'CRM-M', 'CR', 'RSA', 'CRR', 'CRA-S', 'FAO', 'CM', 'CRM', 
              'ARB', 'ARB-DC', 'ARB-ICA', 'CA', 'CA-CWP', 'CA-MISC', 'CACP', 
              'CAPP', 'CCEC', 'CCES', 'CEA', 'CEC', 'CEGC', 'CESR', 'CLAIM', 
              'CM-INCOMP', 'CMA', 'CMM', 'CO', 'CO-COM', 'COA', 'COCP', 'COMM-PET-M', 
              'CP', 'CP-MISC', 'CR-COM', 'CRA', 'CRA-AD', 'CRA-AS', 'CRA-D', 
              'CRACP', 'CREF', 'CRM-A', 'CRM-CLT-OJ', 'CRM-W', 'CROCP', 'CRR(F)', 
              'CRREF', 'CRWP', 'CS', 'CS-OS', 'CUSAP', 'CWP-COM', 'CWP-PIL', 'DP', 
              'EA', 'EDC', 'EDREF', 'EFA', 'EFA-COM', 'EP', 'EP-COM', 'ESA', 'FAO(FC)', 
              'FAO-C', 'FAO-CARB', 'FAO-COM', 'FAO-ICA', 'FAO-M', 'FEMA-APPL', 'FORM-8A', 
              'GCR', 'GSTA', 'GSTR', 'GTA', 'GTC', 'GTR', 'GVATR', 'INCOMP', 'INTTA', 
              'IOIN', 'ITA', 'ITC', 'ITR', 'LPA', 'LR', 'MATRF', 'MRC', 'O&M', 'OLR', 
              'PBPT-APPL', 'PBT', 'PMLA-APPL', 'PVR', 'RA', 'RA-CA', 'RA-CP', 'RA-CR', 
              'RA-CW', 'RA-LP', 'RA-RF', 'RA-RS', 'RCRWP', 'RERA-APPL', 'RFA', 'RFA-COM', 
              'RP', 'SA', 'SAO', 'SAO(FS)', 'SDR', 'STA', 'STC', 'STR', 'TA', 'TA-COM', 
              'TC', 'TCRIM', 'TEST', 'UVA', 'UVR', 'VATAP', 'VATCASE', 'VATREF', 'WTA', 
              'WTC', 'WTR', 'XOBJ', 'XOBJC', 'XOBJL', 'XOBJR', 'XOBJS']

def listen_case_type(case_types):
    
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(f"Please say the case type : {case_types_names}")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        audio = recognizer.listen(source)

        try:
            # Recognize the speech input
            recognized_text = recognizer.recognize_google(audio)
            print(f"Recognized case type: {recognized_text}")

            # Convert recognized text to uppercase for case-insensitive matching
            recognized_text = recognized_text.upper()

            # Check if the recognized text matches a key or value in the case_types dictionary
            for key, value in case_types.items():
                if recognized_text == key.upper() or recognized_text == value.upper():
                    return key  # Return the abbreviation (key)

            # If no match is found, display an error message
            print(f"Invalid case type: {recognized_text}. Valid case types are: {list(case_types.keys())}")
            return None

        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return None


def listen_case_number(lang='en'):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(f"Please say the case number in {lang}:")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        audio = recognizer.listen(source)

        try:
            # Recognize the speech input
            recognized_text = recognizer.recognize_google(audio, language=lang)
            print(f"Recognized case number: {recognized_text}")

            # Map spoken numbers to numeric equivalents
            recognized_text = map_spoken_numbers(recognized_text, lang)

            # Replace common misinterpretations (e.g., "O" with "0")
            recognized_text = recognized_text.replace("O", "0").replace("o", "0")

            # Replace spaces with a dash to handle cases like "2743 lpa" -> "2743-lpa"
            recognized_text = recognized_text.replace(" ", "-")

            # Split the recognized text into parts (e.g., "2743-lpa" -> ["2743", "lpa"])
            parts = recognized_text.split("-")

            # Ensure the alphanumeric part (if present) is in uppercase
            if len(parts) > 1:
                parts[1] = parts[1].upper()  # Convert to uppercase (e.g., "lpa" -> "LPA")

            # Reconstruct the case number with uppercase letters
            structured_case_number = "-".join(parts)

            # Validate the case number format (digits followed by optional dash and letters/numbers)
            # Example: "10925-CII", "1551-CI", "2357-LPA", or "2357"
            if re.match(r'^\d+(-\w+)?$', structured_case_number):
                return structured_case_number
            else:
                print(f"Invalid case number: {structured_case_number}. Case number must be in the format 'XXXX-XXX' or 'XXXX'.")
                return None

        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return None
    
def listen_case_year(lang='en'):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(f"Please say the case year in {lang}:")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        audio = recognizer.listen(source)

        try:
            # Recognize the speech input
            recognized_text = recognizer.recognize_google(audio, language=lang)
            print(f"Recognized case year: {recognized_text}")

            # Map spoken numbers to numeric equivalents
            recognized_text = map_spoken_numbers(recognized_text, lang)

            # Replace common misinterpretations (e.g., "O" with "0")
            recognized_text = recognized_text.replace("O", "0").replace("o", "0")

            # Validate the case year (must be numeric and 4 digits)
            if recognized_text.isdigit() and len(recognized_text) == 4:
                return recognized_text
            else:
                print(f"Invalid case year: {recognized_text}. Case year must be a 4-digit number.")
                return None

        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return None


def listen_case_id(case_types, lang='en'):
    # Listen for the case type
    case_type = listen_case_type(case_types)
    if not case_type:
        return None

    # Listen for the case number
    case_number = listen_case_number(lang)
    if not case_number:
        return None

    # Listen for the case year
    case_year = listen_case_year(lang)
    if not case_year:
        return None

    # Return the combined case ID
    case_id = f"{case_type}-{case_number}-{case_year}"
    print(f"Valid case ID: {case_id}")
    return case_id


def speak_text(text, lang="en"):
    try:
        # Remove the existing file if it exists
        if os.path.exists("speech.mp3"):
            os.remove("speech.mp3")

        # Convert numbers to words for better pronunciation
        text = number_to_words(text)

        # Generate the speech file
        tts = gTTS(text=text, lang=lang)
        tts.save("speech.mp3")

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load("speech.mp3")

        # Play the audio
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Clean up
        pygame.mixer.quit()
    except Exception as e:
        print(f"Text-to-speech error: {e}")


# Dictionary of case types (abbreviation: full form)
case_types = {
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

# Main program
if __name__ == "__main__":
    # Set the language for case number and year input
    lang = 'en'  # Change to 'hi' for Hindi or 'en' for English

    # Listen for a case ID
    case_id = listen_case_id(case_types, lang)

    # If a valid case ID is recognized, speak it back to the user
    if case_id:
        speak_text(f"The case ID is {case_id}", lang="en")
    else:
        speak_text("No valid case ID was recognized. Please try again.", lang="en")

