import tkinter as tk
import asyncio
from gtts import gTTS
import os
import cv2
from PIL import Image, ImageTk
import json
import subprocess
import psutil
from mutagen.mp3 import MP3
from deep_translator import GoogleTranslator
import speech_recognition as sr
import winsound
import time

# ===================================================================================================================
class Conversation:
    def __init__(self):
        self.translator = GoogleTranslator()
        self.recognizer = sr.Recognizer()
        
        self.start_sound = "C:\\Windows\\Media\\chimes.wav"
        self.end_sound = "C:\\Windows\\Media\\notify.wav"

    def get_audio_length(self, file_path="speech.mp3"):
        try:
            audio = MP3(file_path)
            return audio.info.length
        except Exception as e:
            print(f"Error in get_audio_length: {e}")
            return 0

    async def speak_text(self, text, lang="en"):
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save("speech.mp3")
            subprocess.run(["start", "speech.mp3"], shell=True)
            time_to_wait = self.get_audio_length("speech.mp3")
            await asyncio.sleep(time_to_wait)
            os.remove("speech.mp3")
        except Exception as e:
            print(f"Error in speak_text: {e}")

    def translate_text(self, text, source, target):
        try:
            return GoogleTranslator(source=source, target=target).translate(text)
        except Exception as e:
            return f"Error in translation: {e}"

    async def recognize_speech(self, language="en-US", timeout=10):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                winsound.PlaySound(self.start_sound, winsound.SND_FILENAME)
                
                speech_future = asyncio.Future()
                def recognize_callback():
                    try:
                        audio = self.recognizer.listen(source, timeout=timeout)
                        text = self.recognizer.recognize_google(audio, language=language)
                        speech_future.set_result(text)
                    except Exception as e:
                        speech_future.set_exception(e)
                
                loop = asyncio.get_event_loop()
                loop.run_in_executor(None, recognize_callback)
                
                try:
                    text = await asyncio.wait_for(speech_future, timeout=timeout)
                    print(f"Recognized: {text}")
                    return text
                except asyncio.TimeoutError:
                    await self.speak_text("No input detected.", lang="en")
                    return None
        except Exception as e:
            print(f"Error in recognize_speech: {e}")
            return None

#==========================================================================================================
class CourtApplication:
    def __init__(self, root):
        self.root = root
        self.cap = None
        with open('case_db.json', 'r') as f: 
            self.case_db = json.load(f)
        self.conversation = Conversation()
        self.case_number_entry = None
        self.text_area = None
        self.video_label = None

        # Bind the Escape key to toggle full screen
        self.root.bind("<Escape>", self.toggle_full_screen)
        self.is_full_screen = False  # Start in windowed mode

    def toggle_full_screen(self, event=None):
        """Toggle between full screen and windowed mode."""
        if self.is_full_screen:
            self.root.attributes('-fullscreen', False)
            self.root.state('normal')  # Restore window to normal state
        else:
            self.root.attributes('-fullscreen', True)  # Make window full screen
        self.is_full_screen = not self.is_full_screen  # Flip the full screen state

    def center_window(self, width, height):
        """Centers the window on the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the position of the window to center it
        position_top = int(screen_height / 2 - height / 2)
        position_left = int(screen_width / 2 - width / 2)

        # Set the position of the window
        self.root.geometry(f'{width}x{height}+{position_left}+{position_top}')

    def get_case_description(self, case_number):
        return next((case['case'] for case in self.case_db if case['case number'] == case_number), None)

    def update_text_area(self, message):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, message)

    def cleanup_resources(self):
        # Close camera
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

        # Kill any hanging mp3 processes
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'speech.mp3':
                proc.terminate()

        # Remove temporary files
        if os.path.exists('speech.mp3'):
            os.remove('speech.mp3')

        # Ensure Tkinter window is closed
        self.root.quit()
        self.root.destroy()

    async def on_button_click(self, language):
        case_number = self.case_number_entry.get()
        if not case_number.isdigit():
            self.update_text_area("Please enter a valid case number.\n")
            return
        
        case_description = self.get_case_description(case_number)
        if case_description:
            message = f"Case number {case_number}: {case_description}"
            # First update GUI with translated message
            translated_message = self.conversation.translate_text(message, 'en', {'hindi': 'hi', 'punjabi': 'pa'}.get(language, 'en'))
            self.update_text_area(translated_message)
            await self.conversation.speak_text(translated_message, {'hindi': 'hi', 'punjabi': 'pa'}.get(language, 'en'))
        else:
            self.update_text_area(f"No case found for case number {case_number}.\n")
            await self.conversation.speak_text(f"No case found for case number {case_number}.", 'pa')

    async def listen_for_case_number(self):
        start_time = time.time()
        
        while True:
            case_number = await self.conversation.recognize_speech(language="en-US", timeout=10)
            if case_number:
                if case_number.isdigit():
                    self.case_number_entry.delete(0, tk.END)
                    self.case_number_entry.insert(tk.END, case_number)
                    await self.on_button_click('punjabi')
                    break
                else:
                    self.update_text_area("Invalid input. Please try again.\n")
                    await self.conversation.speak_text("Please say a valid case number.", lang="en")
            
            # Check for timeout
            if time.time() - start_time > 30:
                self.update_text_area("No input detected. Restarting application.\n")
                await self.conversation.speak_text("No input detected. Restarting application.", lang="en")
                self.cleanup_resources()
                break

    async def detect_face_and_ask_case_number(self):
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.cap = cv2.VideoCapture(0)
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                roi = gray[int(frame.shape[0] * 0.25):int(frame.shape[0] * 0.75), 
                           int(frame.shape[1] * 0.25):int(frame.shape[1] * 0.75)]
                faces = face_cascade.detectMultiScale(roi, scaleFactor=1.1, minNeighbors=5, 
                                                      minSize=(150, 150), maxSize=(300, 300))
                
                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, 
                                      (x + int(frame.shape[1] * 0.25), y + int(frame.shape[0] * 0.25)),
                                      (x + w + int(frame.shape[1] * 0.25), y + h + int(frame.shape[0] * 0.25)), 
                                      (0, 255, 0), 2)
                    
                    # First update GUI
                    self.update_text_area("Face detected! Please say your case number.")
                    
                    # Then speak
                    await self.conversation.speak_text(
                        self.conversation.translate_text("Face detected! Please say your case number.", 'en', 'pa'), 
                        'pa'
                    )
                    await self.listen_for_case_number()
                    break
                
                # Update video display
                self.video_label.img_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.video_label.config(image=self.video_label.img_tk)
                self.root.update()
            
        except Exception as e:
            print(f"Face detection error: {e}")
            self.cleanup_resources()
        
    
    def create_gui(self):
        self.root.title("Case Search Application")

        # Create an outer frame with silver solid border
        outer_frame = tk.Frame(self.root, bd=5, relief="solid", bg="brown", highlightbackground="silver", highlightthickness=2)
        outer_frame.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)  # Fill the window and add padding

        # Center the window
        self.center_window(800, 600)  # You can adjust the width and height here

        # Set background color to light sky blue (RGB equivalent of #87CEEB)
        outer_frame.configure(bg="#87CEEB")

        # Load and display the image (phone court.jpg) above the "Enter case number" field
        try:
            phone_court_image = Image.open("images/court01.jpg")
            phone_court_image = phone_court_image.resize((480, 240), Image.Resampling.LANCZOS)
            phone_court_img_tk = ImageTk.PhotoImage(phone_court_image)

            # Create a label to display the image
            img_label = tk.Label(outer_frame, image=phone_court_img_tk, bg="#87CEEB")
            img_label.image = phone_court_img_tk  # Keep reference to avoid garbage collection
            img_label.grid(row=0, column=0, columnspan=3, pady=10)  # Positioning with grid

        except Exception as e:
            print(f"Error loading image: {e}")

        # Header Label
        header_label = tk.Label(outer_frame, text="Case Search", font=("Arial", 18, "bold"), pady=10, bg="#87CEEB")
        header_label.grid(row=1, column=0, columnspan=3)

        # Instructions Label
        instructions_label = tk.Label(outer_frame, text="Please say your case number after face detection.", font=("Arial", 12, "bold"), wraplength=400, bg="#87CEEB")
        instructions_label.grid(row=2, column=0, columnspan=3, pady=5)

        # Case Number Entry with rounded corners and yellow border
        self.case_number_entry = tk.Entry(outer_frame, width=40, font=("Arial", 14, "bold"), bd=2, relief="solid", highlightthickness=2, highlightbackground="yellow", highlightcolor="yellow")
        self.case_number_entry.grid(row=3, column=0, columnspan=3, pady=10)

        # Language selection buttons (using grid for better alignment)
        button_frame = tk.Frame(outer_frame, bg="#87CEEB")
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)

        # Custom Style for Rounded Buttons with yellow border
        def create_rounded_button(text, language):
            button = tk.Button(button_frame, text=text, font=("Arial", 12, "bold"), bg="blue", fg="white", activebackground="lightgreen", 
                            command=lambda lang=language: asyncio.run(self.on_button_click(lang)),
                            relief="flat", padx=10, pady=10)
            # Customizing to make the button's corners rounded with yellow border
            button.config(borderwidth=2, highlightbackground="darkblue", highlightthickness=2, highlightcolor="lightblue")
            button.grid(row=0, column=languages.index((language, text)), padx=15, pady=5)

        languages = [('hindi', 'Hindi'), ('english', 'English'), ('punjabi', 'Punjabi')]
        for language, text in languages:
            create_rounded_button(text, language)

        # Text Area with rounded corners and yellow border
        self.text_area = tk.Text(outer_frame, width=50, height=8, wrap=tk.WORD, font=("Arial", 12), bd=2, relief="solid", highlightthickness=2, highlightbackground="yellow", highlightcolor="yellow")
        self.text_area.grid(row=5, column=0, columnspan=3, pady=10)

        # Video Label for displaying the camera feed
        self.video_label = tk.Label(outer_frame)
        self.video_label.grid(row=6, column=0, columnspan=3, pady=10)

        # Close Button with rounded corners and yellow border
        close_button = tk.Button(outer_frame, text="Close", font=("Arial", 12, "bold"), command=self.cleanup_resources, bg="red", fg="white", relief="flat", padx=20, pady=10)
        close_button.config(borderwidth=2, highlightbackground="green", highlightthickness=2, highlightcolor="yellow")
        close_button.grid(row=7, column=0, columnspan=3, padx=15, pady=10)

        # Add a loading spinner label (Initially hidden)
        self.loading_label = tk.Label(outer_frame, text="Processing... Please wait.", font=("Arial", 12), fg="red", bg="#87CEEB")
        self.loading_label.grid(row=8, column=0, columnspan=3, pady=10)
        self.loading_label.grid_forget()  # Hide it initially

        # Run the face detection method to start the process
        asyncio.get_event_loop().run_until_complete(self.detect_face_and_ask_case_number())


def main():
    while True:
        try:
            root = tk.Tk()
            app = CourtApplication(root)
            app.create_gui()
            root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")
            break

if __name__ == "__main__":
    main()



