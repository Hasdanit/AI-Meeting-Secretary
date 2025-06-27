# main.py — интерфейс и управление программой

import tkinter as tk
from tkinter import messagebox
from recorder import Recorder

# Создаём экземпляр рекордера
recorder = Recorder()

# Интерфейс
root = tk.Tk()
root.title("ИИ-Секретарь - Неделя 2")
root.geometry("320x200")
root.resizable(False, False)

status_label = tk.Label(root, text="Статус: Ожидание", font=("Arial", 10))
status_label.pack(pady=10)


def start_recording():
    if recorder.is_recording:
        messagebox.showinfo("Инфо", "Уже идёт запись!")
        return
    recorder.start(status_label)


def stop_recording():
    if not recorder.is_recording:
        messagebox.showinfo("Инфо", "Запись не ведётся.")
        return
    recorder.stop(status_label)

record_btn = tk.Button(root, text="Начать запись", command=start_recording, font=("Arial", 12), width=25)
record_btn.pack(pady=15)

stop_btn = tk.Button(root, text="Остановить запись", command=stop_recording, font=("Arial", 12), width=25)
stop_btn.pack(pady=5)

root.mainloop()
