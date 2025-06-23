from google.generativeai import GenerativeModel, configure
import os
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Ошибка: переменная окружения GEMINI_API_KEY не установлена.")
    exit(1)


configure(api_key=api_key)

model = GenerativeModel("gemini-1.5-flash")


def send_message(message):

    try:
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None



print("Введите сообщение и нажмите Enter. Введите 'exit' для выхода.")

try:
    while True:
        user_input = input("Вы: ")
        if user_input.lower() == "exit":
            break
        response = send_message(user_input)
        if response:
            print("Gemini:", response)
except KeyboardInterrupt:
    print("\nВыход...")