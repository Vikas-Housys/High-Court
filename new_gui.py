import customtkinter as ctk
from PIL import Image
import os

class LegalCaseGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Legal Case Management")
        self.geometry("1080x1960")
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header image frame
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=40, pady=(40,20), sticky="ew")
        
        # Load and display header image
        try:
            self.header_image = ctk.CTkImage(
                light_image=Image.open("legal_header.png"),
                dark_image=Image.open("legal_header.png"),
                size=(1000, 400)  # Increased size for larger screen
            )
            self.header_label = ctk.CTkLabel(self.header_frame, image=self.header_image, text="")
            self.header_label.grid(row=0, column=0)
        except:
            self.header_label = ctk.CTkLabel(self.header_frame, text="Legal Case Management", 
                                           font=ctk.CTkFont(size=48, weight="bold"))
            self.header_label.grid(row=0, column=0)

        # Search frame with increased size
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_frame.grid(row=1, column=0, padx=40, pady=20, sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)
        
        # Larger search entry with microphone icon
        self.search_entry = ctk.CTkEntry(self.search_frame, 
                                       placeholder_text="Search for your case details",
                                       height=60,
                                       font=ctk.CTkFont(size=20))
        self.search_entry.grid(row=0, column=0, sticky="ew")
        
        self.mic_button = ctk.CTkButton(self.search_frame, text="🎤", width=60,
                                       height=60, font=ctk.CTkFont(size=20),
                                       command=self.activate_voice)
        self.mic_button.grid(row=0, column=1, padx=(10,0))

        # Language selection frame with larger buttons
        self.lang_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.lang_frame.grid(row=2, column=0, padx=40, pady=20)
        
        # Larger language buttons
        button_config = {
            "width": 200,
            "height": 50,
            "font": ctk.CTkFont(size=20),
            "fg_color": "#6B4EFF",
            "hover_color": "#5540CC"
        }
        
        self.english_btn = ctk.CTkButton(self.lang_frame, text="English", **button_config)
        self.english_btn.grid(row=0, column=0, padx=10)
        
        self.hindi_btn = ctk.CTkButton(self.lang_frame, text="हिंदी", **button_config)
        self.hindi_btn.grid(row=0, column=1, padx=10)
        
        self.punjabi_btn = ctk.CTkButton(self.lang_frame, text="ਪੰਜਾਬੀ", **button_config)
        self.punjabi_btn.grid(row=0, column=2, padx=10)

        # Larger info section
        self.info_label = ctk.CTkLabel(
            self.main_frame,
            text="Demonstrate how the software caters\nto different user roles (e.g., lawyers\nfiling cases, judges managing)",
            font=ctk.CTkFont(size=24),
            justify="left"
        )
        self.info_label.grid(row=3, column=0, padx=40, pady=20, sticky="w")

        # Case details frame with increased size
        self.case_frame = ctk.CTkFrame(self.main_frame)
        self.case_frame.grid(row=4, column=0, padx=40, pady=20, sticky="ew")
        
        # Larger case number header
        self.case_header = ctk.CTkLabel(
            self.case_frame,
            text="Case No. 56",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.case_header.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Larger case description
        self.case_desc = ctk.CTkLabel(
            self.case_frame,
            text="Your case no. is 56 this is the court room and the reason that is due",
            font=ctk.CTkFont(size=20),
            wraplength=900
        )
        self.case_desc.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Create grid of case numbers with larger text
        for i in range(3):
            for j in range(2):
                case_label = ctk.CTkLabel(self.case_frame, 
                                        text="Case No.",
                                        font=ctk.CTkFont(size=20))
                case_label.grid(row=i+2, column=j, padx=20, pady=10)
                case_number = ctk.CTkLabel(self.case_frame, 
                                         text="56",
                                         font=ctk.CTkFont(size=20))
                case_number.grid(row=i+2, column=j, padx=(140,0), pady=10)

        # Larger pathway button
        self.pathway_btn = ctk.CTkButton(
            self.case_frame,
            text="See pathway",
            font=ctk.CTkFont(size=20),
            fg_color="#6B4EFF",
            hover_color="#5540CC",
            width=300,
            height=50
        )
        self.pathway_btn.grid(row=5, column=0, columnspan=2, pady=30)

    def activate_voice(self):
        print("Voice search activated")

if __name__ == "__main__":
    app = LegalCaseGUI()
    # Set the color theme
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app.mainloop()