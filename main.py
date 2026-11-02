import os
import threading
import keyboard
import pystray
from PIL import Image, ImageDraw
from quick_input import show_quick_input
from manager_gui import show_manager

def launch_async(target_fn):
    """Esegue la GUI in un thread separato per non bloccare il loop del tray o delle hotkey."""
    t = threading.Thread(target=target_fn, daemon=True)
    t.start()

def create_tray_icon_image():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, 60, 60], radius=14, fill="#111827", outline="#374151", width=2)
    points = [(18, 32), (28, 44), (46, 20)]
    draw.line(points, fill="#10b981", width=6, joint="curve")
    return img

def quit_app(icon, item=None):
    icon.stop()
    os._exit(0)

def setup_hotkeys():
    keyboard.add_hotkey("alt+n", lambda: launch_async(show_quick_input))
    keyboard.add_hotkey("alt+p", lambda: launch_async(show_manager))
    keyboard.wait()

def main():
    hotkey_thread = threading.Thread(target=setup_hotkeys, daemon=True)
    hotkey_thread.start()

    menu = pystray.Menu(
        pystray.MenuItem("Nuovo Task (Alt + N)", lambda icon, item: launch_async(show_quick_input)),
        pystray.MenuItem("Apri Manager (Alt + P)", lambda icon, item: launch_async(show_manager), default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Esci", quit_app)
    )

    icon = pystray.Icon(
        name="ToDoWallpaper",
        icon=create_tray_icon_image(),
        title="To-Do Wallpaper Manager",
        menu=menu
    )

    icon.run()

if __name__ == "__main__":
    main()