import ctypes
from ctypes import wintypes
import tkinter as tk
from storage import add_quick_task
from wallpaper_engine import render_and_update_wallpaper

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def force_window_focus(hwnd):
    """
    Forza il focus reale di input aggirando le protezioni anti-focus-stealing di Windows
    tramite AttachThreadInput tra la finestra attiva e la nostra GUI.
    """
    try:
        foreground_hwnd = user32.GetForegroundWindow()
        if foreground_hwnd == hwnd:
            return

        current_thread_id = kernel32.GetCurrentThreadId()
        foreground_thread_id = user32.GetWindowThreadProcessId(foreground_hwnd, None)

        if foreground_thread_id != current_thread_id:
            user32.AttachThreadInput(foreground_thread_id, current_thread_id, True)
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            user32.SetFocus(hwnd)
            user32.AttachThreadInput(foreground_thread_id, current_thread_id, False)
        else:
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            user32.SetFocus(hwnd)
    except Exception:
        pass

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

def show_quick_input():
    root = tk.Tk()
    root.title("Quick Task")
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    bg_key = "#ff00fe"
    root.config(bg=bg_key)
    root.wm_attributes("-transparentcolor", bg_key)

    w, h = 520, 56
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = int(sh * 0.40) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    canvas = tk.Canvas(root, width=w, height=h, bg=bg_key, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    x1, y1 = 2, 2
    x2, y2 = w - 2, h - 2
    radius = 12

    draw_rounded_rect(canvas, x1, y1, x2, y2, radius, fill="#374151", outline="")
    draw_rounded_rect(canvas, x1 + 1, y1 + 1, x2 - 1, y2 - 1, radius - 1, fill="#111827", outline="")

    canvas.create_text(
        x1 + 22, (y1 + y2) // 2, 
        text=">", 
        font=("Courier New", 14, "bold"), 
        fill="#10b981"
    )

    entry = tk.Entry(
        root,
        font=("Courier New", 13),
        bg="#111827",
        fg="#f3f4f6",
        insertbackground="#10b981",
        relief=tk.FLAT,
        bd=0
    )
    
    entry_x = x1 + 40
    entry_w = (x2 - x1) - 54
    entry_h = 28
    entry_y = (h - entry_h) // 2

    entry.place(x=entry_x, y=entry_y, width=entry_w, height=entry_h)

    # Costringiamo Windows a renderizzare la finestra prima di rubare il focus
    root.update_idletasks()

    def activate_focus():
        try:
            hwnd = root.winfo_id()
            force_window_focus(hwnd)
        except Exception:
            pass
        root.lift()
        root.focus_force()
        entry.focus_set()

    root.after(10, activate_focus)

    def on_submit(event=None):
        testo = entry.get().strip()
        if testo:
            data = add_quick_task(testo)
            render_and_update_wallpaper(
                tasks=data["tasks"], 
                title=data.get("title", "Progetti"),
                theme=data.get("theme", "auto"),
                card_bg=data.get("card_bg", False)
            )
        root.destroy()

    def on_cancel(event=None):
        root.destroy()

    entry.bind("<Return>", on_submit)
    entry.bind("<Escape>", on_cancel)

    root.mainloop()

if __name__ == "__main__":
    show_quick_input()