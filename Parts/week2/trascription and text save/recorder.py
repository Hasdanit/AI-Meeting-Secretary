# recorder.py

import sounddevice as sd
import soundfile as sf
import threading
import datetime
import os
import queue
import json
from vosk import Model, KaldiRecognizer


class Recorder:
    def __init__(self):
        self.SAVE_DIR = "recordings"
        os.makedirs(self.SAVE_DIR, exist_ok=True)

        self.SAMPLE_RATE = 16000
        self.CHANNELS = 1
        self.q = queue.Queue()

        try:
            self.model = Model("vosk-model-small-ru-0.22")
        except Exception as e:
            print("Ошибка загрузки модели Vosk:", e)
            exit(1)

        self.is_recording = False
        self.thread = None
        self.file_path = None
        self.transcript_path = None

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(bytes(indata))

    def start(self, status_label):
        self.is_recording = True
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.file_path = os.path.join(self.SAVE_DIR, f"meeting_{timestamp}.wav")
        self.transcript_path = os.path.join(self.SAVE_DIR, f"meeting_{timestamp}.txt")

        def _record():
            rec = KaldiRecognizer(self.model, self.SAMPLE_RATE)
            rec.SetWords(True)

            with sf.SoundFile(self.file_path, mode='w', samplerate=self.SAMPLE_RATE, channels=self.CHANNELS) as wav_file:
                with sd.RawInputStream(samplerate=self.SAMPLE_RATE, blocksize=8000, dtype='int16',
                                       channels=self.CHANNELS, callback=self.audio_callback):
                    with open(self.transcript_path, 'w', encoding='utf-8') as transcript_file:
                        while self.is_recording:
                            data = self.q.get()
                            wav_file.buffer_write(data, dtype='int16')
                            if rec.AcceptWaveform(data):
                                result = json.loads(rec.Result())
                                transcript_file.write(result.get('text', '') + '\n')
                        final_result = json.loads(rec.FinalResult())
                        transcript_file.write(final_result.get('text', '') + '\n')

        self.thread = threading.Thread(target=_record)
        self.thread.start()
        status_label.config(text="Статус: Запись и распознавание...", fg="green")

    def stop(self, status_label):
        self.is_recording = False
        self.thread.join()
        status_label.config(text="Статус: Остановлено", fg="red")

        from tkinter import messagebox
        messagebox.showinfo("Готово", f"Файлы сохранены:\n{self.file_path}\n{self.transcript_path}")
