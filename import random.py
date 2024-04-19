import customtkinter as ctk
from PIL import Image

root = ctk.CTk()
root.geometry('800x600')  # Set your desired window size

# Load the background image
bgimg = Image.open('lethal_art.png')  # Replace with your image path
bgimg_tk = ctk.CTkImage(bgimg)

# Create a label to display the background image
background_label = ctk.CTkLabel(root, image=bgimg_tk)
background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Make the label fit the window

# Create a frame inside the label (acts as the content container)
frame = ctk.CTkFrame(background_label, bg_color='white')  # Set the background color of the frame
frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)  # Adjust position and size

# Add widgets (buttons, labels, etc.) inside the frame
ctk.CTkLabel(frame, text='Some File').grid(row=0, column=0)
e1 = ctk.CTkEntry(frame)
e1.grid(row=0, column=1)

root.mainloop()
