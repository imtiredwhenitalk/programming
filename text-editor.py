import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel, filedialog

UTF_SPACES = {
    '\u0020': "Звичайний пробіл",
    '\u00A0': "NO-BREAK SPACE",
    '\u1680': "OGHAM SPACE MARK",
    '\u2000': "EN QUAD",
    '\u2001': "EM QUAD",
    '\u2002': "EN SPACE",
    '\u2003': "EM SPACE",
    '\u2004': "THREE-PER-EM SPACE",
    '\u2005': "FOUR-PER-EM SPACE",
    '\u2006': "SIX-PER-EM SPACE",
    '\u2007': "FIGURE SPACE",
    '\u2008': "PUNCTUATION SPACE",
    '\u2009': "THIN SPACE",
    '\u200A': "HAIR SPACE",
    '\u200B': "ZERO WIDTH SPACE",
    '\u200C': "ZERO WIDTH NON-JOINER",
    '\u200D': "ZERO WIDTH JOINER",
    '\u202F': "NARROW NO-BREAK SPACE",
    '\u205F': "MEDIUM MATHEMATICAL SPACE",
    '\u2060': "WORD JOINER",
    '\u3000': "IDEOGRAPHIC SPACE",
    '\u180E': "MONGOLIAN VOWEL SEPARATOR",
    '\uFEFF': "ZERO WIDTH NO-BREAK SPACE (BOM)", 
}

def clear_highlight():
    for tag in text_area.tag_names():
        text_area.tag_delete(tag)

def highlight_spaces():
    clear_highlight()
    txt = text_area.get("1.0", tk.END)
    for i, ch in enumerate(txt):
        if ch in UTF_SPACES and ch != " ":
            pos_start = f"1.0+{i}c"
            pos_end = f"1.0+{i+1}c"
            text_area.tag_add(f"sp_{i}", pos_start, pos_end)
            text_area.tag_config(f"sp_{i}", background="red", foreground="white")

def check_utf_spaces():
    txt = text_area.get("1.0", tk.END)
    found = []
    for i, ch in enumerate(txt):
        if ch in UTF_SPACES and ch != " ":
            found.append((i + 1, UTF_SPACES[ch], repr(ch)))
    if found:
        msg = f"Знайдено {len(found)} спец-пробілів:\n\n"
        for idx, name, repr_sp in found:
            msg += f"Позиція {idx}: {name} ({repr_sp})\n"
        highlight_spaces()
        show_in_window("Результати перевірки", msg)
    else:
        clear_highlight()
        messagebox.showinfo("Перевірка", "Спец-пробілів не знайдено!")

def clean_utf_spaces():
    txt = text_area.get("1.0", tk.END)
    for sp in UTF_SPACES:
        if sp != " ":
            txt = txt.replace(sp, " ")
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", txt)
    clear_highlight()
    messagebox.showinfo("Очищення", "Всі спец-пробіли замінені на звичайні!")

def space_statistics():
    txt = text_area.get("1.0", tk.END)
    stats = {}
    for ch in txt:
        if ch in UTF_SPACES and ch != " ":
            stats[UTF_SPACES[ch]] = stats.get(UTF_SPACES[ch], 0) + 1
    if stats:
        msg = "Статистика пробілів:\n\n"
        for name, count in stats.items():
            msg += f"{name}: {count}\n"
        show_in_window("Статистика пробілів", msg)
    else:
        messagebox.showinfo("Статистика", "Жодних спец-пробілів не знайдено.")

def show_in_window(title, content):
    win = Toplevel(root)
    win.title(title)
    win.geometry("500x400")
    txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Calibri", 12))
    txt.pack(expand=True, fill='both')
    txt.insert("1.0", content)
    txt.config(state="disabled")

def paste_text():
    try:
        content = root.clipboard_get()
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", content)
    except:
        messagebox.showerror("Помилка", "Буфер обміну порожній або містить не текст!")

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            text_area.delete("1.0", tk.END)
            text_area.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}") 

def save_file(): 
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path: 
        try: 
            content = text_area.get("1.0", tk.END) 
            with open(file_path, "w", encoding="utf-8") as f: 
                f.write(content)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")

def on_closing(): 
    if messagebox.askokcancel("Вихід", "Ви дійсно хочете вийти?"):
        root.destroy() 

root = tk.Tk()
root.title("AI-Proof Text Cleaner")
root.geometry("800x600")
root.config(bg="lightgrey")
root.resizable(0, 0)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Calibri", 12))
text_area.pack(expand=True, fill='both')
text_area.config(bg="white", fg="black", insertbackground="black")

frame = tk.Frame(root, bg="lightgrey")
frame.pack(fill="x")

btn_check = tk.Button(frame, text="Перевірити текст", command=check_utf_spaces, bg="#e0e0e0")
btn_check.pack(side="left", padx=5, pady=5)

btn_clean = tk.Button(frame, text="Очистити текст", command=clean_utf_spaces, bg="#e0e0e0")
btn_clean.pack(side="left", padx=5, pady=5)

btn_stats = tk.Button(frame, text="Статистика пробілів", command=space_statistics, bg="#e0e0e0")
btn_stats.pack(side="left", padx=5, pady=5)

btn_paste = tk.Button(frame, text="Вставити текст", command=paste_text, bg="#d0ffd0")
btn_paste.pack(side="left", padx=5, pady=5)

btn_load = tk.Button(frame, text="Завантажити файл", command=load_file, bg="#d0d0ff")
btn_load.pack(side="left", padx=5, pady=5) 

btn_save = tk.Button(frame, text="Зберегти файл", command=save_file, bg="#ffffd0")
btn_save.pack(side="left", padx=5, pady=5)

btn_exit = tk.Button(frame, text="Вийти", command=on_closing, bg="#ffb0b0") 
btn_exit.pack(side="right", padx=5, pady=5)
root.mainloop()
