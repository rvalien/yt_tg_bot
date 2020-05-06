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
from youtube_utils import get_data_day, get_data_week, get_data_month, make_picture, prepare_text, get_yt, write_data

print("init bot")

# local debug
if sys.platform == "win32":
    from config import *

    print("local execute")

telegram_token = os.environ["TELEGRAM_TOKEN"]
youtube_token = os.environ["YOUTUBE_TOKEN"]
weather_token = os.environ["WEATHER_TOKEN"]
database = os.environ["DATABASE_URL"]
stat_table = os.environ["CHANNEL_NAME"]
delay = int(os.environ["DELAY"])
print("delay:", delay)
print("-" * 30)
bot = Bot(token=telegram_token)
dp = Dispatcher(bot)

# do not disturb time
night_from = datetime.time(22)
night_to = datetime.time(8)

conn = psycopg2.connect(database)
cursor = conn.cursor()

chat_ids = []
cursor.execute("select chat_id from users")
print("update users")
for item in cursor.fetchall():
    chat_ids.append(item[0])
print(chat_ids)
print("-" * 30)
print("collect last database data")

with open("./sql_queries/max_db_subs.sql") as q:
    max_db_subs = q.read()

cursor.execute(max_db_subs)
subscribers = cursor.fetchone()
subscribers = int(subscribers[0])
print("subscribers:", subscribers)
print("-" * 30)
conn.close()
print("done")

markup = types.ReplyKeyboardMarkup()
markup.row(
    KeyboardButton("day 📈"),
    KeyboardButton("week 📈"),
    KeyboardButton("month 📅")
)
markup.row("🌤 weather 🌧")
markup.row("📱 internet 🌐")


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await types.ChatActions.typing(1)
    await message.reply("Привет, я GladOS. я умею показывать статистику просмотров видео youtube канала\n ",
                        reply_markup=markup)


@dp.message_handler(regexp="day..")
async def worker(message):
    media = types.MediaGroup()
    statistic_df = get_data_day(database, n_days=2)
    raw = get_yt(youtube_token)
    text = prepare_text(statistic_df, raw)
    make_picture(statistic_df.diff(-1).apply(abs))
    media.attach_photo(types.InputFile("hour.png"), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp="week..")
async def worker(message):
    media = types.MediaGroup()
    statistic_df = get_data_week(database)
    raw = get_yt(youtube_token)
    text = prepare_text(statistic_df, raw)
    make_picture(statistic_df)
    media.attach_photo(types.InputFile("day of week.png"), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp="month..")
async def worker(message):
    media = types.MediaGroup()
    statistic_df = get_data_month(database)
    raw = get_yt(youtube_token)
    text = prepare_text(statistic_df, raw)
    make_picture(statistic_df)
    media.attach_photo(types.InputFile("day of month.png"), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp="..weather..")
async def worker(message):
    await types.ChatActions.typing(1)
    await message.reply(get_weather(weather_token))


@dp.message_handler(regexp="..internet..")
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
    response = get_yt(youtube_token)
    current_subs = int(response.get("items")[0].get("statistics").get("subscriberCount"))
    connection = psycopg2.connect(database)
    cursor = connection.cursor()
    with open("./sql_queries/max_db_subs.sql") as sql_file:
        query = sql_file.read()

    cursor.execute(query)
    db_subs = cursor.fetchone()
    db_subs = int(db_subs[0])
    conn.close()
    write_data(database, response)
    if send:
        if night_to < datetime.datetime.utcnow().time() < night_from:
            if db_subs == current_subs:
                print(current_subs, db_subs)
                pass
            else:
                for chat_id in chat_ids:
                    await bot.send_message(
                        chat_id,
                        str(f"Изменеие в количестве подписчиков.\nбыло:  {db_subs}\nстало: {current_subs}")
                    )


async def count_db_rows():
    # TODO убрать после переходна на новую таблицу
    """
    временная функция для отслеживания количества записей в базе данных. ограничение на бесплатном тарифе 10000 строк
    нужно, пока не переехал на другую бд.
    :return:
    """
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f"select count(*) from {stat_table}")
    count_rows = cursor.fetchall()[0][0]
    if count_rows > 9500:
        for chat_id in ["464620721"]:
            await bot.send_message(chat_id=chat_id, text=str(f"Делай резервную копию базы. Строк сейчас: {count_rows}"))


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(delay, repeat, coro, loop)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(delay, repeat, auto_yt_check, loop)
    loop.call_later(delay, repeat, count_db_rows, loop)
    asyncio.run(executor.start_polling(dp, loop=loop))
