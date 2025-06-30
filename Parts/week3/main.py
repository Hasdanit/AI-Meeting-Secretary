import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from recorder import Recorder
import threading

# Создаём экземпляр рекордера
recorder = Recorder()

# Интерфейс
root = tk.Tk()
root.title("ИИ-Секретарь")
root.geometry("500x400")
root.resizable(False, False)

# Вкладки
notebook = tk.ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Вкладка записи
record_frame = tk.Frame(notebook)
notebook.add(record_frame, text="Запись")

status_label = tk.Label(record_frame, text="Статус: Ожидание", font=("Arial", 10))
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

record_btn = tk.Button(record_frame, text="Начать запись", command=start_recording, font=("Arial", 12), width=25)
record_btn.pack(pady=15)

stop_btn = tk.Button(record_frame, text="Остановить запись", command=stop_recording, font=("Arial", 12), width=25)
stop_btn.pack(pady=5)

# Вкладка чата
chat_frame = tk.Frame(notebook)
notebook.add(chat_frame, text="Чат с ИИ")

chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, width=60, height=15)
chat_display.pack(pady=10)

input_field = tk.Entry(chat_frame, width=50)
input_field.pack(side=tk.LEFT, padx=5)

def send_message():
    user_message = input_field.get()
    if user_message.lower() == "exit":
        root.quit()
    chat_display.insert(tk.END, f"Вы: {user_message}\n")
    input_field.delete(0, tk.END)

    def get_response():
        response = recorder.model.generate_content(user_message).text
        chat_display.insert(tk.END, f"Gemini: {response}\n")

    threading.Thread(target=get_response).start()

send_btn = tk.Button(chat_frame, text="Отправить", command=send_message)
send_btn.pack(side=tk.LEFT)

root.mainloop()