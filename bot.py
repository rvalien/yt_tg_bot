import os
import sys
import asyncio
import psycopg2
import datetime

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.types import KeyboardButton
from aiogram.dispatcher import Dispatcher
from utils import get_weather, get_gbs_left, print_gb_info
from youtube_utils import _get_db_data, printer, get_yt_info, _make_picture,  day_stat, week_stat, month_stat

delay = 900

if sys.platform == 'win32':
    from config import *
    print('локальненько в тестовом режимчике')
    delay = 900

telegram_token = os.environ['TELEGRAM_TOKEN']
youtube_token = os.environ['YOUTUBE_TOKEN']
weather_token = os.environ['WEATHER_TOKEN']
database = os.environ['DATABASE_URL']
stat_table = os.environ['CHANNEL_NAME']


bot = Bot(token=telegram_token)
dp = Dispatcher(bot)

night_from = datetime.time(22)
night_to = datetime.time(8)

conn = psycopg2.connect(database)
cursor = conn.cursor()

chat_ids = []
cursor.execute('select chat_id from chat_ids')
for item in cursor.fetchall():
    chat_ids.append(item[0])
    print(chat_ids)

cursor.execute(f'select subscribers from {stat_table} where datetime = (select max(datetime) from {stat_table})')
subscribers = cursor.fetchall()
subscribers = subscribers[0][0]
conn.close()


markup = types.ReplyKeyboardMarkup()
markup.row(KeyboardButton('youtube 🎬'),
           KeyboardButton('day 📈'),
           KeyboardButton('week 📈'),
           KeyboardButton('month 📅'))
markup.row('🌤 weather 🌧')
markup.row('📱 internet 🌐')
markup.row('🍾 alco 🥂')

# InlineKeyboardMarkup


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await types.ChatActions.typing(1)
    await message.reply("""Привет, я GladOS. я умею показывать статистику по просмотрам youtube канала""",
                        reply_markup=markup)


# TODO брать
@dp.message_handler(regexp='youtube..')
async def send_welcome(message):
    await types.ChatActions.typing(1)
    await message.reply(printer(*get_yt_info(youtube_token)))
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f"insert into yt_query_log(chat_id, datetime) values('{message['from']['id']}', now())")

    # two days views count
    cursor.execute(f"""select count(*) from yt_query_log
                        where datetime >= current_date and chat_id = '{message['from']['id']}'""")
    two_days = _get_db_data(database, quary_name='day', depth=0)

    await message.reply(f"вчера :\n{two_days.set_index('date')[['views','subscribers']].iloc[0]}")
    await message.reply(f"сегодня :\n{two_days.set_index('date')[['views','subscribers']].iloc[-1]}")
    res = cursor.fetchone()
    if res[0] > 5:
        await message.reply(str(f'А ещё, ты проверяешь статистику уже {res[0]} раз за сегодня'))

    conn.commit()


@dp.message_handler(regexp='..weather..')
async def send_welcome(message):
    await types.ChatActions.typing(1)
    await message.reply(get_weather(weather_token))


@dp.message_handler(regexp='day..')
async def send_welcome(message):
    media = types.MediaGroup()
    text = "статистика просмотров за два дня"
    _make_picture(day_stat(database))
    # TODO убрать хардкод названий файлов
    media.attach_photo(types.InputFile('day.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)




@dp.message_handler(regexp='week..')
async def send_welcome(message):
    media = types.MediaGroup()
    # text = make_text_and_picture(database)
    _make_picture(week_stat(database))
    text = "статистика просмотров за две недели"
    # TODO убрать хардкод названий файлов
    media.attach_photo(types.InputFile('week.png'), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)
    # conn = psycopg2.connect(database)
    # cursor = conn.cursor()
    # cursor.execute(f"""select count(*) from yt_query_log
    #                     where datetime >= current_date and chat_id = '{message['from']['id']}'""")
    # two_weeks = _get_db_data(database, quary_name='two_days')
    #
    # await message.reply(f"прошлая неделя :\n{two_weeks.set_index('date').iloc[0]}")
    # await message.reply(f"эта неделя :\n{two_weeks.set_index('date').iloc[1]}")
    # res = cursor.fetchone()
    # if res[0] > 5:
    #     await message.reply(str(f'А ещё, ты проверяешь статистику уже {res[0]} раз за сегодня'))


@dp.message_handler(regexp='month..')
async def send_welcome(message):
    _make_picture(month_stat(database))
    media = types.MediaGroup()
    media.attach_photo(types.InputFile('month.png'), "статистика просмотров за 2 месяца")
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)
    # conn = psycopg2.connect(database)
    # cursor = conn.cursor()
    # cursor.execute(f"""select count(*) from yt_query_log
    #                     where datetime >= current_date and chat_id = '{message['from']['id']}'""")
    # two_month = _get_db_data(database, quary_name='two_days')
    # two_month = _get_db_data(database, quary_name='two_days')
    #
    # await message.reply(f"прошлая неделя :\n{two_weeks.set_index('date').iloc[0]}")
    # await message.reply(f"эта неделя :\n{two_weeks.set_index('date').iloc[1]}")
    # res = cursor.fetchone()
    # if res[0] > 5:
    #     await message.reply(str(f'А ещё, ты проверяешь статистику уже {res[0]} раз за сегодня'))


@dp.message_handler(regexp='..alco..')
async def send_welcome(message):
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    await types.ChatActions.typing(1)
    price = 400
    reason = 'праздничный ужин'
    cursor.execute(f"insert into alco(date, price, reason) values(current_date, {price}, '{reason}')")
    conn.commit()
    await message.reply(str('записано'))


@dp.message_handler(regexp='..internet..')
async def send_welcome(message):
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f"select phone, password from ststel where chat_id = {message['from']['id']}")
    res = cursor.fetchone()
    await types.ChatActions.typing(1)
    await message.reply(str(print_gb_info(get_gbs_left(*res))))


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
                print('не делаем ничего')
                pass
            else:
                print('отправка')
                for chat_id in chat_ids:
                    print(chat_id)
                    await types.ChatActions.typing(1)
                    await bot.send_message(chat_id, str(f'Подписки попурли! Сейчас: {current_subs}'))


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(delay, repeat, coro, loop)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(delay, repeat, auto_yt_check, loop)
    asyncio.run(executor.start_polling(dp, loop=loop))
