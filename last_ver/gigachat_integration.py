# Импорты
from functools import lru_cache
import time
from gigachat import GigaChat
from gigachat.exceptions import ResponseError, AuthenticationError
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


# Класс для управления подключением
class GigaChatManager:
    def __init__(self):
        self.client = None
        self.update_token()

    def update_token(self):
        try:
            self.client = GigaChat(
                credentials=os.getenv("GIGACHAT_API_KEY"),
                verify_ssl_certs=False
            )
        except AuthenticationError as e:
            raise Exception(f"Auth error: {e}")


# Функция генерации описания с кэшированием
@lru_cache(maxsize=50)
def generate_task_description(title: str) -> str:
    start_time = time.time()
    manager = GigaChatManager()

    try:
        prompt = f"Сгенерируй краткое описание задачи (до 500 символов): {title}. Основные этапы:"
        response = manager.client.chat(prompt)
        description = response.choices[0].message.content

        print(f"Генерация заняла: {time.time() - start_time:.2f} сек")
        return description

    except ResponseError as e:
        if "token" in str(e).lower():
            print("Обновление токена...")
            manager.update_token()
            return generate_task_description(title)
        raise Exception(f"API error: {e}")

    except Exception as e:
        raise Exception(f"Неизвестная ошибка: {e}")
