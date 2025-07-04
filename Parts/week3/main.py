import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import os
import webbrowser

from dotenv import load_dotenv

from recorder import Recorder
import threading

load_dotenv()

DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

recorder = Recorder()

root = tk.Tk()
root.title("ИИ-Секретарь")
root.geometry("500x400")
root.resizable(False, False)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

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

def analyze_audio_file():
    file_path = filedialog.askopenfilename(
        title="Выберите WAV-файл",
        filetypes=[("WAV files", "*.wav")]
    )
    if not file_path:
        return

    # Окно с опциями обработки
    options_window = tk.Toplevel(root)
    options_window.title("Опции анализа")
    options_window.geometry("300x250")
    options_window.transient(root)
    options_window.grab_set()

    tk.Label(options_window, text="Выберите действия:", font=("Arial", 10)).pack(pady=10)

    transcribe_var = tk.BooleanVar(value=True)
    analyze_var = tk.BooleanVar(value=True)
    docx_var = tk.BooleanVar(value=True)
    notion_var = tk.BooleanVar(value=True)

    tk.Checkbutton(options_window, text="Транскрибировать аудио", variable=transcribe_var).pack(anchor="w", padx=10)
    tk.Checkbutton(options_window, text="Анализировать текст", variable=analyze_var).pack(anchor="w", padx=10)
    tk.Checkbutton(options_window, text="Создать DOCX", variable=docx_var).pack(anchor="w", padx=10)
    tk.Checkbutton(options_window, text="Отправить задачи в Notion", variable=notion_var).pack(anchor="w", padx=10)

    def process_file():
        options_window.destroy()
        status_label.config(text="Статус: Обработка файла...", fg="blue")
        threading.Thread(target=run_processing, args=(file_path, transcribe_var.get(), analyze_var.get(), docx_var.get(), notion_var.get())).start()

    def run_processing(file_path, transcribe, analyze, save_docx, send_notion):
        try:
            transcript = None
            if transcribe:
                transcript = recorder.transcribe_file(file_path)
                if not transcript:
                    raise ValueError("Не удалось распознать текст из аудио")
            else:
                transcript_path = os.path.join("recordings", f"{os.path.splitext(os.path.basename(file_path))[0]}_transcript.txt")
                if os.path.exists(transcript_path):
                    with open(transcript_path, "r", encoding="utf-8") as f:
                        transcript = f.read()
                else:
                    raise ValueError("Транскрипция не выбрана, и текстовый файл не найден")

            summary, timeline, tasks = None, None, None
            if analyze:
                summary, timeline, tasks = recorder.analyze_transcript(transcript)
                if not (summary and timeline and tasks):
                    raise ValueError("Не удалось проанализировать текст")

            filename_base = os.path.splitext(os.path.basename(file_path))[0]
            if save_docx and summary and timeline and tasks:
                recorder.save_to_docx(filename_base, summary, timeline, tasks, transcript)

            if send_notion and tasks:
                recorder.send_to_notion(tasks)

            status_label.config(text="Статус: Обработка завершена", fg="green")
            messagebox.showinfo("Успех", f"Файлы сохранены в папке 'recordings'\nТранскрипт: {filename_base}_transcript.txt\nDOCX: {filename_base}.docx")
        except Exception as e:
            status_label.config(text="Статус: Ошибка", fg="red")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    tk.Button(options_window, text="Начать обработку", command=process_file, font=("Arial", 10)).pack(pady=15)

def open_folder_and_notion():
    recordings_path = os.path.join(os.getcwd(), "recordings")
    if os.path.exists(recordings_path):
        os.startfile(recordings_path)
    else:
        messagebox.showerror("Ошибка", "Папка 'recordings' не найдена")

    notion_url = "https://www.notion.so/20fc4148c5e48036af08d14b6b430e0f?v=222c4148c5e480c78b09000c84c8855d"
    webbrowser.open(notion_url)

record_btn = tk.Button(record_frame, text="Начать запись", command=start_recording, font=("Arial", 12), width=25)
record_btn.pack(pady=15)

stop_btn = tk.Button(record_frame, text="Остановить запись", command=stop_recording, font=("Arial", 12), width=25)
stop_btn.pack(pady=5)

analyze_btn = tk.Button(record_frame, text="Анализировать аудиофайл", command=analyze_audio_file, font=("Arial", 12), width=25)
analyze_btn.pack(pady=5)

open_btn = tk.Button(record_frame, text="Открыть папку и Notion", command=open_folder_and_notion, font=("Arial", 12), width=25)
open_btn.pack(pady=5)

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