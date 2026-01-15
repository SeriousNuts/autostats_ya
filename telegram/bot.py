import logging
import os

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile

from telegram.keyboards import get_main_menu_keyboard
from telegram.middleware import is_user_admin
from report_generator import generate_report

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветственное сообщение и проверка прав."""
    user_id = message.from_user.id

    if not is_user_admin(user_id):
        await message.answer("⛔ У вас нет доступа к этому боту.")
        return

    welcome_text = (
        f"Добро пожаловать, {message.from_user.first_name}!\n"
        "Я бот для генерации отчетов из Яндекс.Статистики.\n"
        "Нажмите кнопку ниже, чтобы получить свежий отчет."
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())

# ---------- Обработчик нажатия на кнопку "Получить отчет" ----------
@router.callback_query(F.data == "get_report")
async def send_report_callback(callback: types.CallbackQuery):
    """Обрабатывает запрос на создание и отправку отчета."""
    user_id = callback.from_user.id

    # Повторная проверка прав (на всякий случай)
    if not is_user_admin(user_id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    # Сообщаем пользователю, что начали формировать отчет
    await callback.message.edit_text("⏳ Формирую отчет, это займет несколько секунд...")

    try:
        # 1. Генерируем Excel-файл
        filepath = await generate_report()

        # 2. Отправляем файл пользователю
        document = FSInputFile(filepath)
        await callback.message.answer_document(
            document,
            caption="✅ Ваш отчет по статистике готов!"
        )
        # Удаляем служебное сообщение "Формирую отчет"
        await callback.message.delete()

        # 3. Опционально: удаляем файл с диска после отправки
        os.remove(filepath)
        logging.info(f"[LOG] Файл {filepath} удален после отправки.")

    except Exception as e:
        # Обработка ошибок
        error_msg = f"При формировании отчета произошла ошибка:\n`{e}`"
        await callback.message.edit_text(error_msg)
        logging.info(f"[ERROR] {e}")

    # Подтверждаем получение callback, чтобы убрать часики на кнопке
    await callback.answer()