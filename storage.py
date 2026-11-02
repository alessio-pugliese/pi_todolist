import json
import os
import sys

def get_app_dir() -> str:
    """Restituisce la cartella reale dell'eseguibile o dello script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(get_app_dir(), "tasks.json")

def load_data() -> dict:
    default_data = {
        "title": "Progetti",
        "theme": "auto",
        "card_bg": False,
        "tasks": []
    }
    if not os.path.exists(DATA_FILE):
        return default_data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {
                    "title": "Progetti:",
                    "theme": "auto",
                    "card_bg": False,
                    "tasks": data
                }
            if "theme" not in data:
                data["theme"] = "auto"
            if "card_bg" not in data:
                data["card_bg"] = False
            return data
    except Exception:
        return default_data

def save_data(data: dict):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_tasks() -> list:
    return load_data().get("tasks", [])

def get_title() -> str:
    return load_data().get("title", "Progetti:")

def get_theme() -> str:
    return load_data().get("theme", "auto")

def get_card_bg() -> bool:
    return load_data().get("card_bg", False)

def set_settings(new_title: str, new_theme: str, new_card_bg: bool):
    data = load_data()
    clean_title = new_title.rstrip(":").strip()
    data["title"] = clean_title if clean_title else "Progetti"
    data["theme"] = new_theme if new_theme in ("auto", "light", "dark") else "auto"
    data["card_bg"] = bool(new_card_bg)
    save_data(data)

def save_tasks(tasks: list):
    data = load_data()
    data["tasks"] = tasks
    save_data(data)

def add_quick_task(testo: str) -> dict:
    data = load_data()
    tasks = data.get("tasks", [])
    new_id = max([t.get("id", 0) for t in tasks], default=0) + 1
    tasks.append({
        "id": new_id,
        "testo": testo.strip(),
        "data": "",
        "completato": False
    })
    data["tasks"] = tasks
    save_data(data)
    return data