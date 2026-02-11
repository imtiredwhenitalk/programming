import tkinter as tk
from tkinter import ttk, Label, Button, Tk, filedialog, simpledialog, messagebox, Listbox, Entry
import os
import zipfile

CORRECT_PASSWORD = "123321"

root = Tk()
root.geometry("800x600")
root.title("Database Viewer")
root.configure(bg="lightgrey")

selected_folder = ""

def list_folder_contents(folder):
    file_listbox.delete(0, tk.END)
    try:
        for item in os.listdir(folder):
            file_listbox.insert(tk.END, item)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open folder: {e}")

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
        root.quit()

def sql_query(): 
    if selected_folder: 
        query = simpledialog.askstring("SQL Query", "Enter your SQL query:")
        if query:
            messagebox.showinfo("Query Result", f"Executed query: {query}\n(Note: This is a placeholder, actual SQL execution not implemented.)")
    else:
        messagebox.showwarning("No Folder", "Please select a folder first.")

def create_VM():
    messagebox.showinfo("Create VM", "This is a placeholder for VM creation functionality.")
    
    virtual_machine_name = simpledialog.askstring("VM Name", "Enter the name for the new virtual machine:")
    if virtual_machine_name:
        messagebox.showinfo("VM Created", f"Virtual machine '{virtual_machine_name}' created successfully (placeholder).")
    os.system("start https://www.virtualbox.org/")
    


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

def open_item(event):
    selection = file_listbox.curselection()
    if selection:
        item_name = file_listbox.get(selection[0])
        item_path = os.path.join(selected_folder, item_name)
        if os.path.isdir(item_path):
            list_folder_contents(item_path)
        elif item_path.endswith(".zip"):
            try:
                with zipfile.ZipFile(item_path, 'r') as zip_ref:
                    extract_path = os.path.join(selected_folder, "unzipped_" + os.path.splitext(item_name)[0])
                    zip_ref.extractall(extract_path)
                    messagebox.showinfo("Zip Extracted", f"Extracted to: {extract_path}")
                    list_folder_contents(extract_path)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot extract zip: {e}")
        else:
            try:
                os.system(f'notepad "{item_path}"')  
            except:
                messagebox.showwarning("Warning", "Cannot open this file.")

def closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

def show_directory(): 
    directory = os.getcwd()
    messagebox.showinfo("Current Directory", f"Current directory: {directory}") 

Label(root, text="Database Viewer", font=("Times New Roman", 14, "bold"), bg="lightgrey").place(relx=0.5, y=20, anchor="n")

Button(root, text='Exit', command=closing).place(x=10, y=10)
Button(root, text='Open Database Viewer', command=open_database_viewer).place(relx=0.5, rely=1.0, y=-50, anchor="s")
Button(root, text='New Folder', command=create_folder).place(x=120, y=10)
Button(root, text='New File', command=create_file).place(x=220, y=10)

folder_label = Label(root, text="No folder selected", bg="lightgrey")
folder_label.place(relx=0.5, y=60, anchor="n")

file_listbox = Listbox(root, width=100, height=25)
file_listbox.place(relx=0.5, rely=0.15, anchor="n")
file_listbox.bind('<Double-Button-1>', open_item)

root.mainloop()

