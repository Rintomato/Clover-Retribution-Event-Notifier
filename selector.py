import ctypes
import json
import tkinter as tk

# Make the process DPI aware (Windows)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class AreaSelector:
    def __init__(self, parent=None):
        self.result = None

        self.start_x = 0
        self.start_y = 0

        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.withdraw()

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        print(f"Screen Size: {screen_width} x {screen_height}")

        self.window.overrideredirect(True)
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.configure(bg="black")
        self.window.attributes("-alpha", 0.30)
        self.window.attributes("-topmost", True)

        self.canvas = tk.Canvas(
            self.window,
            bg="black",
            cursor="cross",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)

        self.window.bind("<Escape>", self.cancel)

    def mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.rect:
            self.canvas.delete(self.rect)

        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="red",
            width=2
        )

    def mouse_drag(self, event):
        if self.rect:
            self.canvas.coords(
                self.rect,
                self.start_x,
                self.start_y,
                event.x,
                event.y
            )

    def mouse_up(self, event):
        left = min(self.start_x, event.x)
        top = min(self.start_y, event.y)
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)

        if width < 5 or height < 5:
            self.cancel()
            return

        self.result = {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }

        with open("config.json", "w") as f:
            json.dump(self.result, f, indent=4)

        print("Saved:", self.result)

        self.window.destroy()

    def cancel(self, event=None):
        self.result = None
        self.window.destroy()

    def run(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.window.wait_window()
        return self.result