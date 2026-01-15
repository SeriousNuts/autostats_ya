import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


# ID администраторов (указываются через запятую в .env)
# Пример в .env: ADMIN_USER_IDS=123456789,987654321
ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]

def is_user_admin(user_id: int) -> bool:
    """Проверяет, есть ли пользователь в списке администраторов."""
    return user_id in ADMIN_USER_IDS