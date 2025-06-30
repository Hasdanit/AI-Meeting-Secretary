import requests
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_KEY or not DATABASE_ID:
    raise ValueError("Ошибка: NOTION_API_KEY или NOTION_DATABASE_ID не установлены.")

def add_task_to_notion(task: str):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Secretary": {
                "title": [
                    {
                        "text": {
                            "content": task
                        }
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"[✔] Задача '{task}' добавлена в Notion.")
    else:
        print(f"[!] Ошибка при добавлении задачи: {response.text}")