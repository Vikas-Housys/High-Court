import customtkinter as ctk
import speech_recognition as sr
from tkinter import StringVar

class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multilingual Speech Recognition")
        self.root.geometry("500x400")

        # Initialize variables
        self.language_var = StringVar(value="en-US")  # Default language
        
        # Main frame
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(self.main_frame, text="Speech Recognition App", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self.main_frame, text="Select language and click 'Listen'", font=("Arial", 16))
        self.status_label.pack(pady=10)

        # Language selection
        self.lang_frame = ctk.CTkFrame(self.main_frame)
        self.lang_frame.pack(pady=10)
        
        self.lang_label = ctk.CTkLabel(self.lang_frame, text="Language:")
        self.lang_label.pack(side="left", padx=5)
        
        # Radio buttons for language selection
        self.english_radio = ctk.CTkRadioButton(self.lang_frame, text="English", variable=self.language_var, value="en-US")
        self.english_radio.pack(side="left", padx=10)
        
        self.punjabi_radio = ctk.CTkRadioButton(self.lang_frame, text="Punjabi", variable=self.language_var, value="pa-IN")
        self.punjabi_radio.pack(side="left", padx=10)

        # Listen button
        self.listen_button = ctk.CTkButton(self.main_frame, text="Listen", command=self.test_listen, 
                                           height=40, width=120, 
                                           fg_color="#3B8ED0", hover_color="#36719F")
        self.listen_button.pack(pady=20)

        # Result display
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.pack(fill="both", expand=True, pady=10)
        
        self.result_label = ctk.CTkLabel(self.result_frame, text="Recognition results will appear here", 
                                        font=("Arial", 14), 
                                        wraplength=400)
        self.result_label.pack(pady=20, padx=10, fill="both", expand=True)

    def listen(self):
        """Listen for user input and return the recognized text."""
        recognizer = sr.Recognizer()
        language = self.language_var.get()
        
        with sr.Microphone() as source:
            try:
                self.status_label.configure(text=f"Adjusting for background noise...")
                self.root.update()
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.status_label.configure(text=f"Listening... (Language: {language})")
                self.root.update()

                # Longer timeout and phrase_time_limit for better digit recognition
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                self.status_label.configure(text="Processing speech...")
                self.root.update()
                
                # Additional parameters to improve recognition accuracy
                recognized_text = recognizer.recognize_google(
                    audio, 
                    language=language,
                    show_all=False  # Set to True for debugging
                )

                return recognized_text

            except sr.UnknownValueError:
                self.status_label.configure(text="Could not understand audio.")
            except sr.RequestError as e:
                self.status_label.configure(text=f"Request error: {e}")
            except Exception as e:
                self.status_label.configure(text=f"Error: {e}")

        return ""

    def test_listen(self):
        """Tests the listen method and displays the result."""
        self.result_label.configure(text="Listening...")
        self.root.update()

        recognized_text = self.listen()
        
        if recognized_text:
            language_name = "English" if self.language_var.get() == "en-US" else "Punjabi"
            self.result_label.configure(text=f"Recognized ({language_name}):\n{recognized_text}")
            self.status_label.configure(text="Recognition complete!")
        else:
            self.result_label.configure(text="No speech recognized.")
            self.status_label.configure(text="Try again")

# Run the application
if __name__ == "__main__":
    ctk.set_appearance_mode("system")  # Use system theme
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = VoiceAssistantApp(root)
    root.mainloop()

