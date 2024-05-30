import customtkinter as ctk
from PIL import Image
import winreg

#           CODE SOURCED FROM
#               https://github.com/rudymohammadbali/ctk_components
#
#
#           MODIFIED BY DARTHLILO, ORIGINAL BY RUDYMOHAMMADBALI
#
#           CTK Component Changes
#               - Added a show cancel button argument
#               - Added the ability to change the progress bar color
#               - Added support for different windows DPI scaling options
#
#

def get_windows_scaling_factor():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Control Panel\Desktop\WindowMetrics")
        value, _ = winreg.QueryValueEx(key,"AppliedDPI")
        winreg.CloseKey(key)
        return value/96
    except Exception as e:
        print("Error:",e)
        return 1

def place_frame(master, frame, horizontal="right", vertical="bottom", padx=20, pady=20):

    windows_scale = get_windows_scaling_factor()

    master_width = master.winfo_width()/windows_scale
    master_height = master.winfo_height()/windows_scale

    frame_width = frame.winfo_reqwidth()/windows_scale
    frame_height = frame.winfo_reqheight()/windows_scale

    frame_x = 20 if horizontal == "left" else master_width - frame_width - padx
    frame_y = 20 if vertical == "top" else master_height - frame_height - pady

    frame.place(x=frame_x, y=frame_y)

class CTkProgressPopup(ctk.CTkFrame):
    def __init__(self, master, title: str = "Background Tasks", label: str = "Label...",
                 message: str = "Do something...", side: str = "right_bottom",show_cancel_button=True,progress_color="#1f6aa5"):
        self.root = master
        self.width = 420
        self.height = 120
        super().__init__(self.root, width=self.width, height=self.height, corner_radius=5, border_width=1)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.cancelled = False

        self.title = ctk.CTkLabel(self, text=title, font=("", 16))
        self.title.grid(row=0, column=0, sticky="ew", padx=20, pady=10, columnspan=2)

        self.label = ctk.CTkLabel(self, text=label, height=0)
        self.label.grid(row=1, column=0, sticky="sw", padx=20, pady=0)

        self.progressbar = ctk.CTkProgressBar(self,progress_color=progress_color)
        self.progressbar.set(0)
        self.progressbar.grid(row=2, column=0, sticky="ew", padx=20, pady=0 if show_cancel_button else 10)

        if show_cancel_button:

            self.close_icon = ctk.CTkImage(Image.open("assets/cross.png"),
                                           Image.open("assets/cross.png"),
                                           (16, 16))

            self.cancel_btn = ctk.CTkButton(self, text="", width=16, height=16, fg_color="transparent",
                                            command=self.cancel_task, image=self.close_icon)
            self.cancel_btn.grid(row=2, column=1, sticky="e", padx=10, pady=0)

        self.message = ctk.CTkLabel(self, text=message, height=0)
        self.message.grid(row=3, column=0, sticky="nw", padx=20, pady=(0, 10))

        self.horizontal, self.vertical = side.split("_")
        place_frame(self.root, self, self.horizontal, self.vertical)
        self.root.bind("<Configure>", self.update_position, add="+")

    def update_position(self, event):
        place_frame(self.root, self, self.horizontal, self.vertical)
        self.update_idletasks()
        self.root.update_idletasks()

    def update_progress(self, progress):
        if self.cancelled:
            return "Cancelled"
        self.progressbar.set(progress)

    def update_message(self, message):
        self.message.configure(text=message)

    def update_label(self, label):
        self.label.configure(text=label)

    def cancel_task(self):
        self.cancelled = True
        self.close_progress_popup()

    def close_progress_popup(self):
        self.root.unbind("<Configure>")
        self.destroy()