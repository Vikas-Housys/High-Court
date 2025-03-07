import customtkinter as ctk
import speech_recognition as sr

class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Recognition Test")
        self.root.geometry("400x300")

        # CustomTkinter UI Elements
        self.label = ctk.CTkLabel(root, text="Click 'Listen' to speak", font=("Arial", 16))
        self.label.pack(pady=20)

        self.listen_button = ctk.CTkButton(root, text="Listen", command=self.test_listen)
        self.listen_button.pack(pady=10)

        self.result_label = ctk.CTkLabel(root, text="", font=("Arial", 14), fg_color="lightgray")
        self.result_label.pack(pady=20, padx=10, fill="both")

    def listen(self, lang="en"):
        """Listen for user input and return the recognized text."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source)
                self.label.configure(text="Listening...")
                self.root.update()

                audio = recognizer.listen(source, timeout=5)
                recognized_text = recognizer.recognize_google(audio, language=lang)

                return recognized_text

            except sr.UnknownValueError:
                self.label.configure(text="Could not understand audio.")
            except sr.RequestError as e:
                self.label.configure(text=f"Request error: {e}")
            except Exception as e:
                self.label.configure(text=f"Error: {e}")

        return ""

    def test_listen(self):
        """Tests the listen method and displays the result."""
        self.result_label.configure(text="Listening...")
        self.root.update()

        recognized_text = self.listen(lang="en")
        
        if recognized_text:
            self.result_label.configure(text=f"Recognized: {recognized_text}")
        else:
            self.result_label.configure(text="No speech recognized.")

# Run the application
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    app = VoiceAssistantApp(root)
    root.mainloop()
