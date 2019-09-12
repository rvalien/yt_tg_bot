# -*- coding: utf-8 -*-
import pandas as pd
import requests
import psycopg2
import datetime
import os


def printer(subs, views):
    s1 = "{:,d}".format(subs) + " подписчиков! 🍾🎉🍾"
    s2 = "{:,d}".format(views) + " просмотов! 🎈🎈🎈"
    return f'{s1}\n{s2}'


def _get_db_data(database):
    conn = psycopg2.connect(database)
    df = pd.read_sql('select * from detektivo', conn)
    return df


def _transform_db_data(df):
    df = df.assign(datetime=df['datetime'] + datetime.timedelta(minutes=180))  # так мы хитро получаем московское время.
    df = df[df['datetime'].dt.date == pd.Timestamp.now().date()].sort_values(by='datetime')
    df = df.assign(datetime=df['datetime'].values.astype('datetime64[s]'))
    df = df.assign(time=df['datetime'].dt.time)
    df = df.assign(hour=df['datetime'].dt.hour)
    df = df.assign(subs_shifted=df['subscribers'].shift(1), views_shifted=df['views'].shift(1))
    df = df.assign(subs_hourly=df['subscribers'] - df['subs_shifted'], views_hourly=df['views'] - df['views_shifted'])

    df = df.set_index('hour')
    df.sort_index(inplace=True)
    return df


# def show_day_statistic(database, path='./data/stat.png'):
#     df = _get_db_data(database)
#     df = _transform_db_data(df)
#
#     # make text
#     max_sub = df.loc[df['subs_hourly'] == df['subs_hourly'].max()][['time', 'subs_hourly']].values[0]
#     max_view = df.loc[df['views_hourly'] == df['views_hourly'].max()][['time', 'views_hourly']].values[0]
#     stat_text = f"""
#     в период с {df.iloc[0]['datetime'].hour} по {df.iloc[-1]['datetime'].hour} подписалось {df.iloc[-1]['subscribers'] - df.iloc[0]['subscribers']}.
#     пик просмотров в {max_view[0].hour} ч. ({int(max_view[1])})
#     пик подписок в {max_sub[0].hour} ч. ({int(max_sub[1])}) """
#
#     # make picture
#     df[['subs_hourly']].plot(figsize=(10, 5), xticks=df.index, title='статуся').get_figure().savefig(path)
#     return stat_text


def show_day_statistic(database):
    conn = psycopg2.connect(database)
    df = pd.read_sql("select * from detektivo where datetime >= current_date - INTERVAL '2 DAY'", conn)
    df = df.dropna()
    df = df.assign(datetime=df['datetime'] + datetime.timedelta(minutes=180))  # так мы хитро получаем московское время.

    df = df.assign(datetime=df['datetime'].values.astype('datetime64[s]'))
    df = df.assign(date=df['datetime'].dt.date)
    df = df.assign(time=df['datetime'].dt.time)
    df = df.assign(hour=df['datetime'].dt.hour)
    df = df.sort_values(by='datetime')
    df = df.assign(subs_shifted=df['subscribers'].shift(1), views_shifted=df['views'].shift(1))
    df = df.assign(subs_hourly=df['subscribers'] - df['subs_shifted'], views_hourly=df['views'] - df['views_shifted'])
    df = df.drop(columns=['subs_shifted', 'views_shifted', 'datetime'])
    past = df[df['date'] == pd.Timestamp.now().date() - pd.Timedelta('2 days')].set_index('hour').sort_index()
    yest = df[df['date'] == pd.Timestamp.now().date() - pd.Timedelta('1 days')].set_index('hour').sort_index()
    tod = df[df['date'] == pd.Timestamp.now().date()].set_index('hour').sort_index()
    past = past.add_suffix('_past')
    yest = yest.add_suffix('_yest')
    tod = tod.add_suffix('_tod')
    res = pd.concat([yest, tod, past], 1)

    max_sub = tod.loc[tod['subs_hourly_tod'] == tod['subs_hourly_tod'].max()][['time_tod', 'subs_hourly_tod']].values[0]
    max_view = \
    tod.loc[tod['views_hourly_tod'] == tod['views_hourly_tod'].max()][['time_tod', 'views_hourly_tod']].values[0]

    #     # make picture
    res[['subs_hourly_tod',
         'subs_hourly_yest',
         'subs_hourly_past']].fillna(method='pad').plot(figsize=(10, 5), xticks=res.index,
                                                        title='подписки').get_figure().savefig('subs.png')

    res[['views_hourly_tod',
         'views_hourly_yest',
         'views_hourly_past']].fillna(method='pad').plot(figsize=(10, 5), xticks=res.index,
                                                         title='просмотры').get_figure().savefig('views.png')

    #     time_text = (df.iloc[0]['time_tod'].hour, df.iloc[-1]['time_tod'].hour)
    #     subs_text = df.iloc[-1]['subscribers_tod'] - df.iloc[0]['subscribers_tod']
    stat_text = f"""
    в период с  по  подписалось
    """
    return stat_text


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


def get_gbs_left(login: str, password: str) -> dict:
    url = 'http://ststel.ru/lk/submit.php'
    header = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0"}
    payload = {'phone': str(login), 'pass': str(password)}
    a, b = 0, 0
    i = 0
    with requests.Session() as s:
        while a == 0 and b == 0:
            print(i)
            r = s.post(url, data=payload, headers=header)
            if r.status_code != 200:
                return f'ошибка авторизации {r.status_code}'
            else:
                foo = r.json()['customers']
                if len(foo) != 1:
                    print('проверь код')
                else:
                    foo = foo[0]
                    a, b = foo['ctnInfo']['rest_internet_initial'], foo['ctnInfo']['rest_internet_current']
                i += 1
        return foo['ctnInfo']


def print_gb_info(data: dict) -> str:
    data = int(data['rest_internet_current'])

    if data >= 1024:
        i = 'Gb'
        data = round(data / 1024, 2)
    else:
        i = 'Mb'
    return f'осталось {data} {i}'


if __name__ == '__main__':
    pass
