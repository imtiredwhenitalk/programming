import tkinter 
from tkinter import Label, Button, Tk, filedialog, simpledialog, messagebox, Listbox 
import os
import zipfile
import shutil
from datetime import datetime
import csv 
import json
import xml.etree.ElementTree as ET
import sqlite3
import pandas as pd
import openpyxl
import subprocess

CORRECT_PASSWORD = "1233211" 

root = Tk()
root.state('zoomed')  # Fullscreen
root.configure(bg="lightgrey")
root.title("Database Viewer")
selected_folder = "" 


# --- Main frame for layout ---7
main_frame = tkinter.Frame(root, bg="lightgrey")
main_frame.pack(fill="both", expand=True)

folder_label = Label(main_frame, text="Selected Folder: None", bg="lightgrey", anchor="w")
folder_label.pack(pady=(10, 0), fill="x")

# --- Listbox frame ---
listbox_frame = tkinter.Frame(main_frame, bg="lightgrey")
listbox_frame.pack(side="left", fill="both", expand=True, padx=(40,10), pady=20)

file_listbox = Listbox(listbox_frame, width=1, font=("Consolas", 13))
file_listbox.pack(fill="both", expand=True)

scan_status = {}

def list_folder_contents(Folder): 
    file_listbox.delete(0, tkinter.END)
    try:
        for item in os.listdir(Folder):
            mark = " ✅" if scan_status.get(os.path.join(Folder, item)) == "clean" else ""
            file_listbox.insert(tkinter.END, item + mark)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open folder: {e}")
        
def scan_with_defender():
    selected = file_listbox.curselection()
    if not selected or not selected_folder:
        messagebox.showwarning("No Selection", "Please select a file to scan.")
        return

    item_name = file_listbox.get(selected[0]).replace(" ✅", "")
    path = os.path.join(selected_folder, item_name)

    if not os.path.isfile(path):
        messagebox.showwarning("Not a file", "Please select a file, not a folder.")
        return

    try:
        powershell_cmd = f'powershell -Command "Start-MpScan -ScanPath \"{path}\""'
        result = subprocess.run(powershell_cmd, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            scan_status[path] = "clean"
            messagebox.showinfo("Scan Result", f"{item_name}: Clean ✅")
        else:
            scan_status[path] = "infected"
            messagebox.showwarning("Scan Result", f"{item_name}: Threats found! ⚠️\n{result.stdout}")

        list_folder_contents(selected_folder)

    except Exception as e:
        messagebox.showerror("Scan Error", f"Error: {e}")

def open_database_viewer():
    global selected_folder 
    entered_password = simpledialog.askstring("Password Required", "Enter password:", show="*") 
    if entered_password == CORRECT_PASSWORD:
        folder_path = filedialog.askdirectory(title="Select Database Folder")
        if folder_path:
            selected_folder = folder_path
            folder_label.config(text=f"Selected Folder: {selected_folder}")
            list_folder_contents(selected_folder)
        else:
            print("No folder selected.")
    else:
        messagebox.showerror("Access Denied", "Incorrect password.")
        return

def netdiscover(): 
    try:
        proc = subprocess.run(["netdiscover", "-r", "-s"], capture_output=True, text=True)
        output = proc.stdout or proc.stderr or "No output"
        messagebox.showinfo("Netdiscover Result", output)
    except FileNotFoundError:
        messagebox.showerror("Error", "netdiscover not found. Install netdiscover or add it to PATH.")
    except Exception as e:
        messagebox.showerror("Error", f"Cannot run netdiscover: {e}")

def create_folder(): 
    if selected_folder: 
        name = simpledialog.askstring("New Folder", "Enter folder name:") 
        if name: 
            path = os.path.join(selected_folder, name) 
            try: 
                os.makedirs(path) 
                list_folder_contents(selected_folder)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def create_file(): 
    if selected_folder: 
        name = simpledialog.askstring("New File", "Enter file name:") 
        if name: 
            path = os.path.join(selected_folder, name) 
            try: 
                with open(path, 'w') as f: 
                    f.write("")  
                list_folder_contents(selected_folder) 
            except Exception as e: 
                messagebox.showerror("Error", f"Cannot create file: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.") 

def open_file(event):
    selection = file_listbox.curselection()
    if selection:
        item_name = file_listbox.get(selection[0]).replace(" ✅", "")
        item_path = os.path.join(selected_folder, item_name)
        if os.path.isdir(item_path):
            list_folder_contents(item_path)
        else:
            try:
                if os.name == 'nt':  # Вінда
                    os.startfile(item_path)
                elif os.name == 'posix':  # ДЛя МакОС і Лінукса
                    subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', item_path])
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")

def delete_item(): 
    selected = file_listbox.curselection() 
    if selected and selected_folder: 
        item_name = file_listbox.get(selected[0]) 
        path = os.path.join(selected_folder, item_name) 
        try: 
            if os.path.isdir(path): 
                shutil.rmtree(path) 
            else: 
                os.remove(path) 
            list_folder_contents(selected_folder) 
        except Exception as e: 
            messagebox.showerror("Error", f"Cannot delete item: {e}") 
    else: 
        messagebox.showwarning("No Selection", "Please select an item to delete.") 

def see_zip(): 
    if selected_folder:
        name = simpledialog.askstring("Zip File", "Enter zip file name:")
        if name:
            path = os.path.join(selected_folder, name)
            if os.path.isfile(path) and zipfile.is_zipfile(path):
                try:
                    with zipfile.ZipFile(path, 'r') as zip_ref:
                        # namelist() работает даже если архив с паролем
                        zip_contents = zip_ref.namelist()
                    messagebox.showinfo("Zip Contents", "\n".join(zip_contents))
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot read zip file: {e}")
            else:
                messagebox.showerror("Error", "Selected file is not a valid zip file.")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy() 

def backup_folder():
    if selected_folder:
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        backup_path = os.path.join(selected_folder, backup_name)
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root_dir, dirs, files in os.walk(selected_folder):
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        arcname = os.path.relpath(file_path, selected_folder)
                        zipf.write(file_path, arcname)
            messagebox.showinfo("Backup Created", f"Backup created at {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create backup: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def change_directory():
    global selected_folder 
    folder_path = filedialog.askdirectory(title="Select Folder") 
    if folder_path: 
        selected_folder = folder_path 
        folder_label.config(text=f"Selected Folder: {selected_folder}") 
        list_folder_contents(selected_folder) 
    else: 
        print("No folder selected.") 

def import_csv():
    if selected_folder:
        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                messagebox.showinfo("CSV Data", df.to_string())
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read CSV file: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def import_json():
    if selected_folder:
        file_path = filedialog.askopenfilename(title="Select JSON File", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                messagebox.showinfo("JSON Data", json.dumps(data, indent=4))
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read JSON file: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def import_xml():
    if selected_folder:
        file_path = filedialog.askopenfilename(title="Select XML File", filetypes=[("XML files", "*.xml")])
        if file_path:
            try:
                tree = ET.parse(file_path)
                root_elem = tree.getroot()
                xml_str = ET.tostring(root_elem, encoding='unicode')
                messagebox.showinfo("XML Data", xml_str)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read XML file: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.") 

def import_sqite3(): 
    if selected_folder:
        file_path = filedialog.askopenfilename(title="Select SQLite File", filetypes=[("SQLite files", "*.sqlite;*.db")])
        if file_path:
            try:
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                table_names = [t[0] for t in tables]
                msg = "Tables in DB:\n" + "\n".join(table_names)
                messagebox.showinfo("SQLite file", msg)
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read SQLite file: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def wireshark(): 
    try:
        subprocess.Popen(["wireshark"])
    except FileNotFoundError:
        messagebox.showerror("Error", "Wireshark not found. Install Wireshark or add it to PATH.")
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open Wireshark: {e}")

def import_nmap(): 
    if selected_folder:
        ip = simpledialog.askstring("Nmap Scan", "Enter IP or host to scan:")
        if not ip:
            messagebox.showwarning("No IP", "No IP or host provided.")
            return
        port = simpledialog.askstring("Nmap Scan", "Enter port (optional):")
        try:
            cmd = ["nmap"]
            if port:
                cmd += ["-p", port]
            cmd.append(ip)
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout or result.stderr or "No output"
            messagebox.showinfo("Nmap Result", output)
        except FileNotFoundError:
            messagebox.showerror("Error", "nmap not found. Install nmap or add it to PATH.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot run nmap: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def import_openxyle(): 
    if selected_folder:
        file_path = filedialog.askopenfilename(title="Select openxyle file", filetypes=[("Openxyle files", "*.xle")])
        if file_path:
            try:
                tree = ET.parse(file_path)
                root_elem = tree.getroot()
                xyle_str = ET.tostring(root_elem, encoding='unicode')
                messagebox.showinfo("openxyle file", xyle_str)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read openxyle file: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.") 

button_frame = tkinter.Frame(main_frame, bg="lightgrey")
button_frame.pack(side="right", fill="y", padx=40, pady=20)

def add_hover_effect(btn, color_on='#e0e0e0', color_off='#f5f5f5'):
    def on_enter(e): btn['background'] = color_on
    def on_leave(e): btn['background'] = color_off
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def create_zip_file(): 
    if selected_folder: 
        file_path = filedialog,create_file(title="Create ZIP archive", filetypes=[("Open ZIP archive", "*.zip")]) 
        if file_path: 
            try:
                with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf: 
                    for root_dir, dirs, files in os.walk(selected_folder): 
                        for file in files: 
                            file_path = os.path.join(root_dir, file) 
                            arcname = os.path.relpath(file_path, selected_folder) 
                            zipf.write(file_path, arcname) 
                            messagebox.showinfo("Success", f"ZIP archive created at {file_path}") 
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create ZIP file: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.") 

def extract_zip_file(): 
    if selected_folder: 
        file_path = filedialog.askopenfilename(title="Select ZIP archive", filetypes=[("Open ZIP archive", "*.zip")]) 
        if file_path: 
            try:
                with zipfile.ZipFile(file_path, 'r') as zipf: 
                    zipf.extractall(selected_folder) 
                    messagebox.showinfo("Success", f"ZIP archive extracted to {selected_folder}") 
            except Exception as e:
                messagebox.showerror("Error", f"Cannot extract ZIP file: {e}")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def view_file_details():
    if selected_folder:
        selected = file_listbox.curselection()
        if selected:
            item_name = file_listbox.get(selected[0]).replace(" ✅", "")
            path = os.path.join(selected_folder, item_name)
            try:
                stats = os.stat(path)
                details = f"Path: {path}\nSize: {stats.st_size} bytes\nCreated: {datetime.fromtimestamp(stats.st_ctime)}\nModified: {datetime.fromtimestamp(stats.st_mtime)}"
                messagebox.showinfo("File Details", details)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot get file details: {e}")
        else:
            messagebox.showwarning("No Selection", "Please select a file or folder.") 

def scan_wifi(): 
    messagebox.showinfo("Wifi Scan") 
    os.path.exists("C:/Windows/System32/wlanapi.dll")
    os.system("netsh wlan show profiles")
    os.system("netsh wlan show profile name=* key=clear")
    os.system("netsh wlan export profile folder=C:\\ key=clear")
    messagebox.showinfo("Wifi Scan", "Wifi scan completed. Check console output.")
    file_listbox.bind("<Double-1>", open_file)
    file_listbox.bind("<Double-2>", open_file)
    file_listbox.bind("<")

# --- Кнопки для роботи з папками/файлами ---
lbl_files = Label(button_frame, text="Файли та папки", bg="lightgrey", font=("Arial", 11, "bold"))
lbl_files.pack(pady=(0, 5), anchor="w")
open_button = Button(button_frame, text="Відкрити базу", command=open_database_viewer, bg="#f5f5f5")
open_button.pack(fill="x", pady=2)
add_hover_effect(open_button)
create_folder_button = Button(button_frame, text="Створити папку", command=create_folder, bg="#f5f5f5")
create_folder_button.pack(fill="x", pady=2)
add_hover_effect(create_folder_button)
create_file_button = Button(button_frame, text="Створити файл", command=create_file, bg="#f5f5f5")
create_file_button.pack(fill="x", pady=2)
add_hover_effect(create_file_button)
delete_button = Button(button_frame, text="Видалити", command=delete_item, bg="#f5f5f5")
delete_button.pack(fill="x", pady=2)
add_hover_effect(delete_button)
see_zip_button = Button(button_frame, text="Вміст ZIP", command=see_zip, bg="#f5f5f5")
see_zip_button.pack(fill="x", pady=2)
add_hover_effect(see_zip_button)
backup_folder_button = Button(button_frame, text="Backup папки", command=backup_folder, bg="#f5f5f5")
backup_folder_button.pack(fill="x", pady=2)
add_hover_effect(backup_folder_button)
change_directory_button = Button(button_frame, text="Змінити директорію", command=change_directory, bg="#f5f5f5")
change_directory_button.pack(fill="x", pady=2)
add_hover_effect(change_directory_button) 
view_details_button = Button(button_frame, text="Деталі файлу", command=view_file_details, bg="#f5f5f5")
view_details_button.pack(fill="x", pady=2)
add_hover_effect(view_details_button)
create_zip_button = Button(button_frame, text="Створити ZIP", command=create_zip_file, bg="#f5f5f5")
create_zip_button.pack(fill="x", pady=2)
add_hover_effect(create_zip_button)
extract_zip_button = Button(button_frame, text="Розпакувати ZIP", command=extract_zip_file, bg="#f5f5f5")
extract_zip_button.pack(fill="x", pady=2)
add_hover_effect(extract_zip_button)
wireshark_button = Button(button_frame, text="Відкрити Wireshark", command=wireshark, bg="#f5f5f5")
wireshark_button.pack(fill="x", pady=2)
add_hover_effect(wireshark_button)

# --- імпорт ---
lbl_import = Label(button_frame, text="Імпорт даних", bg="lightgrey", font=("Arial", 11, "bold"))
lbl_import.pack(pady=(15, 5), anchor="w")
import_csv_button = Button(button_frame, text="Імпорт CSV", command=import_csv, bg="#f5f5f5")
import_csv_button.pack(fill="x", pady=2)
add_hover_effect(import_csv_button)
import_json_button = Button(button_frame, text="Імпорт JSON", command=import_json, bg="#f5f5f5")
import_json_button.pack(fill="x", pady=2)
add_hover_effect(import_json_button)
import_xml_button = Button(button_frame, text="Імпорт XML", command=import_xml, bg="#f5f5f5")
import_xml_button.pack(fill="x", pady=2)
add_hover_effect(import_xml_button)
import_sqite3_button = Button(button_frame, text="Імпорт SQLite", command=import_sqite3, bg="#f5f5f5")
import_sqite3_button.pack(fill="x", pady=2)
add_hover_effect(import_sqite3_button)
import_openxyle_button = Button(button_frame, text="Перевірити openxyle", command=import_openxyle, bg="#f5f5f5")
import_openxyle_button.pack(fill="x", pady=2)
add_hover_effect(import_openxyle_button)

# --- сканування ---
lbl_scan = Label(button_frame, text="Безпека", bg="lightgrey", font=("Arial", 11, "bold"))
lbl_scan.pack(pady=(15, 5), anchor="w")
scan_button = Button(button_frame, text="Проверка на вірус (Defender)", command=scan_with_defender, bg="#f5f5f5")
scan_button.pack(fill="x", pady=2)
add_hover_effect(scan_button) 
scan_wifi_button = Button(button_frame, text="Сканування Wifi", command=scan_wifi, bg="#f5f5f5")
scan_wifi_button.pack(fill="x", pady=2)
add_hover_effect(scan_wifi_button) 
nmap_button = Button(button_frame, text="Сканування мережі (Nmap)", command=import_nmap, bg="#f5f5f5")
nmap_button.pack(fill="x", pady=2)
add_hover_effect(nmap_button)
netdiscover_button = Button(button_frame, text="Сканування портів Netdiscover", command=netdiscover, bg="#f5f5f5")
netdiscover_button.pack(fill="x", pady=2)
add_hover_effect(netdiscover_button)

# --- Обробка закриття вік
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

root.mainloop()