import google.generativeai as genai
import os
from dotenv import load_dotenv
from docx import Document
from datetime import datetime
import re
from notion_integration import add_task_to_notion

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Ошибка: GEMINI_API_KEY не установлен.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_text(text: str):
    prompt = (
        "Ты ИИ-секретарь. Проанализируй текст встречи и выдели:\n"
        "1. Краткое резюме встречи.\n"
        "2. Хронологию обсуждаемых тем (таймлайн, по минутам).\n"
        "3. Список задач (action items).\n\n"
        "Формат ответа:\n"
        "Резюме:\n[текст резюме]\n\n"
        "Таймлайн:\n- [время] - [тема]\n\n"
        "Задачи:\n- [задача]\n\n"
        "Текст встречи:\n" + text
    )

    try:
        response = model.generate_content(prompt)
        analysis = response.text

        summary = re.search(r'Резюме:\s*(.*?)\s*Таймлайн:', analysis, re.DOTALL).group(1).strip()
        timeline = re.search(r'Таймлайн:\s*(.*?)\s*Задачи:', analysis, re.DOTALL).group(1).strip()
        tasks = re.search(r'Задачи:\s*(.*)', analysis, re.DOTALL).group(1).strip().split('\n')

        return summary, timeline, tasks
    except Exception as e:
        print(f"Произошла ошибка при анализе текста: {e}")
        return None, None, None

def save_to_docx(filename_base: str, summary: str, timeline: str, tasks: list, raw_text: str):
    doc = Document()
    doc.add_heading("Отчёт по встрече", level=0)
    doc.add_paragraph(f"Дата и время: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    doc.add_heading("🔹 Резюме:", level=1)
    doc.add_paragraph(summary)
    doc.add_heading("🔹 Таймлайн:", level=1)
    doc.add_paragraph(timeline)
    doc.add_heading("🔹 Задачи:", level=1)
    for task in tasks:
        doc.add_paragraph(task, style='List Bullet')
    doc.add_heading("🔹 Полная стенограмма:", level=1)
    doc.add_paragraph(raw_text)

    output_path = os.path.join("recordings", f"{filename_base}.docx")
    doc.save(output_path)
    print(f"[✔] Word-файл сохранён: {output_path}")

    for task in tasks:
        add_task_to_notion(task.strip('- ').strip())