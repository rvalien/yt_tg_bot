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
from youtube_utils import printer, get_yt_info, _get_db_data, _make_picture, statistic_text, get_yt_info_new, write_data

# local debug
if sys.platform == 'win32':
    from config import *
    print('local execute')

telegram_token = os.environ['TELEGRAM_TOKEN']
youtube_token = os.environ['YOUTUBE_TOKEN']
weather_token = os.environ['WEATHER_TOKEN']
database = os.environ['DATABASE_URL']
stat_table = os.environ['CHANNEL_NAME']
delay = int(os.environ['DELAY'])
print('delay:', delay)

bot = Bot(token=telegram_token)
dp = Dispatcher(bot)

# do not disturb time
night_from = datetime.time(22)
night_to = datetime.time(8)

conn = psycopg2.connect(database)
cursor = conn.cursor()

chat_ids = []
cursor.execute('select chat_id from users')
for item in cursor.fetchall():
    chat_ids.append(item[0])

cursor.execute(f'select subscribers from {stat_table} where datetime = (select max(datetime) from {stat_table})')
subscribers = cursor.fetchall()
subscribers = subscribers[0][0]
conn.close()

markup = types.ReplyKeyboardMarkup()
markup.row(
    KeyboardButton('day 📈'),
    KeyboardButton('week 📈'),
    KeyboardButton('month 📅')
)
markup.row('🌤 weather 🌧')
markup.row('📱 internet 🌐')


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
    statistic_df = _get_db_data(database, period='day')
    stat = statistic_text(statistic_df)
    _make_picture(statistic_df)
    sum_stat = printer(*get_yt_info(youtube_token))
    text = f"статистика просмотров за {statistic_df.shape[1]} дня\n{stat}\nобщая статистика канала:\n{sum_stat}"
    media.attach_photo(types.InputFile('day.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp='week..')
async def worker(message):
    media = types.MediaGroup()
    statistic_df = _get_db_data(database, period='week')
    stat = statistic_text(statistic_df)
    _make_picture(statistic_df)
    sum_stat = printer(*get_yt_info(youtube_token))
    text = f"статистика просмотров за {statistic_df.shape[1]} недели\n{stat}\nобщая статистика канала:\n{sum_stat}"
    media.attach_photo(types.InputFile('week.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp='month..')
async def worker(message):
    media = types.MediaGroup()
    statistic_df = _get_db_data(database, period='month')
    stat = statistic_text(statistic_df)
    _make_picture(statistic_df)
    sum_stat = printer(*get_yt_info(youtube_token))
    text = f"статистика просмотров за {statistic_df.shape[1]} месяца\n{stat}\nобщая статистика канала:\n{sum_stat}"
    media.attach_photo(types.InputFile('month.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp='..internet..')
async def worker(message):
    await types.ChatActions.typing(2)
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f"select phone, password from users where chat_id = {message['from']['id']}")
    res = cursor.fetchone()

    await message.reply(str(print_ststel_info(get_ststel_data(*res))))


async def auto_yt_check(send=True):
    """
    check youtube subscribers and sand message every <daley> seconds if new counts not the same as last count
    add check result to log data
    disable sending if it's sleep time
    :param send: sanding massage is active
    :return: None
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
    response = get_yt_info_new(youtube_token)
    write_data(database, response)

    if send:
        if night_to < now < night_from:
            if len(db_subs) != 0 and db_subs[0][0] == current_subs:
                db_subs = db_subs[0][0]
                print(current_subs, db_subs)
                pass
            else:
                for chat_id in chat_ids:
                    await bot.send_message(chat_id, str(f'Подписки попёрли! Сейчас: {current_subs}'))


async def count_db_rows():
    """
    временная функция для отслеживания количества записей в базе данных. ограничение на бесплатном тарифе 10000 строк
    нужно, пока не переехал на другую бд.
    :return:
    """
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f'select count(*) from {stat_table}')
    count_rows = cursor.fetchall()[0][0]
    if count_rows > 9500:
        for chat_id in ['464620721']:
            await bot.send_message(chat_id=chat_id, text=str(f'Делай резервную копию базы. Строк сейчас: {count_rows}'))


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(delay, repeat, coro, loop)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(delay, repeat, auto_yt_check, loop)
    loop.call_later(delay, repeat, count_db_rows, loop)
    asyncio.run(executor.start_polling(dp, loop=loop))
