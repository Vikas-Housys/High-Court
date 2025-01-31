import customtkinter
from PIL import Image, ImageTk
    
window = customtkinter.CTk()
    
button_image = customtkinter.CTkImage(Image.open("images/mic.png"), size=(26, 26))
    
image_button = customtkinter.CTkButton(master=window, text="Text will be gone if you don't use compound attribute",image=button_image)
image_button.pack()
    
window.mainloop()