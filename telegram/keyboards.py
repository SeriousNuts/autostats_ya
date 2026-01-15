from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню с кнопкой для получения отчета
def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Получить отчет", callback_data="get_report")]
    ])
    return keyboard