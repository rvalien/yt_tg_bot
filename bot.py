import os
import sys
import asyncio
import psycopg2
import datetime

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.types import KeyboardButton
from aiogram.dispatcher import Dispatcher
from utils import get_yt_info, printer, get_weather, show_day_statistic, get_gbs_left, print_gb_info


delay = 900

if sys.platform == 'win32':
    from config import *
    print('локальненько в тестовом режимчике')
    delay = 180

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

chat_ids = []
cursor_pos.execute('select chat_id from chat_ids')
for item in cursor_pos.fetchall():
    chat_ids.append(item[0])

cursor_pos.execute('select subscribers from detektivo where datetime = (select max(datetime) from detektivo)')
subscribers = cursor_pos.fetchall()
subscribers = subscribers[0][0]
conn_pos.close()


markup = types.ReplyKeyboardMarkup()
markup.row(KeyboardButton('youtube 🎬'), KeyboardButton('statistic 📈'))
markup.row('🌤 weather 🌧')
markup.row('📱 internet 🌐')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await types.ChatActions.typing(1)
    await message.reply("Привет, я GladOS и я умею:\n /youtube \n /weather", reply_markup=markup)


@dp.message_handler(regexp='youtube..')
async def send_welcome(message):
    await types.ChatActions.typing(1)
    await message.reply(printer(*get_yt_info(youtube_token)))
    conn_pos = psycopg2.connect(database)
    cursor_pos = conn_pos.cursor()
    cursor_pos.execute(f"insert into yt_query_log(chat_id, datetime) values('{message['from']['id']}', now())")
    conn_pos.commit()


@dp.message_handler(regexp='..weather..')
async def send_welcome(message):
    await types.ChatActions.typing(1)
    await message.reply(get_weather(weather_token))


@dp.message_handler(regexp='statistic..')
async def send_welcome(message):

    media = types.MediaGroup()
    text = show_day_statistic(database)
    # TODO убрать хардкод названий файлов
    media.attach_photo(types.InputFile('subs_hourly.png'), text)
    # media.attach_photo(types.InputFile('views_.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp='..internet..')
async def send_welcome(message):
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f"select phone, password from ststel where chat_id = {message['from']['id']}")
    res = cursor.fetchone()
    await types.ChatActions.typing(1)
    await message.reply(str(print_gb_info(get_gbs_left(*res))))


async def auto_yt_check(send=False):
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
    if send:
        if night_to < now < night_from:
            if len(db_subs) != 0 and db_subs[0][0] == current_subs:
                db_subs = db_subs[0][0]
                print(current_subs, db_subs)
                print('не делаем ничего')
                pass
            else:
                print('отправка')
                for chat_id in chat_ids:
                    await types.ChatActions.typing(1)
                    await bot.send_message(chat_id, printer(current_subs, current_view))


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(delay, repeat, coro, loop)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(delay, repeat, auto_yt_check, loop)
    asyncio.run(executor.start_polling(dp, loop=loop))
