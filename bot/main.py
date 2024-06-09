"""Module which runs the Nutritioner Telegram Bot."""
import asyncio
import json
import logging
import sys
from os import getenv

import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

STATUS_OK = 200
STATUS_BAD_REQUEST = 400

BOT_TOKEN = getenv('BOT_TOKEN')
BASE_URL = getenv('BACKEND_BASE_URL')

dp = Dispatcher()


@dp.message(CommandStart())
async def _command_start_handler(message: Message) -> None:
    full_name = message.from_user.full_name
    await message.answer(f'Hello, {full_name}!')


@dp.message(Command('recommendations'))
async def _recommendations_handler(message: Message) -> None:
    user_id = message.from_user.id
    wait_msg = await message.answer('Генерируем ответ...')
    resp = requests.get(f'{BASE_URL}/api/v1/stats', params={'user_id': user_id})
    await wait_msg.delete()
    if resp.status_code != STATUS_OK:
        return await message.answer('Произошла ошибка')
    return await message.answer(resp.json()['recommendations'])


@dp.message()
async def _meal_handler(message: Message) -> None:
    description = message.text
    if not description:
        return await message.answer('Пожалуйста, введите текстовое описание')
    body = json.dumps({'description': description, 'user_id': message.from_user.id})
    wait_msg = await message.answer('Генерируем ответ...')
    resp = requests.post(f'{BASE_URL}/api/v1/meals', data=body)
    await wait_msg.delete()
    if resp.status_code != STATUS_OK:
        if resp.status_code == STATUS_BAD_REQUEST:
            return await message.answer('Неверный запрос')
        return await message.answer('Произошла ошибка, попробуйте позже')
    calories = int(resp.json()['calories'])
    await message.answer(f'{calories} калорий.')


asyncio.run(dp.start_polling(Bot(token=BOT_TOKEN)))
