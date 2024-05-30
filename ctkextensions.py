import customtkinter as ctk
from PIL import Image
import winreg
from pywinstyles import set_opacity

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

class CTkGif(ctk.CTkLabel):

    def __init__(self, master: any, path, loop=True, acceleration=1, repeat=1, width=40, height=40, **kwargs):
        super().__init__(master, **kwargs)
        if acceleration <= 0:
            raise ValueError('Acceleration must be strictly positive')
        self.master = master
        self.repeat = repeat
        self.configure(text='')
        self.path = path
        self.count = 0
        self.loop = loop
        self.acceleration = acceleration
        self.index = 0
        self.is_playing = False
        self.gif = Image.open(path)
        self.n_frame = self.gif.n_frames
        self.frame_duration = self.gif.info['duration'] * 1 / self.acceleration
        self.force_stop = False

        self.width = width
        self.height = height

    def update(self):
        if self.index < self.n_frame:
            if not self.force_stop:
                self.gif.seek(self.index)
                self.configure(image=ctk.CTkImage(self.gif, size=(self.width, self.height)))
                self.index += 1
                self.after(int(self.frame_duration), self.update)
            else:
                self.force_stop = False
        else:
            self.index = 0
            self.count += 1
            if self.is_playing and (self.count < self.repeat or self.loop):
                self.after(int(self.frame_duration), self.update)
            else:
                self.is_playing = False

    def start(self):
        if not self.is_playing:
            self.count = 0
            self.is_playing = True
            self.after(int(self.frame_duration), self.update)

    def stop(self, forced=False):
        if self.is_playing:
            self.is_playing = False
            self.force_stop = forced

    def toggle(self, forced=False):
        if self.is_playing:
            self.stop(forced=forced)
        else:
            self.start()

class CTkLoader(ctk.CTkFrame):
    def __init__(self, master: any, opacity: float = 0.8, width: int = 40, height: int = 40):
        self.master = master
        self.master.update()
        self.master_width = self.master.winfo_width()
        self.master_height = self.master.winfo_height()
        super().__init__(master, width=self.master_width, height=self.master_height, corner_radius=0)

        set_opacity(self.winfo_id(), value=opacity)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.loader = CTkGif(self, "assets/loader_wheel.gif", width=width, height=height)
        self.loader.grid(row=0, column=0, sticky="nsew")
        self.loader.start()

        self.place(relwidth=1.0, relheight=1.0)

    def stop_loader(self):
        self.loader.stop()
        self.destroy()