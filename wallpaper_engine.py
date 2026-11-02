import ctypes
import os
import shutil
import sys
import time
import winreg
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01

def get_app_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
OUTPUT_WALLPAPER = os.path.normpath(os.path.join(APP_DIR, "current_wallpaper.png"))
TEMP_WALLPAPER = os.path.normpath(os.path.join(APP_DIR, "current_wallpaper_temp.png"))
BACKUP_BASE_WALLPAPER = os.path.normpath(os.path.join(APP_DIR, "original_base_wallpaper.png"))

def enable_dpi_awareness():
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

def get_screen_resolution() -> tuple[int, int]:
    enable_dpi_awareness()
    user32 = ctypes.windll.user32
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)
    if w <= 0 or h <= 0:
        return 1920, 1080
    return w, h

def get_windows_current_wallpaper() -> str:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
        wallpaper_path, _ = winreg.QueryValueEx(key, "Wallpaper")
        winreg.CloseKey(key)
        if wallpaper_path and os.path.exists(wallpaper_path):
            return os.path.normpath(wallpaper_path)
    except Exception:
        pass

    appdata = os.environ.get("APPDATA", "")
    transcoded = os.path.join(appdata, r"Microsoft\Windows\Themes\TranscodedWallpaper")
    if os.path.exists(transcoded):
        return os.path.normpath(transcoded)

    return ""

def get_base_image_path() -> str:
    system_wall = get_windows_current_wallpaper()

    if system_wall and os.path.exists(system_wall):
        if system_wall.lower() not in (OUTPUT_WALLPAPER.lower(), TEMP_WALLPAPER.lower()):
            try:
                shutil.copyfile(system_wall, BACKUP_BASE_WALLPAPER)
                return BACKUP_BASE_WALLPAPER
            except Exception:
                return system_wall

    if os.path.exists(BACKUP_BASE_WALLPAPER):
        return BACKUP_BASE_WALLPAPER

    for fallback_name in ("base_wallpaper.jpg", "base_wallpaper.png"):
        candidate = os.path.join(APP_DIR, fallback_name)
        if os.path.exists(candidate):
            return candidate

    return system_wall

def safe_save_and_apply(img: Image.Image, output_path: str):
    """Salvataggio asincrono/protetto che non manda in deadlock le finestre Tkinter."""
    try:
        final_img = img.convert("RGB")
        final_img.save(TEMP_WALLPAPER, format="PNG", compress_level=1)
        
        for _ in range(5):
            try:
                if os.path.exists(output_path):
                    os.replace(TEMP_WALLPAPER, output_path)
                else:
                    os.rename(TEMP_WALLPAPER, output_path)
                break
            except PermissionError:
                time.sleep(0.05)

        abs_path = os.path.abspath(output_path)
        # Solo SPIF_UPDATEINIFILE evita broadcast sincroni bloccanti per la GUI
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            abs_path,
            SPIF_UPDATEINIFILE
        )
    except Exception as e:
        print(f"Errore wallpaper non bloccante: {e}")

def is_background_dark(img: Image.Image, box_area: tuple[int, int, int, int]) -> bool:
    try:
        crop_area = img.crop(box_area).convert("L")
        stat = ImageStat.Stat(crop_area)
        return stat.mean[0] < 128
    except Exception:
        return False

def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    if not text:
        return [""]
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        bbox = font.getbbox(test_line)
        line_w = bbox[2] - bbox[0]
        if line_w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = ""
            word_bbox = font.getbbox(word)
            if word_bbox[2] - word_bbox[0] > max_width:
                chunk = ""
                for char in word:
                    test_chunk = chunk + char
                    c_bbox = font.getbbox(test_chunk)
                    if c_bbox[2] - c_bbox[0] <= max_width:
                        chunk = test_chunk
                    else:
                        if chunk:
                            lines.append(chunk)
                        chunk = char
                current_line = chunk
            else:
                current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def render_and_update_wallpaper(
    output_path: str = OUTPUT_WALLPAPER,
    tasks: list = None,
    title: str = "Progetti",
    theme: str = "auto",
    card_bg: bool = False
):
    if tasks is None:
        tasks = []

    base_image_path = get_base_image_path()
    screen_w, screen_h = get_screen_resolution()

    if not base_image_path or not os.path.exists(base_image_path):
        raw_img = Image.new("RGB", (screen_w, screen_h), (30, 41, 59))
    else:
        try:
            with Image.open(base_image_path) as opened_img:
                raw_img = opened_img.copy()
        except Exception:
            raw_img = Image.new("RGB", (screen_w, screen_h), (30, 41, 59))

    if not tasks:
        fitted_base = ImageOps.fit(raw_img.convert("RGB"), (screen_w, screen_h), Image.Resampling.LANCZOS)
        safe_save_and_apply(fitted_base, output_path)
        return

    img = ImageOps.fit(raw_img.convert("RGBA"), (screen_w, screen_h), Image.Resampling.LANCZOS)

    scale = min(screen_w / 1920.0, screen_h / 1080.0)
    scale = max(scale, 0.75)

    font_task_size = int(20 * scale)
    font_title_size = int(22 * scale)
    font_date_size = int(17 * scale)
    box_size = int(15 * scale)
    half_box = box_size // 2

    try:
        font_task = ImageFont.truetype("arial.ttf", font_task_size)
        font_title = ImageFont.truetype("arialbd.ttf", font_title_size)
        font_date = ImageFont.truetype("arial.ttf", font_date_size)
    except IOError:
        font_task = ImageFont.load_default()
        font_title = font_task
        font_date = font_task

    screen_margin = int(28 * scale)
    card_padding = int(22 * scale)
    card_width = int(450 * scale)

    card_x1 = max(0, screen_w - screen_margin - card_width)
    card_y1 = screen_margin
    card_x2 = min(screen_w, screen_w - screen_margin)

    content_start_x = card_x1 + card_padding
    content_start_y = card_y1 + card_padding

    inner_margin = int(14 * scale)
    date_col_offset = int(270 * scale)
    separator_x = content_start_x + date_col_offset - int(16 * scale)
    text_start_x = content_start_x + box_size + inner_margin
    max_text_width = max(50, (separator_x - inner_margin) - text_start_x)

    line_height = int(26 * scale)
    task_gap = int(14 * scale)
    title_height = int(42 * scale)

    total_tasks_height = 0
    prepared_tasks = []
    for t in tasks:
        lines = wrap_text(t.get("testo", ""), font_task, max_text_width)
        h = (len(lines) * line_height) + task_gap
        total_tasks_height += h
        prepared_tasks.append((t, lines))

    card_height = card_padding + title_height + total_tasks_height + (card_padding // 2)
    card_y2 = min(screen_h - 10, card_y1 + card_height)

    if theme == "dark":
        dark_card = True
    elif theme == "light":
        dark_card = False
    else:
        sample_area = (card_x1, card_y1, card_x2, min(screen_h, card_y2))
        dark_card = is_background_dark(img, sample_area)

    if dark_card:
        text_color = (248, 250, 252, 255)
        date_color = (148, 163, 184, 255)
        line_color = (100, 116, 139, 160)
        box_border = (52, 211, 153, 255)
        box_checked_fill = (248, 113, 113, 255)
        card_fill = (15, 23, 42, 190)
        card_outline = (148, 163, 184, 70)
    else:
        text_color = (15, 23, 42, 255)
        date_color = (71, 85, 105, 255)
        line_color = (148, 163, 184, 180)
        box_border = (16, 185, 129, 255)
        box_checked_fill = (239, 68, 68, 255)
        card_fill = (255, 255, 255, 200)
        card_outline = (255, 255, 255, 150)

    if card_bg:
        overlay = Image.new("RGBA", (screen_w, screen_h), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        corner_radius = int(16 * scale)
        overlay_draw.rounded_rectangle(
            [card_x1, card_y1, card_x2, card_y2],
            radius=corner_radius,
            fill=card_fill,
            outline=card_outline,
            width=max(1, int(1 * scale))
        )
        img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    display_title = title.rstrip(":").strip()
    draw.text((content_start_x, content_start_y), display_title, font=font_title, fill=text_color)

    current_y = content_start_y + title_height
    border_width = max(1, int(2 * scale))
    check_border = max(1, int(1 * scale))
    max_task_y = current_y

    for task, lines in prepared_tasks:
        # Limite massimo di 16 caratteri sul testo della data
        date_text = str(task.get("data", ""))[:16]
        first_line_mid_y = current_y + half_box
        box_x = content_start_x

        if task.get("completato", False):
            draw.rectangle(
                [box_x, first_line_mid_y - half_box, box_x + box_size, first_line_mid_y + half_box],
                fill=box_checked_fill,
                outline=text_color,
                width=check_border
            )
        else:
            draw.rectangle(
                [box_x, first_line_mid_y - half_box, box_x + box_size, first_line_mid_y + half_box],
                outline=box_border,
                width=border_width
            )

        if date_text:
            draw.text(
                (content_start_x + date_col_offset, first_line_mid_y),
                date_text,
                font=font_date,
                fill=date_color,
                anchor="lm"
            )

        for i, line in enumerate(lines):
            line_mid_y = current_y + half_box + (i * line_height)
            draw.text(
                (text_start_x, line_mid_y),
                line,
                font=font_task,
                fill=text_color,
                anchor="lm"
            )
            max_task_y = max(max_task_y, line_mid_y)

        current_y += (len(lines) * line_height) + task_gap

    draw.line(
        [(separator_x, content_start_y + int(36 * scale)), (separator_x, max_task_y + int(10 * scale))],
        fill=line_color,
        width=max(1, int(1 * scale))
    )

    safe_save_and_apply(img, output_path)