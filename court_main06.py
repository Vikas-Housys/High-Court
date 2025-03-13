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
import cv2
import threading
import requests
import re
from difflib import get_close_matches
import winsound

class HighCourt:
    # =========================================== Constructore ==========================================
    def __init__(self, root):
        self.start_sound = "C:\\Windows\\Media\\chimes.wav"
        self.end_sound = "C:\\Windows\\Media\\notify.wav"

        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.title("Court Case Information System")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        pygame.mixer.init()
        self.load_auth_data()

        self.camera_pause=False

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

        # Face detection variables
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = None
        self.is_running = False
        self.detection_thread = None
        self.face_detected = False
        self.face_detection_cooldown = False
        
        # Create frame for camera feed
        self.image_frame = ctk.CTkFrame(
            self.main_frame,
            width=950,
            height=430,
            fg_color="transparent",
            border_width=3,
            border_color="black",
            corner_radius=10,
        )
        self.image_frame.pack(padx=10, pady=10)
        
        # Create label for camera feed
        self.image_label = ctk.CTkLabel(self.image_frame, text="", width=940, height=420)
        self.image_label.pack(padx=5, pady=5)
        
        self.start_camera()

        # Label for the text input box
        self.text_input_label = ctk.CTkLabel(self.main_frame, 
                                            text="Search", 
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
        self.search_label.pack(side="left", padx=(30, 5), pady=5)

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
            command=self.conversation,
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
            command=lambda: self.process_case_details(self.text_input.get(), "en"),
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#573AC0",
            text_color="white",
            height=75,
            width=275,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.english_button.pack(side="left", padx=30, pady=10)

        self.hindi_button = ctk.CTkButton(
            self.button_frame,
            text="हिंदी बोलें",
            command=lambda: self.process_case_details(self.translate_text(self.text_input.get(), source='en', target='hi'), "hi"),
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#573AC0",
            text_color="white",
            height=75,
            width=275,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.hindi_button.pack(side="left", padx=30, pady=10)

        self.punjabi_button = ctk.CTkButton(
            self.button_frame,
            text="ਹਿੰਦੀ ਬੋਲੋ",
            command=lambda: self.process_case_details(self.translate_text(self.text_input.get(), source='en', target='pa'), "pa"),
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#573AC0",
            text_color="white",
            height=75,
            width=275,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.punjabi_button.pack(side="left", padx=30, pady=10)
        
        # Create a frame to act as a solid border
        self.subtitle_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="white",
            width=940,
            height=280,
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
            height=280,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="gray",
            fg_color="white",
            wraplength=530,
            padx=10,
            pady=10
        )
        self.subtitle_label.pack(padx=5, pady=5)

        # Add table for case details
        self.create_case_table()

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
            fg_color="maroon", 
            text_color="white",
            height=60,
            width=180,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.close_button.pack(side="left", padx=10, pady=10)
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            self.last_button_frame,
            text="Reset",
            command=self.reset_application,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="green",
            text_color="white",
            height=60,
            width=180,
            border_width=2,
            border_color="black",
            corner_radius=40
        )
        self.reset_button.pack(side="left", padx=10, pady=10)
        
        # Register cleanup function to release camera resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
    
    # ===================================================================================================

    # ========================================= face detection ==========================================
    def start_camera(self):
        """Start the camera and face detection thread"""
        self.cap = cv2.VideoCapture(0)  # 0 is usually the built-in webcam
        self.is_running = True
        
        # Start detection in a separate thread
        self.detection_thread = threading.Thread(target=self.detect_faces)
        self.detection_thread.daemon = True
        self.detection_thread.start()
    
    def detect_faces(self):
        """Thread function for face detection with minimum and maximum range control"""
        last_detection_time = 0
        cooldown_period = 10  # 10 seconds cooldown
        min_face_size = (160, 160) 
        max_face_size = (240, 240)
        
        while self.is_running:
            if self.camera_pause:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue
                
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with min/max size constraints
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=min_face_size,
                maxSize=max_face_size
            )
            
            # Convert frame to PIL format for displaying
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Draw detection zone (center 60% of the frame)
            height, width = frame.shape[:2]
            x_start = int(width * 0.3)
            x_end = int(width * 0.7)
            y_start = int(height * 0.2)
            y_end = int(height * 0.8)
            
            # Draw detection zone rectangle
            cv2.rectangle(frame_rgb, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
            
            # Add text indicators for range
            cv2.putText(frame_rgb, "Detection Range", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame_rgb, "Min: " + str(min_face_size[0]) + "px", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
            cv2.putText(frame_rgb, "Max: " + str(max_face_size[0]) + "px", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
            
            face_in_zone = False
            
            # Draw rectangle around the faces with distance indication
            for (x, y, w, h) in faces:
                face_size = max(w, h)
                # Calculate approximate distance indicator (inversely proportional to face size)
                # This is a rough estimate - actual distance would require camera calibration
                distance_factor = min_face_size[0] / face_size if face_size > 0 else 1
                distance_indicator = f"Size: {face_size}px"
                
                # Determine if face is in optimal range
                in_range = min_face_size[0] <= face_size <= max_face_size[0]
                
                # Check if face is in detection zone
                face_center_x = x + w // 2
                face_center_y = y + h // 2
                
                if (x_start < face_center_x < x_end and 
                    y_start < face_center_y < y_end and in_range):
                    # Face is in detection zone and optimal range - draw blue rectangle
                    cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (255, 0, 0), 3)
                    cv2.putText(frame_rgb, "DETECTED", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    cv2.putText(frame_rgb, distance_indicator, (x, y+h+20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    face_in_zone = True
                elif (x_start < face_center_x < x_end and y_start < face_center_y < y_end):
                    # Face is in zone but not in optimal range - draw yellow rectangle
                    cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    
                    # Add text indicating why it's not detected
                    if face_size < min_face_size[0]:
                        range_text = "TOO FAR"
                    elif face_size > max_face_size[0]:
                        range_text = "TOO CLOSE"
                        
                    cv2.putText(frame_rgb, range_text, (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    cv2.putText(frame_rgb, distance_indicator, (x, y+h+20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                else:
                    # Face is outside detection zone - draw green rectangle
                    cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame_rgb, "OUT OF ZONE", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Check if we should trigger case number
            current_time = time.time()
            if face_in_zone and not self.face_detection_cooldown and (current_time - last_detection_time > cooldown_period):
                self.face_detected = True
                last_detection_time = current_time
                self.face_detection_cooldown = True
                
                self.root.after(0, self.prompt_for_case_number)
            
            # Convert the image to PIL format for CTkLabel
            pil_img = Image.fromarray(frame_rgb)
            ctk_img = ctk.CTkImage(light_image=pil_img, size=(940, 420))
            
            # Update the label with the new image (in the main thread)
            self.root.after(0, lambda: self.image_label.configure(image=ctk_img))
            
            # Small delay to reduce CPU usage
            time.sleep(0.03)  # ~30 FPS
            

    def prompt_for_case_number(self):
        """Prompt the user for case number after face detection"""
        if not self.face_detected:
            return
            
        self.face_detected = False
        self.conversation(lang='pa')
        
        # Reset cooldown after some time
        def reset_cooldown():
            self.face_detection_cooldown = False
            
        # Schedule cooldown reset after 10 seconds
        self.root.after(10000, reset_cooldown)
    
    # ===================================================================================================

    # ========================================= authentication ==========================================
    def on_closing(self):
        """Release resources and close application"""
        self.is_running = False
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1.0)
        if self.cap is not None:
            self.cap.release()
        if pygame.mixer.get_init() is not None:
            pygame.mixer.quit()
        self.root.destroy()

    def show_password_popup(self):
        """Show a password entry popup with a numeric keypad."""
        self.password_window = ctk.CTkToplevel(self.root)
        self.password_window.title("Password Verification")
        self.password_window.geometry("360x480")  # Increased height to accommodate new buttons
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

        # Keypad Buttons for password pop up
        buttons = [
            ('1', '2', '3'),
            ('4', '5', '6'),
            ('7', '8', '9'),
            ('⌫', '0', '✔')
        ]

        for row_idx, row in enumerate(buttons):
            for col_idx, digit in enumerate(row):
                button = ctk.CTkButton(
                    keypad_frame,
                    text=digit,
                    font=ctk.CTkFont(size=24, weight="bold"),
                    width=80,
                    height=60,
                    fg_color="teal",
                    border_width=2,
                    border_color="black",
                    corner_radius=10,
                    command=lambda d=digit: self.handle_keypress(d)
                )
                button.grid(row=row_idx, column=col_idx, padx=5, pady=5)
        
        # Additional buttons frame
        additional_buttons_frame = ctk.CTkFrame(self.password_window)
        additional_buttons_frame.pack(pady=10)
        
        # Reset Button
        reset_button = ctk.CTkButton(
            additional_buttons_frame,
            text="Reset",
            font=ctk.CTkFont(size=24, weight="bold"),
            width=120,
            height=60,
            fg_color="green",
            border_width=2,
            border_color="white",
            corner_radius=10,
            command=self.reset_password
        )
        reset_button.grid(row=0, column=0, padx=10, pady=5)
        
        # Close Button
        close_button = ctk.CTkButton(
            additional_buttons_frame,
            text="Close",
            font=ctk.CTkFont(size=24, weight="bold"),
            width=120,
            height=60,
            fg_color="maroon",
            border_width=2,
            border_color="white",
            corner_radius=10,
            command=self.close_password_window
        )
        close_button.grid(row=0, column=1, padx=10, pady=5)

    def reset_password(self):
        """Reset the password field."""
        self.password_var.set("")

    def close_password_window(self):
        """Close the password window."""
        self.password_window.destroy()

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
                    self.on_closing()  # Use on_closing to properly release camera resources
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
                {"admin": "244466666"}
            ]

    def reset_application(self):
        """Stop all running and pending operations, and restart the application as fresh."""
        # Stop any ongoing audio playback
        if pygame.mixer.get_init() is not None:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        
        # Clear the subtitle label and text input
        self.subtitle_label.configure(text="")
        self.text_input.delete(0, ctk.END)
        self.update_table("")

    def load_image(self, path, size):
        """Load and resize an image."""
        try:
            image = Image.open(path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=image, size=size)
        except Exception as e:
            print(f"Could not load image: {e}")
            return None
        
    # ===================================================================================================
    
    # ========================================== main keyboard ==========================================
    def create_numeric_keypad(self):
        """Create a full keyboard with alphanumeric keys."""
        # Create a frame for the keyboard
        self.keypad_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.keypad_frame.pack(padx=10, pady=10)

        # Define the layout of the buttons in QWERTY format
        buttons = [
            ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'),
            ('Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'),
            ('A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':'),
            ('Z', 'X', 'C', 'V', 'B', 'N', 'M', '/', '-', ';'),
            ('*', '(', ')', '{', '}', '(', ')', ',', '.',  '#'),
            ('+', '-', '|', '$', '%', '^', '_', '`', '~', '?')
        ]

        # Create and place the buttons in a grid
        for row_idx, row in enumerate(buttons):
            for col_idx, key in enumerate(row):
                button = ctk.CTkButton(
                    self.keypad_frame,
                    text=key,
                    font=ctk.CTkFont(size=28, weight="bold"),
                    width=80,
                    height=60,
                    fg_color="black",
                    border_width=2,
                    border_color="red",
                    corner_radius=40,
                    command=lambda k=key: self.append_to_input(k)
                )
                button.grid(row=row_idx, column=col_idx, padx=5, pady=5)

        # Add function buttons in the bottom row
        row_idx = len(buttons)  # Place them on the next row after the keyboard

        # Hash button
        hash_button = ctk.CTkButton(
            self.keypad_frame,
            text="@",
            font=ctk.CTkFont(size=28, weight="bold"),
            width=80,
            height=60,
            fg_color="black",
            border_width=2,
            border_color="red",
            corner_radius=40,
            command=lambda: self.append_to_input('@')
        )
        hash_button.grid(row=row_idx, column=0, padx=5, pady=10)

        # Backspace button
        backspace_button = ctk.CTkButton(
            self.keypad_frame,
            text="⌫ Back",
            font=ctk.CTkFont(size=24, weight="bold"),
            width=180,
            height=60,
            fg_color="black",
            border_width=2,
            border_color="red",
            corner_radius=40,
            command=self.remove_last_character
        )
        backspace_button.grid(row=row_idx, column=1, columnspan=2, padx=5, pady=10)

        # Space button
        space_button = ctk.CTkButton(
            self.keypad_frame,
            text="Space",
            font=ctk.CTkFont(size=24, weight="bold"),
            width=180,
            height=60,
            fg_color="black",
            border_width=2,
            border_color="red",
            corner_radius=40,
            command=lambda: self.append_to_input(' ')
        )
        space_button.grid(row=row_idx, column=3, columnspan=2, padx=5, pady=10)

        # Enter button
        enter_button = ctk.CTkButton(
            self.keypad_frame,
            text="↵ Enter",
            font=ctk.CTkFont(size=24, weight="bold"),
            width=180,
            height=60,
            fg_color="black",
            border_width=2,
            border_color="red",
            corner_radius=40,
            command=lambda: self.process_case_details(self.text_input.get(), "en")
        )
        enter_button.grid(row=row_idx, column=5, columnspan=2, padx=5, pady=10)

        # Clear button
        clear_button = ctk.CTkButton(
            self.keypad_frame,
            text="Clear",
            font=ctk.CTkFont(size=24, weight="bold"),
            width=180,
            height=60,
            fg_color="black",
            border_width=2,
            border_color="red",
            corner_radius=40,
            command=self.clear_input
        )
        clear_button.grid(row=row_idx, column=7, columnspan=2, padx=5, pady=10)
    
        # Star button
        star_button = ctk.CTkButton(
            self.keypad_frame,
            text="&",
            font=ctk.CTkFont(size=28, weight="bold"),
            width=80,
            height=60,
            fg_color="black",
            border_width=2,
            border_color="red",
            corner_radius=40,
            command=lambda: self.append_to_input('&')
        )
        star_button.grid(row=row_idx, column=9, padx=5, pady=10)

    def append_to_input(self, character):
        """Append the clicked character to the text input."""
        current_text = self.text_input.get()
        self.text_input.delete(0, ctk.END)
        self.text_input.insert(0, current_text + character)

    def remove_last_character(self):
        """Remove the last character from the text input."""
        current_text = self.text_input.get()
        if current_text:  # Check if there is text to remove
            self.text_input.delete(0, ctk.END)
            self.text_input.insert(0, current_text[:-1])  # Remove the last character

    def clear_input(self):
        """Clear the entire text input."""
        self.text_input.delete(0, ctk.END)
    
    # ===================================================================================================
    
    # ======================================== case table ===============================================
    def create_case_table(self):
        # Create frame for table with fixed size
        self.table_frame = ctk.CTkFrame(self.main_frame, width=940, height=120,
                                        border_width=2,
                                        border_color="black",
                                        corner_radius=10)  # Initialize table_frame
        self.table_frame.pack_propagate(False)  # Prevent resizing based on child widgets
        self.table_frame.pack(expand=True, padx=10, pady=20)

        ### Case Number
        # Create a StringVar to hold the case number
        self.case_id_var = ctk.StringVar(value="Case Id: ")  # Default text

        # Label for the text input box
        self.text_input_label = ctk.CTkLabel(
            self.table_frame,
            textvariable=self.case_id_var,  # Use variable instead of fixed text
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"  # Align text inside the label to the left
        )

        # Align label to the left side of the frame properly
        self.text_input_label.pack(padx=5, pady=5)

        # Create table with Treeview
        columns = ("Case ID", "Petitioner Name", "Respondent Name", "Advocate Name", "Status", "Next Date")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=10)

        # Configure column headings to be centered
        for col in columns:
            self.tree.heading(col, text=col, anchor="center")  # Center-align header text
            self.tree.column(col, width=150, anchor="center")  # Center-align cell text

        # Style the table
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Helvetica', 12, 'bold'), foreground="black", anchor="center")
        style.configure("Treeview", font=('Helvetica', 12, 'bold'), foreground="blue", rowheight=25, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
    
    def on_text_change(self, event=None):
        """Update table when text input changes"""
        case_id = self.text_input.get()
        self.update_table(case_id)

    def update_table(self, case_details=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if isinstance(case_details, dict):
            self.case_id_var.set(f"Case Number: {case_details['case_id']}")
            self.tree.insert("", "end", values=(
                case_details['case_id'],
                case_details['petitioner_name'],
                case_details['respondent_name'],
                case_details['advocate_name'],
                case_details['status'],
                case_details['next_date']
            ))
        elif isinstance(case_details, str):
            self.case_id_var.set(f"Case Number: {case_details}")
        else:
            self.case_id_var.set("Case Number: Not Found")

    def process_case_details(self, case_id, lang="en"):
        self.camera_pause=True
        
        BASE_URL = "http://192.168.1.12:8000/cases"

        # Check if the case details are already cached
        if hasattr(self, 'case_cache') and case_id in self.case_cache:
            case_details = self.case_cache[case_id]
        else:
            def get_case_details(case_id):
                try:
                    response = requests.get(f"{BASE_URL}/{case_id}")
                    if response.status_code == 200:
                        return response.json()
                    else:
                        return None
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching case details: {e}")
                    return None

            case_details = get_case_details(case_id)
            if case_details:
                # Cache the case details
                if not hasattr(self, 'case_cache'):
                    self.case_cache = {}
                self.case_cache[case_id] = case_details

        if case_details:
            case_details_sentence = f"""
            Your case details are as follows: Case Type - {case_details['case_type']}, Case Number - {case_details['case_no']}, and Filing Year - {case_details['case_year']}. 
            The petitioner in this case is {case_details['petitioner_name']}, while the respondent is {case_details['respondent_name']}. 
            The case is being represented by Advocate {case_details['advocate_name']}. Currently, the case status is {case_details['status']}. 
            The next hearing is scheduled for {case_details['next_date']}. Thank you.
            """
            case_details_sentence = self.translate_text(case_details_sentence, source='en', target=lang)
            self.speak_text(case_details_sentence, lang)
        else:
            self.speak_text("Case not found.", lang)

        self.update_table(case_details)

        self.camera_pause = False
        
    # ===================================================================================================

    #  ================================ language Speak and Translate ====================================
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
        """
        Convert text to speech and play it using gTTS and pygame.
        This method has been optimized to reduce resource usage and improve performance.
        """
        try:
            # Remove the existing file if it exists
            if os.path.exists("speech.mp3"):
                os.remove("speech.mp3")

            # Generate the speech file using gTTS
            tts = gTTS(text=text, lang=lang)
            tts.save("speech.mp3")

            # Initialize pygame mixer if not already initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Load the speech file into pygame mixer
            pygame.mixer.music.load("speech.mp3")

            # Play the audio
            pygame.mixer.music.play()

            # Calculate the total duration of the audio
            audio = pygame.mixer.Sound("speech.mp3")
            total_duration = audio.get_length()

            # Split the text into words for real-time display
            words = text.split()
            num_words = len(words)
            duration_per_word = total_duration / max(num_words, 1)  # Avoid division by zero

            # Clear the subtitle label before starting
            if self.root and self.subtitle_label.winfo_exists():
                self.subtitle_label.configure(text="")
                self.root.update()

            # Start time for tracking word display
            start_time = time.time()

            # Display words in real-time as the audio plays
            for word in words:
                if self.root and self.subtitle_label.winfo_exists():
                    # Append the current word to the subtitle label
                    current_text = self.subtitle_label.cget("text")
                    self.subtitle_label.configure(text=current_text + " " + word)
                    self.root.update()

                # Calculate the elapsed time and sleep accordingly
                elapsed_time = time.time() - start_time
                expected_time = duration_per_word * (words.index(word) + 1)
                sleep_time = max(0, expected_time - elapsed_time)
                time.sleep(sleep_time)

            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Limit the loop to 10 FPS to reduce CPU usage

            # Clean up pygame mixer
            pygame.mixer.quit()

        except Exception as e:
            print(f"Text-to-speech error: {e}")

        finally:
            # Clear the subtitle label after the audio finishes
            if self.root and self.subtitle_label.winfo_exists():
                self.subtitle_label.configure(text="")
                self.root.update()
        
    
    def listen(self, lang="en"):
        """Listen for user input and return the recognized text."""
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            try:
                winsound.PlaySound(self.start_sound, winsound.SND_FILENAME)
                recognizer.adjust_for_ambient_noise(source)
                self.subtitle_label.configure(text="Listening...")
                self.root.update()

                # Reduce listening time to 5 seconds
                audio = recognizer.listen(source, timeout=5)
                recognized_text = recognizer.recognize_google(audio, language=lang)
                winsound.PlaySound(self.end_sound, winsound.SND_FILENAME)
                return recognized_text

            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand audio.")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Could not request results; {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        return ""
    
    # ===================================================================================================

    # ======================================= listen case id ============================================
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
            winsound.PlaySound(self.start_sound, winsound.SND_FILENAME)
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

            try:
                recognized_text = recognizer.recognize_google(audio)
                recognized_text = recognized_text.upper()
                print(f"Recognized case type: {recognized_text}")

                closest_match = get_close_matches(recognized_text, case_types.keys(), n=1, cutoff=0.6)
                winsound.PlaySound(self.end_sound, winsound.SND_FILENAME)
                
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
            winsound.PlaySound(self.start_sound, winsound.SND_FILENAME)
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

            try:
                recognized_text = recognizer.recognize_google(audio, language=lang)
                print(f"Recognized case number: {recognized_text}")

                recognized_text = self.map_spoken_numbers(recognized_text, lang)
                recognized_text = recognized_text.replace("O", "0").replace("o", "0")
                recognized_text = recognized_text.replace(" ", "-")

                winsound.PlaySound(self.end_sound, winsound.SND_FILENAME)

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
            winsound.PlaySound(self.start_sound, winsound.SND_FILENAME)
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

            try:
                recognized_text = recognizer.recognize_google(audio, language=lang)
                recognized_text = self.map_spoken_numbers(recognized_text, lang)
                recognized_text = recognized_text.replace("O", "0").replace("o", "0")
                
                winsound.PlaySound(self.end_sound, winsound.SND_FILENAME)

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
    
    # ===================================================================================================
    
    # ====================================== Conversation ===============================================
    def conversation(self, lang="en"):
        """Engage in a conversation based on user input."""
        self.camera_pause = True

        # Dictionary of case types (abbreviation: full form)
        case_types = self.case_types
        
        prompt_lang = "Kindly select a language. I could understand three languages, Punjabi, English and Hindi. Speak anyone of them."

        prompt_lang = self.translate_text(prompt_lang, source='en', target=lang)
        self.speak_text(prompt_lang, lang=lang)
        selected_lang = self.listen(lang='en')

        if 'english' in selected_lang.lower():
            prompt_text = """
                Congrates you selected english language.
                Kindly tell me, how would you like to get the details?\n
                1. Case Search
                2. Judgment Search
                3. Filing Search
            """
            lang = 'en'
            self.speak_text(prompt_text, lang=lang)
        elif 'punjabi' in selected_lang.lower():
            prompt_text = """
                Congrates you selected punjabi language.
                Kindly tell me, how would you like to get the details?\n
                1. Case Search
                2. Judgment Search
                3. Filing Search
            """
            lang = 'pa'
            translated_prompt = self.translate_text(prompt_text, source="en", target=lang)
            self.speak_text(translated_prompt, lang=lang)
        elif 'hindi' in selected_lang.lower():
            prompt_text = """
                Congrates you selected hindi language.
                Kindly tell me, how would you like to get the details?\n
                1. Case Search
                2. Judgment Search
                3. Filing Search
            """
            lang = 'hi'
            translated_prompt = self.translate_text(prompt_text, source="en", target=lang)
            self.speak_text(translated_prompt, lang=lang)
        else:
            prompt_text = """
                You did not selected any language. So by default I will continoue with punjabi language.
                Kindly tell me, how would you like to get the details?\n
                1. Case Search
                2. Judgment Search
                3. Filing Search
            """
            lang = 'pa'
            translated_prompt = self.translate_text(prompt_text, source="en", target=lang)
            self.speak_text(translated_prompt, lang=lang)

        # Listen for user input
        search_type = self.listen(lang=lang)
        if any(str(word) in search_type.lower() for word in ['1', 'one', 'ek', 'ik', 'case search', 'केस खोज', 'ਕੇਸ ਖੋਜ', 'एक', 'ਇੱਕ']):
            search_type = 'case search'
        elif any(str(word) in search_type.lower() for word in ['2', 'two', 'tu', 'do', 'judgment search', 'निर्णय खोज', 'ਨਿਰਣੇ ਦੀ ਖੋਜ', 'दो', 'ਦੋ']):
            search_type = 'judgment search'
        elif any(str(word) in search_type.lower() for word in ['3', 'three', 'teen', 'filing search', 'फाइलिंग खोज', 'ਫਾਈਲਿੰਗ ਖੋਜ', 'तीन', 'ਤਿੰਨ']):
            search_type = 'filing search'
        else:
            print("no match found.")
        self.speak_text(self.translate_text(f"Ok. You want to make a search by {search_type}.", source='en', target=lang), lang=lang)

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
        
        self.camera_pause = False

    # ===================================================================================================

if __name__ == "__main__":
    root = ctk.CTk()
    tts = HighCourt(root)
    root.mainloop()
