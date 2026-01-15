import logging
import os
import sys


def setup_logging():
    """Настройка единого логгера для всего приложения"""

    log_level = os.environ.get("LOG_LEVEL", "INFO")


    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(message)s"
    )

    # Создаем обработчики
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)


    # Настраиваем базовую конфигурацию
    logging.basicConfig(
        level=log_level,
        handlers=[stdout_handler]
    )