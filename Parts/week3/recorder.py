import sounddevice as sd
import soundfile as sf
import threading
import datetime
import whisper
import os
import queue
from analyzer import analyze_text, save_to_docx
from notion_integration import add_task_to_notion
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
from tkinter import messagebox
from pydub import AudioSegment

load_dotenv()

class Recorder:
    def __init__(self):
        self.SAVE_DIR = "recordings"
        os.makedirs(self.SAVE_DIR, exist_ok=True)

        self.SAMPLE_RATE = 16000
        self.CHANNELS = 1
        self.q = queue.Queue()

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Ошибка: GEMINI_API_KEY не установлен.")
            exit(1)
        configure(api_key=api_key)
        self.model = GenerativeModel("gemini-1.5-flash")

        self.is_recording = False
        self.thread = None
        self.file_path = None
        self.transcript_path = None

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(indata.copy())

    def start(self, status_label):
        self.is_recording = True
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.file_path = os.path.join(self.SAVE_DIR, f"meeting_{timestamp}.wav")

        def _record():
            try:
                with sf.SoundFile(self.file_path, mode='w', samplerate=self.SAMPLE_RATE,
                                  channels=self.CHANNELS) as wav_file:
                    with sd.InputStream(samplerate=self.SAMPLE_RATE, channels=self.CHANNELS,
                                        dtype='float32', callback=self.audio_callback):
                        while self.is_recording:
                            wav_file.write(self.q.get())
            except Exception as e:
                print(f"Ошибка при записи аудио: {e}")
                status_label.config(text="Статус: Ошибка записи", fg="red")
                messagebox.showerror("Ошибка", f"Не удалось записать аудио: {str(e)}")

        self.thread = threading.Thread(target=_record)
        self.thread.start()
        status_label.config(text="Статус: Запись...", fg="green")

    def stop(self, status_label):
        self.is_recording = False
        self.thread.join()
        status_label.config(text="Статус: Транскрибирование...", fg="blue")

        if not os.path.exists(self.file_path):
            status_label.config(text="Статус: Ошибка", fg="red")
            messagebox.showerror("Ошибка", f"Аудиофайл не найден: {self.file_path}")
            return

        try:
            audio = AudioSegment.from_file(self.file_path)
            audio = audio.set_channels(1).set_frame_rate(self.SAMPLE_RATE).set_sample_width(2)
            converted_path = os.path.join(self.SAVE_DIR, "temp_converted.wav")
            audio.export(converted_path, format="wav")

            model = whisper.load_model("medium")
            result = model.transcribe(converted_path, language="ru")
            transcript_with_timestamps = ""
            for segment in result["segments"]:
                start_time = segment["start"]
                text = segment["text"]
                transcript_with_timestamps += f"[{start_time:.2f}] {text}\n"

            self.transcript_path = os.path.join(self.SAVE_DIR, f"{os.path.splitext(os.path.basename(self.file_path))[0]}_transcript.txt")
            with open(self.transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript_with_timestamps)

            os.remove(converted_path)

            messagebox.showinfo("Готово", f"Файлы сохранены:\n{self.file_path}\n{self.transcript_path}")

            self.process_transcript(transcript_with_timestamps, os.path.splitext(os.path.basename(self.file_path))[0])
            status_label.config(text="Статус: Обработка завершена", fg="green")
        except Exception as e:
            status_label.config(text="Статус: Ошибка", fg="red")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def transcribe_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        if not file_path.endswith('.wav'):
            raise ValueError("Файл должен быть в формате WAV")

        try:
            audio = AudioSegment.from_file(file_path)
            audio = audio.set_channels(1).set_frame_rate(self.SAMPLE_RATE).set_sample_width(2)
            converted_path = os.path.join(self.SAVE_DIR, "temp_converted.wav")
            audio.export(converted_path, format="wav")

            model = whisper.load_model("small")
            result = model.transcribe(converted_path, language="ru")
            transcript_with_timestamps = ""
            for segment in result["segments"]:
                start_time = segment["start"]
                text = segment["text"]
                transcript_with_timestamps += f"[{start_time:.2f}] {text}\n"

            transcript_path = os.path.join(self.SAVE_DIR,
                                          f"{os.path.splitext(os.path.basename(file_path))[0]}_transcript.txt")
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript_with_timestamps)

            os.remove(converted_path)
            return transcript_with_timestamps
        except Exception as e:
            print(f"Ошибка при транскрибировании файла: {e}")
            return None

    def analyze_transcript(self, transcript):
        return analyze_text(transcript)

    def save_to_docx(self, filename_base, summary, timeline, tasks, transcript):
        save_to_docx(filename_base, summary, timeline, tasks, transcript)

    def send_to_notion(self, tasks):
        for task in tasks:
            add_task_to_notion(task.strip('- ').strip())

    def process_transcript(self, transcript, filename_base):
        summary, timeline, tasks = self.analyze_transcript(transcript)
        if summary and timeline and tasks:
            self.save_to_docx(filename_base, summary, timeline, tasks, transcript)
            self.send_to_notion(tasks)