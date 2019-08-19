# -*- coding: utf-8 -*-
import os
import requests
import psycopg2


def printer(subs, views):
    s1 = "{:,d}".format(subs) + " подписчиков! 🍾🎉🍾"
    s2 = "{:,d}".format(views) + " просмотов! 🎈🎈🎈"
    return f'{s1}\n{s2}'


# def get_rhyme():
#     conn = sqlite3.connect("mydatabase.db")  # или :memory: чтобы сохранить в RAM
#     cursor = conn.cursor()
#     cursor.execute('SELECT name, rhyme FROM "rhyme"')  # все таблицы
#     items = cursor.fetchall()
#     # print(items)
#     # print(len(items))
#     rand_max = len(items) - 1
#     return items[randint(0, rand_max)]


# def add_rhyme(name, rhyme):
#     conn = sqlite3.connect("mydatabase.db")  # или :memory: чтобы сохранить в RAM
#     cursor = conn.cursor()
#     cursor.execute(f"insert into rhyme (name, rhyme) values('{name}', '{rhyme}')")
#     conn.commit()


def show_day_statistic(database):
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    cursor.execute(f'''select * from detektivo''')
    res = cursor.fetchall()
    return res


def get_yt_info(youtube_token, c_id='UCawxRTnNrCPlXHJRttupImA'):
    """

    :param c_id: youtube channel id
    :return: youtube channel subscribers and sum(views)
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={c_id}&key={youtube_token}"
    data = requests.get(url)
    if data.status_code == 200:
        subs = int(data.json()['items'][0]['statistics']['subscriberCount'])
        views = int(data.json()['items'][0]['statistics']['viewCount'])
        return subs, views
    else:
        print(data.status_code)


def get_weather(weather_token, city_id=550280):  # Khimky
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': weather_token})
    data = res.json()
    res_text = f"температура: {data['main']['temp']}C, {data['weather'][0]['description']}"
    return res_text
