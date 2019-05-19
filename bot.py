import os
import asyncio
import sqlite3
import datetime

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from utils import get_yt_info, printer, get_weather
import ikea

from config import *

telegram_token = os.environ['TELEGRAM_TOKEN']
youtube_token = os.environ['YOUTUBE_TOKEN']
weather_token = os.environ['WEATHER_TOKEN']

bot = Bot(token=telegram_token)
dp = Dispatcher(bot)
db_name = 'bot.db'

delay = 3600
night_from = datetime.time(19)
night_to = datetime.time(5)
#
# delay = 60
# night_from = datetime.time(19)
# night_to = datetime.time(5)
#

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

chat_ids = []
cursor.execute('select chat_id from chat_ids')
for item in cursor.fetchall():
    chat_ids.append(item[0])

try:
    cursor.execute('select subscribers from detectivo')
    subscribers = cursor.fetchall()[0][0]
except sqlite3.OperationalError:
    cursor.execute("""CREATE TABLE detectivo (subscribers int) """)
    cursor.execute(f'insert into detectivo values({1000})')
finally:
    subscribers = 1
    conn.commit()
    conn.close()


markup = types.ReplyKeyboardMarkup()
markup.row('/youtube')
markup.row('/weather')
markup.row('/ikea')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет, я GladOS и я умею:\n /youtube \n /weather", reply_markup=markup)


@dp.message_handler(commands=['youtube'])
async def send_welcome(message):
    await message.reply(printer(*get_yt_info(youtube_token)))


@dp.message_handler(commands=['weather'])
async def send_welcome(message):
    await message.reply(get_weather(weather_token))


@dp.message_handler(commands=['ikea'])
async def send_welcome(message):
    await message.reply(ikea.main())


async def auto_yt_check():
    now = datetime.datetime.now().time()
    if night_to < now < night_from:
        current_subs, current_view = get_yt_info(youtube_token)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('select subscribers from detectivo')
        db_subs = cursor.fetchall()[0][0]
        print(current_subs, db_subs)
        if current_subs == db_subs:
            print('не делаем ничего')
            conn.close()
            pass
        else:
            print('отправка')
            for chat_id in chat_ids:
                await bot.send_message(chat_id, printer(current_subs, current_view))
            cursor.execute(f'UPDATE detectivo SET subscribers = {current_subs}')
            print('тут мы делаем коммит')
            conn.commit()
            print('закрываем соединение')
            conn.close()
    else:
        print(now)
        pass


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(delay, repeat, coro, loop)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(delay, repeat,
                    auto_yt_check,
                    # ikea.main,
                    loop)
    executor.start_polling(dp, loop=loop)
