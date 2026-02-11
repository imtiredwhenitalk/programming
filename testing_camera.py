import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk

class PersonDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Детекція людей")
        self.root.geometry("800x650")
        self.root.configure(bg="#2b2b2b")

        self.camera = None
        self.running = False
        self.people_count = 0

        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(pady=10)

        self.status_label = tk.Label(
            self.root, text="Статус: очікування", fg="yellow", bg="#2b2b2b"
        )
        self.status_label.pack()

        self.count_label = tk.Label(
            self.root, text="Бачу людей: 0", fg="lime", bg="#2b2b2b", font=("Arial", 14)
        )
        self.count_label.pack(pady=5)

        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="Запуск", bg="green", fg="white",
            command=self.start_camera, width=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="Стоп", bg="red", fg="white",
            command=self.stop_camera, width=15
        ).pack(side=tk.LEFT, padx=5)

    def start_camera(self):
        if self.running:
            return

        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not self.camera.isOpened():
            messagebox.showerror("Помилка", "Камера не знайдена")
            return

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.running = True
        self.status_label.config(text="Статус: камера працює", fg="lime")
        self.update_frame()

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.camera.read()
        if not ret:
            self.stop_camera()
            return

        boxes, _ = self.hog.detectMultiScale(
            frame, winStride=(4, 4), padding=(8, 8), scale=1.05
        )

        self.people_count = len(boxes)

        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame, "ЛЮДИНА", (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

        self.count_label.config(text=f"Бачу людей: {self.people_count}")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(img)

        self.video_label.imgtk = img
        self.video_label.config(image=img)

        self.root.after(30, self.update_frame)

    def stop_camera(self):
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None

        self.video_label.config(image="")
        self.status_label.config(text="Статус: зупинено", fg="orange")
        self.count_label.config(text="Бачу людей: 0")

    def on_closing(self):
        self.stop_camera()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = PersonDetectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
