import tkinter
from itertools import cycle
from pathlib import Path
import random
from collections import deque
import tkinter.font as tkfont

_COLOR_CYCLE = cycle(("#FF0000", "#000000"))

def change_bg_color():
    return next(_COLOR_CYCLE)

def load_art_text():
    art_path = Path(__file__).with_name("text.txt")
    try:
        return art_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "[text.txt not found]"
    except UnicodeDecodeError:
        return art_path.read_text(encoding="cp1251", errors="replace")

root = tkinter.Tk()
root.title("Suck Balls")
root.attributes("-fullscreen", True)
root.configure(background=change_bg_color())

def close(event):
    root.destroy()

root.bind("<Escape>", close)

_art_text = load_art_text()
_art_font = tkfont.Font(family="Consolas", size=16)

art_label = tkinter.Label(
    root,
    text=_art_text,
    font=_art_font,
    fg="white",
    bg=root["background"],
    justify="left",
    anchor="nw",
)
art_label.place(x=10, y=10)

_error_templates = [
    "Unhandled exception in {module}: null pointer dereference (0xC0000005)",
    "Cannot open file '{path}': Access is denied.",
    "Network timeout while connecting to {host}:{port}",
    "Assertion failed: {expr} ({file}:{line})",
    "Segmentation fault at address 0x{addr}",
    "Failed to allocate {mb}MB: out of memory",
    "CRC mismatch while reading '{path}'",
    "Invalid opcode 0x{op} in JIT pipeline",
    "Thread {tid} deadlocked waiting for mutex '{mtx}'",
    "GPU device removed (DXGI_ERROR_DEVICE_HUNG)",
]
_modules = ["kernel32.dll", "user32.dll", "ntdll.dll", "app.exe", "renderer.dll"]
_hosts = ["127.0.0.1", "10.0.0.2", "cdn.example", "api.service", "gateway"]
_paths = [
    "C:/Windows/System32/config/systemprofile",
    "C:/Users/User/AppData/Local/Temp/cache.bin",
    "D:/data/savegame.dat",
    "C:/Program Files/App/config.json",
]
_mutexes = ["render", "audio", "io", "net", "physics"]
_exprs = ["ptr != NULL", "index < size", "state == READY", "len(buf) > 0"]
_files = ["main.cpp", "engine.cpp", "net.cpp", "io.cpp", "gpu.cpp"]

_error_font = tkfont.Font(family="Consolas", size=12)
_line_h = _art_font.metrics("linespace")
_art_lines = max(1, len(_art_text.splitlines()))
_error_y = 20 + (_art_lines * _line_h) + 20

_error_log = deque(maxlen=25)

error_label = tkinter.Label(
    root,
    text="",
    font=_error_font,
    fg="white",
    bg=root["background"],
    justify="left",
    anchor="nw",
)
error_label.place(x=10, y=_error_y)

# Текст по середині (трохи правіше)
_center_font = tkfont.Font(family="Consolas", size=20, weight="bold")
center_label = tkinter.Label(
    root,
    text=":( Мы наткнулись с некоторимы проблемами на вашем устройств.... \n Чё блять? Ему пизда))))",  
    font=_center_font,
    fg="white",
    bg=root["background"],
)
center_label.place(relx=0.65, rely=0.52, anchor="center")

def show_error():
    tmpl = random.choice(_error_templates)
    data = {
        "module": random.choice(_modules),
        "path": random.choice(_paths),
        "host": random.choice(_hosts),
        "port": random.randint(1, 65535),
        "expr": random.choice(_exprs),
        "file": random.choice(_files),
        "line": random.randint(1, 5000),
        "addr": f"{random.randint(0, 16**8 - 1):08X}",
        "mb": random.choice([64, 128, 256, 512, 1024, 2048, 4096]),
        "op": f"{random.randint(0, 255):02X}",
        "tid": random.randint(100, 9999),
        "mtx": random.choice(_mutexes),
    }
    return tmpl.format(**data)

def update_errors():
    _error_log.append(show_error())
    error_label.configure(text="\n".join(_error_log))
    root.after(50, update_errors)

def update_color():
    new_bg = change_bg_color()
    root.configure(background=new_bg)
    
    for w in root.winfo_children():
        if isinstance(w, tkinter.Label):
            w.configure(bg=new_bg)

    root.after(100, update_color)

update_color()
update_errors()
root.mainloop()