import sounddevice as sd
import soundfile as sf
import threading
import tkinter as tk
from tkinter import messagebox
import datetime
import os

SAVE_DIR = "recordings"
os.makedirs('L:\RecordingSaves', exist_ok=True)

is_recording = False
recording_thread = None
file_path = None

SAMPLE_RATE = 44100
CHANNELS = 2


def start_recording():
    global is_recording, recording_thread, file_path

    if is_recording:
        messagebox.showinfo("Инфо", "Уже идёт запись!")
        return

    is_recording = True
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(SAVE_DIR, f"meeting_{timestamp}.wav")

    def _record():
        with sf.SoundFile(file_path, mode='w', samplerate=SAMPLE_RATE, channels=CHANNELS) as file:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS) as stream:
                while is_recording:
                    data = stream.read(1024)[0]
                    file.write(data)

    recording_thread = threading.Thread(target=_record)
    recording_thread.start()
    status_label.config(text="Статус: Запись...", fg="green")


def stop_recording():
    global is_recording

    if not is_recording:
        messagebox.showinfo("Инфо", "Запись не ведётся.")
        return

    is_recording = False
    recording_thread.join()
    status_label.config(text="Статус: Остановлено", fg="red")
    messagebox.showinfo("Готово", f"Файл сохранён: {file_path}")


root = tk.Tk()
root.title("Запись экрана")
root.geometry("300x180")
root.resizable(False, False)

record_btn = tk.Button(root, text="Начать запись", command=start_recording, font=("Arial", 12), width=20)
record_btn.pack(pady=15)

stop_btn = tk.Button(root, text="Остановить запись", command=stop_recording, font=("Arial", 12), width=20)
stop_btn.pack(pady=5)

status_label = tk.Label(root, text="Статус: Ожидание", font=("Arial", 10))
status_label.pack(pady=10)

root.mainloop()
