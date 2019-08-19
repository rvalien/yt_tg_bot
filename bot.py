import os
import sys
import asyncio
import sqlite3
import psycopg2
import datetime

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from utils import get_yt_info, printer, get_weather, show_day_statistic
from random import randint
import ikea


db_name = 'bot.db'
delay = 3600

if sys.platform == 'win32':
    from config import *
    print('локальненько в тестовом режимчике')
    db_name = 'bot_test.db'
    delay = 10

telegram_token = os.environ['TELEGRAM_TOKEN']
youtube_token = os.environ['YOUTUBE_TOKEN']
weather_token = os.environ['WEATHER_TOKEN']
database = os.environ['DATABASE_URL']

bot = Bot(token=telegram_token)
dp = Dispatcher(bot)

night_from = datetime.time(19)
night_to = datetime.time(5)

conn_pos = psycopg2.connect(database)
cursor_pos = conn_pos.cursor()

# conn = sqlite3.connect(db_name)
# cursor = conn.cursor()

chat_ids = []
cursor_pos.execute('select chat_id from chat_ids')
for item in cursor_pos.fetchall():
    chat_ids.append(item[0])

cursor_pos.execute('select subscribers from detektivo where datetime = (select max(datetime) from detektivo)')
subscribers = cursor_pos.fetchall()
subscribers = subscribers[0][0]
conn_pos.close()

markup = types.ReplyKeyboardMarkup()
markup.row('/youtube')
markup.row('/statistic')
markup.row('/weather')
markup.row('/ikea')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет, я GladOS и я умею:\n /youtube \n /weather", reply_markup=markup)


@dp.message_handler(commands=['youtube'])
async def send_welcome(message):
    await message.reply(printer(*get_yt_info(youtube_token)))
    # await message.reply('возврат оформи на туфли')


@dp.message_handler(commands=['weather'])
async def send_welcome(message):
    await message.reply(get_weather(weather_token))


@dp.message_handler(commands=['ikea'])
async def send_welcome(message):
    await message.reply(ikea.main())


@dp.message_handler(commands=['statistic'])
async def send_welcome(message):
    await message.reply(str(show_day_statistic(database)))


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
            conn.commit()
            conn.close()
    else:
        print(now)
        pass


async def auto_yt_check_postgress():
    now = datetime.datetime.now().time()
    current_subs, current_view = get_yt_info(youtube_token)
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute('select * from detektivo where datetime = (select max(datetime) from detektivo)')
    db_subs = cursor.fetchall()
    cursor.execute(f'''insert into detektivo (subscribers, views, datetime)
                        values('{current_subs}', '{current_view}', now())''')
    conn.commit()
    conn.close()

    if night_to < now < night_from:
        if len(db_subs) != 0 and db_subs[0][0] == current_subs:
            db_subs = db_subs[0][0]
            print(current_subs, db_subs)
            print('не делаем ничего')
            pass
        else:
            print('отправка')
            for chat_id in chat_ids:
                await bot.send_message(chat_id, printer(current_subs, current_view))


async def auto_ikea_check():
    now = datetime.datetime.now().time()
    if night_to < now < night_from:
        if ikea.main() == 'ничего нового':
            pass
        else:
            for chat_id in chat_ids:
                await bot.send_message(chat_id, ikea.main())


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(delay, repeat, coro, loop)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.call_later(delay, repeat, auto_yt_check, loop)
    loop.call_later(delay, repeat, auto_yt_check_postgress, loop)
    # loop.call_later(delay, repeat, auto_ikea_check, loop)
    asyncio.run(executor.start_polling(dp, loop=loop))
