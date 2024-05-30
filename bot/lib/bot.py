import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import abc
from lib.dto import NutritionInfo

class IBackend(abc.ABC):
    @abc.abstractmethod
    def get_nutrition_info(self, user_id: str, description: str) -> NutritionInfo:
        pass
    @abc.abstractmethod
    def get_recommendations(self, user_id: str) -> str:
        pass

def start_bot(backend: IBackend) -> None: 
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    TOKEN = getenv("BOT_TOKEN")

    dp = Dispatcher()


    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        """
        This handler receives messages with `/start` command
        """
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

    @dp.message(Command('recommendations'))
    async def command_start_handler(message: Message) -> None:
        """
        This handler receives messages with `/start` command
        """
        try:
            rec = backend.get_recommendations(str(message.from_user.id))
            await message.answer(rec)
        except: 
            await message.answer('Произошла ошибка')

    @dp.message()
    async def meal_handler(message: Message) -> None:
        """
        Handler will forward receive a message back to the sender

        By default, message handler will handle all message types (like a text, photo, sticker etc.)
        """
        try:
            nutrition_info = backend.get_nutrition_info(str(message.from_user.id), message.text)
            await message.answer(f'{nutrition_info.calories} калорий')
        except: 
            await message.answer('Не удалось обработать ваш запрос')

    async def main() -> None:
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await dp.start_polling(bot)

    asyncio.run(main())