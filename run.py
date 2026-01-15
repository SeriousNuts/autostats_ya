import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from telegram.bot import router
from setup_logging import setup_logging

def set_bot(bot: Bot):
    global bot_instance
    bot_instance = bot

def init_bot():
    TOKEN = os.environ.get("BOT_TOKEN")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    return bot, dp

async def start_bot_polling() -> None:
    """Запуск бота в режиме polling"""
    bot, dp = init_bot()
    dp.include_router(router)


    set_bot(bot)
    logging.info("===telegram bot started in POLLING mode===")
    await dp.start_polling(bot, skip_updates=False)

async def run_bot():
    setup_logging()
    print("starting bot..")
    bot = asyncio.create_task(start_bot_polling())
    await bot

print("start running bot only")
asyncio.run(run_bot())