import os
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.exceptions import AuthenticationError, ResponseError
import threading

load_dotenv()


class GigaChatManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.client = None
        self.update_token()

    def update_token(self):
        with self.lock:
            try:
                self.client = GigaChat(
                    credentials=os.getenv("GIGACHAT_API_KEY"),
                    verify_ssl_certs=False
                )
            except AuthenticationError as e:
                raise Exception(f"Auth error: {e}")


def generate_task_description(title: str) -> str:
    manager = GigaChatManager()
    try:
        prompt = f"Сгенерируй детальное описание для задачи управления проектами. Заголовок: {title}. Опиши этапы выполнения, возможные подзадачи и рекомендации."
        return manager.client.chat(prompt).choices[0].message.content
    except ResponseError as e:
        if "token" in str(e).lower():
            manager.update_token()
            return generate_task_description(title)
        raise Exception(f"API error: {e}")
