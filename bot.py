import os
import sys
import asyncio
import psycopg2
import datetime

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.types import KeyboardButton
from aiogram.dispatcher import Dispatcher
from utils import get_weather, get_ststel_data, print_ststel_info
from youtube_utils import _get_db_data, printer, get_yt_info, _make_picture,  day_stat, week_stat, month_stat

# local debug
if sys.platform == 'win32':
    from config import *
    print('локальненько в тестовом режимчике')

telegram_token = os.environ['TELEGRAM_TOKEN']
youtube_token = os.environ['YOUTUBE_TOKEN']
weather_token = os.environ['WEATHER_TOKEN']
database = os.environ['DATABASE_URL']
stat_table = os.environ['CHANNEL_NAME']
delay = int(os.environ['DELAY'])


bot = Bot(token=telegram_token)
dp = Dispatcher(bot)

# do not disturb time
night_from = datetime.time(22)
night_to = datetime.time(8)

conn = psycopg2.connect(database)
cursor = conn.cursor()

chat_ids = []
cursor.execute('select chat_id from chat_ids')
for item in cursor.fetchall():
    chat_ids.append(item[0])

cursor.execute(f'select subscribers from {stat_table} where datetime = (select max(datetime) from {stat_table})')
subscribers = cursor.fetchall()
subscribers = subscribers[0][0]
conn.close()


markup = types.ReplyKeyboardMarkup()
markup.row(
    # KeyboardButton('youtube 🎬'),
           KeyboardButton('day 📈'),
           KeyboardButton('week 📈'),
           KeyboardButton('month 📅'))
markup.row('🌤 weather 🌧')
markup.row('📱 internet 🌐')
markup.row('🍾 alco 🥂')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await types.ChatActions.typing(1)
    await message.reply("""Привет, я GladOS. я умею показывать статистику по просмотрам youtube канала""",
                        reply_markup=markup)


@dp.message_handler(regexp='..weather..')
async def worker(message):
    await types.ChatActions.typing(1)
    await message.reply(get_weather(weather_token))


@dp.message_handler(regexp='day..')
async def worker(message):
    media = types.MediaGroup()
    text = f"статистика просмотров за два дня\n\nобщая статистика канала:\n{printer(*get_yt_info(youtube_token))}"
    _make_picture(day_stat(database))
    media.attach_photo(types.InputFile('day.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp='week..')
async def worker(message):
    media = types.MediaGroup()
    _make_picture(week_stat(database))
    text = f"статистика просмотров две недели\n\nобщая статистика канала:\n{printer(*get_yt_info(youtube_token))}"
    media.attach_photo(types.InputFile('week.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp='month..')
async def worker(message):
    _make_picture(month_stat(database))
    text = f"статистика просмотров два месяца\n\nобщая статистика канала:\n{printer(*get_yt_info(youtube_token))}"
    media = types.MediaGroup()
    media.attach_photo(types.InputFile('month.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp='..alco..')
async def worker(message):
    await types.ChatActions.typing(1)
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    price = 400
    reason = 'праздничный ужин'
    cursor.execute(f"insert into alco(date, price, reason) values(current_date, {price}, '{reason}')")
    conn.commit()
    await message.reply(str('записано'))


@dp.message_handler(regexp='..internet..')
async def worker(message):
    await types.ChatActions.typing(2)
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f"select phone, password from ststel where chat_id = {message['from']['id']}")
    res = cursor.fetchone()

    await message.reply(str(print_ststel_info(get_ststel_data(*res))))


async def auto_yt_check(send=True):
    """

    :param send:
    :return:
    """
    now = datetime.datetime.utcnow().time()
    current_subs, current_view = get_yt_info(youtube_token)
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f'select * from {stat_table} where datetime = (select max(datetime) from {stat_table})')
    db_subs = cursor.fetchall()
    cursor.execute(f'''insert into {stat_table} (subscribers, views, datetime)
                       values('{current_subs}', '{current_view}', now())''')
    conn.commit()
    conn.close()

    if send:
        if night_to < now < night_from:
            if len(db_subs) != 0 and db_subs[0][0] == current_subs:
                db_subs = db_subs[0][0]
                print(current_subs, db_subs)
                pass
            else:
                for chat_id in chat_ids:
                    await types.ChatActions.typing(1)
                    await bot.send_message(chat_id, str(f'Подписки попёрли! Сейчас: {current_subs}'))


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(delay, repeat, coro, loop)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(delay, repeat, auto_yt_check, loop)
    asyncio.run(executor.start_polling(dp, loop=loop))
