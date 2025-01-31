import os
import json
from gtts import gTTS
import pygame
import time
import customtkinter as ctk
from tkinter import messagebox, ttk
from deep_translator import GoogleTranslator
import speech_recognition as sr
from PIL import Image
import uuid  # For generating unique filenames

class HighCourt:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.title("Court Case Information System")
        self.root.attributes("-fullscreen", True)  # Open in full screen by default

        # Set customtkinter appearance
        ctk.set_appearance_mode("light")  # Options: "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

        # Initialize pygame mixer once
        pygame.mixer.init()

        # Load court database
        self.load_court_database()

        # Load authentication data
        self.load_auth_data()

        # Create main frame
        self.main_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # Add heading above the title
        self.heading_label = ctk.CTkLabel(
            self.main_frame,
            text="Session Court Case Management",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color="blue",  # Blue color
        )
        self.heading_label.pack(fill="x", pady=10)

        # Load and resize header image once
        self.header_image = self.load_image("images/court03.png", (960, 400))
        if self.header_image:
            self.image_frame = ctk.CTkFrame(
                self.main_frame,
                width=850,
                height=330,
                fg_color="transparent",
                border_width=3,
                border_color="black",
                corner_radius=10,
            )
            self.image_frame.pack(padx=10, pady=10)
            self.image_label = ctk.CTkLabel(self.image_frame, image=self.header_image, text="")
            self.image_label.pack(padx=5, pady=5)
        else:
            self.image_label = ctk.CTkLabel(self.main_frame, text="Header Image", height=10)
            self.image_label.pack(fill="x", pady=10)

        # Label for the text input box
        self.text_input_label = ctk.CTkLabel(self.main_frame, 
                                            text="Enter Case Number", 
                                            font=ctk.CTkFont(size=28, weight="bold"))
        self.text_input_label.pack(padx=10, pady=10)

        # Create a frame to hold the search icon, text input and mic button
        self.input_frame = ctk.CTkFrame(self.main_frame, 
                                        width=780, 
                                        height=80,
                                        fg_color="transparent",
                                        border_width=2,
                                        border_color="black",
                                        corner_radius=40)
        self.input_frame.pack(padx=10, pady=20)
        
        # Load search image once
        self.search_icon = self.load_image("images/search_icons.png", (50, 50))
        self.search_label = ctk.CTkLabel(self.input_frame, image=self.search_icon, text="")  
        self.search_label.pack(side="left", padx=(30, 5), pady=5)  # Now it can be packed

        # Text input box
        self.text_input = ctk.CTkEntry(self.input_frame, 
                                    font=ctk.CTkFont(size=24, weight="bold"), 
                                    width=740, 
                                    height=60,
                                    fg_color="transparent", 
                                    placeholder_text="Search for your case details",
                                    border_width=0)
        self.text_input.pack(side="left", padx=10, pady=10)

        # Load microphone image once
        self.mic_image = self.load_image("images/mic2.png", (50, 50))
        self.mic_button = ctk.CTkButton(
            self.input_frame,
            command=self.listen_and_speak,
            fg_color="transparent",
            height=50,
            width=100,
            corner_radius=30,
            image=self.mic_image,
            text=""
        )
        self.mic_button.pack(side="right", padx=(10, 15), pady=10)

        # Bind the Entry widget to update table on text change
        self.text_input.bind('<KeyRelease>', self.on_text_change)

        # Create numeric keypad
        self.create_numeric_keypad()

        # Buttons for speaking in different languages
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(padx=10, pady=10)

        self.english_button = ctk.CTkButton(
            self.button_frame,
            text="Speak English",
            command=lambda: self.process_case_number(self.text_input.get(), "en"),
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#573AC0",
            text_color="white",
            height=80,
            width=276,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.english_button.pack(side="left", padx=30, pady=10)

        self.hindi_button = ctk.CTkButton(
            self.button_frame,
            text="हिंदी बोलें",
            command=lambda: self.process_case_number(self.translate_text(self.text_input.get(), source='en', target='hi'), "hi"),
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#573AC0",
            text_color="white",
            height=80,
            width=276,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.hindi_button.pack(side="left", padx=30, pady=10)

        self.punjabi_button = ctk.CTkButton(
            self.button_frame,
            text="ਹਿੰਦੀ ਬੋਲੋ",
            command=lambda: self.process_case_number(self.translate_text(self.text_input.get(), source='en', target='pa'), "pa"),
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#573AC0",
            text_color="white",
            height=80,
            width=276,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.punjabi_button.pack(side="left", padx=30, pady=10)
        
        ## =======================================================================
        # Create a frame to act as a solid border
        self.subtitle_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="white",
            width=940,
            height=260,
            border_width=2,
            border_color="white",
            corner_radius=10
        )
        self.subtitle_frame.pack(pady=20, padx=20)

        # Create a label inside the frame
        self.subtitle_label = ctk.CTkLabel(
            self.subtitle_frame,
            text="Case details",
            width=940,
            height=240,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="gray",
            fg_color="white",
            wraplength=530,
            padx=10,
            pady=10
        )
        self.subtitle_label.pack(padx=5, pady=5)

        # Add table for case details
        self.create_case_table()  # Ensure this is called after all necessary attributes are initialized

        # Initialize translators
        self._translators = {}
        
        # Buttons for speaking in different languages
        self.last_button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.last_button_frame.pack(padx=10, pady=10)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.last_button_frame,
            text="Close",
            command=self.show_password_popup,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="maroon",  # Red color for close button
            text_color="white",
            height=60,
            width=180,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.close_button.pack(side="left", padx=10, pady=10)

        # Map button to open map image
        self.map_button = ctk.CTkButton(
            self.last_button_frame,
            text="Map",
            command=self.open_map,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#573AC0",
            text_color="white",
            height=60,
            width=180,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.map_button.pack(side="left", padx=10, pady=10)

        # Add Reset and Close buttons
        self.reset_button = ctk.CTkButton(
            self.last_button_frame,
            text="Reset",
            command=self.reset_application,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="green",  # Red color for reset button
            text_color="white",
            height=60,
            width=180,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.reset_button.pack(side="left", padx=10, pady=10)
    # #########################################################################################################################

    def show_password_popup(self):
        """Show a password entry popup with a numeric keypad."""
        self.password_window = ctk.CTkToplevel(self.root)
        self.password_window.title("Password Verification")
        self.password_window.geometry("300x400")
        self.password_window.resizable(False, False)

        # Keep the pop-up on top and grab focus
        self.password_window.grab_set()  # Prevents clicking outside the window
        self.password_window.focus_force()  # Forces focus on the pop-up

        # Label
        ctk.CTkLabel(self.password_window, text="Enter Password:", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        # Password Entry Field (Read-Only)
        self.password_var = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(self.password_window, textvariable=self.password_var, font=ctk.CTkFont(size=18), justify="center", show="*")
        self.password_entry.pack(pady=5, padx=20, fill="x")

        # Numeric Keypad Frame
        keypad_frame = ctk.CTkFrame(self.password_window)
        keypad_frame.pack(pady=10)

        # Keypad Buttons
        buttons = [
            ('1', '2', '3'),
            ('4', '5', '6'),
            ('7', '8', '9'),
            ('⌫', '0', '✔')  # Backspace, 0, Enter
        ]

        for row_idx, row in enumerate(buttons):
            for col_idx, digit in enumerate(row):
                button = ctk.CTkButton(
                    keypad_frame,
                    text=digit,
                    font=ctk.CTkFont(size=20, weight="bold"),
                    width=60,
                    height=60,
                    fg_color="#573AC0",
                    border_width=2,
                    border_color="black",
                    corner_radius=10,
                    command=lambda d=digit: self.handle_keypress(d)
                )
                button.grid(row=row_idx, column=col_idx, padx=5, pady=5)

    def handle_keypress(self, key):
        """Handle keypresses for the numeric keypad."""
        if key == '⌫':  # Backspace
            self.password_var.set(self.password_var.get()[:-1])
        elif key == '✔':  # Enter
            self.verify_password()
        else:
            self.password_var.set(self.password_var.get() + key)

    def verify_password(self):
        """Verify the entered password and close the app if correct."""
        password = self.password_var.get()
        if password:
            for user in self.auth_data:
                if password in user.values():
                    self.root.destroy()  # Close the application
                    return
            messagebox.showerror("Error", "Incorrect password.")
        else:
            messagebox.showwarning("Warning", "Password cannot be empty.")



    def load_auth_data(self):
        """Load authentication data from auth.json."""
        try:
            with open("auth.json", "r", encoding="utf-8") as file:
                self.auth_data = json.load(file)
        except FileNotFoundError:
            print("Authentication file not found. Using default passwords.")
            self.auth_data = [
                {"superadmin": "69696969"},
                {"admin": "12345678"}
            ]

    def reset_application(self):
        """Reset the application by clearing the input and table."""
        self.text_input.delete(0, ctk.END)
        self.subtitle_label.configure(text="")
        self.update_table("")  # Clear the table

    def load_image(self, path, size):
        """Load and resize an image."""
        try:
            image = Image.open(path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=image, size=size)
        except Exception as e:
            print(f"Could not load image: {e}")
            return None

    def load_court_database(self):
        """Load the court database from a JSON file."""
        try:
            with open("case_database.json", "r", encoding="utf-8") as file:
                self.court_database = json.load(file)
        except FileNotFoundError:
            print("Court database file not found. Using a sample database.")

    # =====================================================================
    def create_numeric_keypad(self):
        """Create a numeric keypad with buttons for digits 0-9 and a backspace button."""
        # Create a frame for the numeric keypad
        self.keypad_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.keypad_frame.pack(padx=10, pady=10)

        # Define the layout of the buttons
        buttons = [
            ('1', '2', '3'),
            ('4', '5', '6'),
            ('7', '8', '9'),
            ('*', '0', '#')
        ]

        # Create and place the buttons in a grid
        for row_idx, row in enumerate(buttons):
            for col_idx, digit in enumerate(row):
                button = ctk.CTkButton(
                    self.keypad_frame,
                    text=digit,
                    font=ctk.CTkFont(size=28, weight="bold"),
                    width=140,
                    height=80,
                    fg_color="#573AC0",
                    border_width=2,
                    border_color="black",
                    corner_radius=40,
                    command=lambda d=digit: self.append_to_input(d)  # Append digit to input
                )
                button.grid(row=row_idx, column=col_idx, padx=20, pady=10)

        # Add Backspace and Enter buttons in the same row
        row_idx = len(buttons)  # Place them on the next row after the digits

        backspace_button = ctk.CTkButton(
            self.keypad_frame,
            text="⌫ Back",  # Unicode symbol for backspace
            font=ctk.CTkFont(size=28, weight="bold"),
            width=160,
            height=80,
            fg_color="Crimson",
            border_width=2,
            border_color="black",
            corner_radius=40,
            command=self.remove_last_character  # Remove the last character
        )
        backspace_button.grid(row=row_idx, column=0, padx=10, pady=10)  # Place in first column

        dash_button = ctk.CTkButton(
            self.keypad_frame,
            text="-",  # Unicode symbol for backspace
            font=ctk.CTkFont(size=28, weight="bold"),
            width=140,
            height=80,
            fg_color="#573AC0",
            border_width=2,
            border_color="black",
            corner_radius=40,
            command=lambda d='-': self.append_to_input(d)
        )
        dash_button.grid(row=row_idx, column=1, padx=10, pady=10)  # Place in first column

        enter_button = ctk.CTkButton(
            self.keypad_frame,
            text="↵ Enter ",  # Unicode symbol for Enter
            font=ctk.CTkFont(size=28, weight="bold"),
            width=160,
            height=80,
            fg_color="darkgreen",
            border_width=2,
            border_color="black",
            corner_radius=40,
            command=lambda: self.process_case_number(self.text_input.get(), "en")
        )
        enter_button.grid(row=row_idx, column=2, padx=10, pady=10)  # Place in third column

    def append_to_input(self, digit):
        """Append the clicked digit to the text input."""
        current_text = self.text_input.get()
        self.text_input.delete(0, ctk.END)
        self.text_input.insert(0, current_text + digit)

    def remove_last_character(self):
        """Remove the last character from the text input."""
        current_text = self.text_input.get()
        if current_text:  # Check if there is text to remove
            self.text_input.delete(0, ctk.END)
            self.text_input.insert(0, current_text[:-1])  # Remove the last character
    # ====================================================================
    
    def create_case_table(self):
        # Create frame for table with fixed size
        self.table_frame = ctk.CTkFrame(self.main_frame, width=940, height=120,
                                        border_width=2,
                                        border_color="black",
                                        corner_radius=10)  # Initialize table_frame
        self.table_frame.pack_propagate(False)  # Prevent resizing based on child widgets
        self.table_frame.pack(expand=True, padx=20, pady=20)

        ### Case Number
        # Create a StringVar to hold the case number
        self.case_number_var = ctk.StringVar(value="Case Number: ")  # Default text

        # Label for the text input box
        self.text_input_label = ctk.CTkLabel(
            self.table_frame,
            textvariable=self.case_number_var,  # Use variable instead of fixed text
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"  # Align text inside the label
        )

        # Align label to the left side of the frame properly
        self.text_input_label.pack(padx=10, pady=10)

        # Create table with Treeview
        columns = ("Case Number", "Case Title", "Court Number", "Judge Name")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=10)

        # Configure column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        # Style the table
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Helvetica', 16, 'bold'), foreground="black")
        style.configure("Treeview", font=('Helvetica', 14, 'bold'), foreground="blue", rowheight=25)

        # # Add scrollbar
        # scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        # self.tree.configure(yscrollcommand=scrollbar.set)

        # # Pack the table and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        # scrollbar.pack(side="right", fill="y")
        
    def on_text_change(self, event=None):
        """Update table when text input changes"""
        case_number = self.text_input.get()
        self.update_table(case_number)

    def update_table(self, search_case_number=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not search_case_number:
            return

        # Format the search number
        digits_only = ''.join(filter(str.isdigit, search_case_number))
        if not digits_only:
            return
        
        formatted_number = f"2025-{digits_only.zfill(3)}"
        
        self.case_number_var.set(f"Case Number: {formatted_number}")

        # Add only the matching case
        for case in self.court_database:
            if case['case_number'] == formatted_number:
                self.tree.insert("", "end", values=(
                    case['case_number'],
                    case['case'],
                    case['court_number'],
                    case['judge_name']
                ))
                break

    def process_case_number(self, case_number, lang="en"):
        case_details = self.find_case_details(case_number)
        if case_details:
            case_details = self.translate_text(case_details, source='en', target=lang)
            self.speak_text(case_details, lang)
        else:
            self.speak_text("Case not found.", lang)
        # Update the table when processing a case number
        self.update_table(case_number)

    def find_case_details(self, case_number):
        """Find case details based on the case number."""
        digits_only = ''.join(filter(str.isdigit, case_number))
        if not digits_only:
            return None
        
        formatted_number = f"2025-{digits_only.zfill(3)}"
        for case in self.court_database:
            if case['case_number'] == formatted_number:
                return f"Your case number is {case['case_number']}, titled '{case['case']}'. The hearing is scheduled in Court Number {case['court_number']}, presided over by Judge {case['judge_name']}."
        return None

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

    def speak_text(self, text, lang="en"):
        try:
            # Remove the existing file if it exists
            if os.path.exists("speech.mp3"):
                os.remove("speech.mp3")

            # Generate the speech file
            tts = gTTS(text=text, lang=lang)
            tts.save("speech.mp3")

            # Initialize pygame mixer
            pygame.mixer.init()
            pygame.mixer.music.load("speech.mp3")
            audio = pygame.mixer.Sound("speech.mp3")
            total_duration = audio.get_length()
            words = text.split()
            num_words = len(words)
            duration_per_word = total_duration / num_words

            # Play the audio
            pygame.mixer.music.play()

            # Print words in real-time and update the GUI
            self.subtitle_label.configure(text="")
            start_time = time.time()

            for word in words:
                self.subtitle_label.configure(text=self.subtitle_label.cget("text") + " " + word)
                self.root.update()

                # Calculate the elapsed time and sleep accordingly
                elapsed_time = time.time() - start_time
                expected_time = duration_per_word * (words.index(word) + 1)
                sleep_time = max(0, expected_time - elapsed_time)
                time.sleep(sleep_time)

            # Clear the subtitle after the audio finishes
            self.root.update()

            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Clean up
            pygame.mixer.quit()
        except Exception as e:
            print(f"Text-to-speech error: {e}")

    def listen_and_speak(self):
        self.speak_text("Kindly tell me your case number. ", lang='en')
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source)
                self.subtitle_label.configure(text="Listening for case number...")
                self.root.update()
                audio = recognizer.listen(source, timeout=5)

                recognized_text = recognizer.recognize_google(audio)
                self.text_input.delete(0, ctk.END)
                # Format the search number
                digits_only = ''.join(filter(str.isdigit, recognized_text))
                self.text_input.insert(0, digits_only)
                self.root.update()
                
                # Process the recognized case number
                self.process_case_number(recognized_text, "en")
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand audio")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Could not request results; {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            
    def open_map(self):
        """Open the map image corresponding to the case number."""
        case_number = self.text_input.get()
        if not case_number:
            messagebox.showwarning("Warning", "Please enter a case number.")
            return

        # Format the case number
        digits_only = ''.join(filter(str.isdigit, case_number))
        if not digits_only:
            messagebox.showwarning("Warning", "Invalid case number.")
            return
        
        formatted_number = f"2025-{digits_only.zfill(3)}"
        map_filename = f"images/map_{formatted_number}.jpg"

        if not os.path.exists(map_filename):
            messagebox.showerror("Error", f"Map file not found for case number: {formatted_number}")
            return

        # Open the map image in a new pop-up window
        map_window = ctk.CTkToplevel(self.root)
        map_window.title(f"Map for Case {formatted_number}")
        map_window.geometry("750x550")  # Set fixed size

        # Make the pop-up modal
        map_window.transient(self.root)  # Attach pop-up to main window
        map_window.grab_set()  # Prevent interaction with the main window
        map_window.focus_set()  # Set focus on the pop-up

        try:
            map_image = Image.open(map_filename)
            map_image = map_image.resize((720, 480), Image.Resampling.LANCZOS)
            map_ctk_image = ctk.CTkImage(light_image=map_image, size=(720, 480))

            # Image label
            map_label = ctk.CTkLabel(map_window, image=map_ctk_image, text="")
            map_label.image = map_ctk_image  # Keep reference to avoid garbage collection
            map_label.pack(pady=10)

            # Close button
            close_button = ctk.CTkButton(
                map_window,
                text="Close",
                font=ctk.CTkFont(size=20, weight="bold"),
                fg_color="red",
                text_color="white",
                height=60,
                width=120,
                border_width=2,
                border_color="black",
                corner_radius=20,
                command=map_window.destroy  # Close the window
            )
            close_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load map image: {e}")

        # Wait for pop-up to close before continuing
        self.root.wait_window(map_window)


if __name__ == "__main__":
    root = ctk.CTk()
    tts = HighCourt(root)
    root.mainloop()


