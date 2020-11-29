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

with open("sql_queries/max_db_data.sql") as q:
    max_db_data = q.read()

cursor.execute(max_db_data)
last_check_date, last_check_hour, views, subscribers = cursor.fetchone()
last_check_hour, views, subscribers = map(int, (last_check_hour, views, subscribers))

print("subscribers:", subscribers, type(subscribers))
print("last_check_hour:", last_check_hour, type(last_check_hour))
print("-" * 30)
conn.close()
print("done")

markup = types.ReplyKeyboardMarkup()
markup.row(KeyboardButton("day 📈"), KeyboardButton("week 📈"), KeyboardButton("month 📅"))
markup.row("🌤 weather 🌧")
markup.row(KeyboardButton("📱 internet 🌐"), KeyboardButton("📱 bill 🌐"))


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await types.ChatActions.typing(1)
    await message.reply(
        "Привет, я GladOS. я умею показывать статистику просмотров видео youtube канала\n", reply_markup=markup
    )


@dp.message_handler(regexp="day..")
async def worker(message):
    media = types.MediaGroup()
    statistic_df = get_data_day(database, n_days=2)
    raw = get_yt(youtube_token)
    text = prepare_text(database, raw)
    make_picture(statistic_df.diff(-1).apply(abs))
    media.attach_photo(types.InputFile("hour.png"), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp="week..")
async def worker(message):
    media = types.MediaGroup()
    statistic_df = get_data_week(database)
    raw = get_yt(youtube_token)
    text = prepare_text(database, raw)
    make_picture(statistic_df)
    media.attach_photo(types.InputFile("day of week.png"), text)
    await types.ChatActions.upload_photo()
    await message.reply_media_group(media=media)


@dp.message_handler(regexp="month..")
async def worker(message):
    media = types.MediaGroup()
    statistic_df = get_data_month(database)
    raw = get_yt(youtube_token)
    text = prepare_text(database, raw)
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


@dp.message_handler(regexp="..bill..")
async def worker(message):
    await types.ChatActions.typing(2)
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute("select phone, password, name from users")
    res = cursor.fetchall()

    def get_all_mobile_bills(all_users):
        result = dict()
        for user in all_users:
            result[user[2]] = get_ststel_data(user[0], user[1])
        return result

    def prepare_response_text(data):
        temp_list = list()
        for key in data.keys():
            temp = f'{key}: {data[key].get("effectiveBalance") if data[key].get("effectiveBalance") else data[key].get("balance")}'
            temp_list.append(temp)
        return "\n".join(temp_list)

    await message.reply(prepare_response_text(get_all_mobile_bills(res)))


@dp.message_handler(regexp="myid")
async def worker(message):
    await types.ChatActions.typing(2)
    print(message.from_user)
    await message.reply(message.from_user)


async def auto_yt_check(send=False):
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
    with open("sql_queries/max_db_data.sql") as sql_file:
        query = sql_file.read()

    cursor.execute(query)
    db_hour, db_views, db_subs = map(int, cursor.fetchone())
    conn.close()
    write_data(database, response)
    if send:
        if night_to < datetime.datetime.now().time() < night_from:
            print("x" * 10)
            print(f"database: hour: {db_hour}, subscribers: {db_subs}")
            print(f"cur time: hour: {datetime.datetime.now().hour}, subscribers: {current_subs}")
            if db_subs == current_subs or datetime.datetime.now().hour == db_hour:
                print("pass")
                pass
            else:
                print("work")
                for chat_id in chat_ids:
                    await bot.send_message(
                        chat_id,
                        # два пробела тут, что бы выравнять по строки --> <--
                        str(f"Изменеие в количестве подписчиков.\nбыло:  {db_subs}\nстало: {current_subs}"),
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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.call_later(delay, repeat, auto_yt_check, loop)
    loop.call_later(delay, repeat, count_db_rows, loop)
    asyncio.run(executor.start_polling(dp, loop=loop))
