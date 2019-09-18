# -*- coding: utf-8 -*-
import pandas as pd
import requests
import psycopg2
import datetime


def printer(subs: int, views: int) -> str:
    """

    :param subs:
    :param views:
    :return:
    """

    s1 = "{:,d}".format(subs) + " подписчиков! 🍾🎉🍾"
    s2 = "{:,d}".format(views) + " просмотов! 🎈🎈🎈"
    return f'{s1}\n{s2}'


def _get_db_data(database: str, depth_days: int = 2, tz: int = 3) -> pd.DataFrame:
    """

    :param database: database connection string
    :param depth_days: how many days ago you need to get from DB
    :param tz: correct timezone from UTC to GMT +3 (Russia/Moscow)
    :return: result dataframe
    """
    conn = psycopg2.connect(database)
    query = f"""select
                    min(subscribers) as subscribers,
                    min(views) as views, 
                    date_part('day', datetime  + interval '{tz} hours') as cur_date_gmt,
                    date_part('hour', datetime  + interval '{tz} hours') as cur_hour_gmt
                from
                    detektivo where datetime  + interval '{tz} hours' >= current_date - INTERVAL '{depth_days} DAY'
                group by cur_date_gmt, cur_hour_gmt
                order by cur_date_gmt, cur_hour_gmt"""

    df = pd.read_sql(query, conn)
    return df


def _make_picture(df: pd.DataFrame, column: str = 'views'):
    """
    method prepare and save 2 pictures based on dataframe
    :param df: dataframe with a few days statistic
    :param column: part of columns name, that we need to make a plot
    :return:
    """
    df.filter(regex=column) .plot(figsize=(10, 5), xticks=list(range(0, 25)),
                                  title=column).get_figure().savefig(f'{column}.png')


def _statistic_text(df: pd.DataFrame) -> str:
    """

    :param df:
    :return: text to send with images
    """
    max_view = df.loc[df['views_hourly_today'] == df['views_hourly_today'].max()][['views_hourly_today']]
    first = int(df['subscribers_today'][0])
    last = int(df['subscribers_today'].dropna().max())

    stat_text = f"""
    {datetime.datetime.now().date()} подписок: {last - first}
    пик просмотров в {int(max_view.index[0])} ч. ({int(max_view.values[0][0])})
    """

    return stat_text


def _transform_db_data(df: pd.DataFrame) -> pd.DataFrame:
    """

    :param df: raw dataframe from database
    :return: transformed dataframe
    """
    df = df.assign(subs_shifted=df['subscribers'].shift(1), views_shifted=df['views'].shift(1))
    df = df.assign(subs_hourly=df['subscribers'] - df['subs_shifted'], views_hourly=df['views'] - df['views_shifted'])
    df = df.drop(columns=['subs_shifted', 'views_shifted'])

    today = df[df['cur_date_gmt'] == max(list(df['cur_date_gmt']))].set_index('cur_hour_gmt').sort_index()
    yesterday = df[df['cur_date_gmt'] == (1 + min(list(df['cur_date_gmt'])))].set_index('cur_hour_gmt').sort_index()
    past = df[df['cur_date_gmt'] == min(list(df['cur_date_gmt']))].set_index('cur_hour_gmt').sort_index()
    past = past.add_suffix('_past')
    yesterday = yesterday.add_suffix('_yesterday')
    today = today.add_suffix('_today')
    res = pd.concat([yesterday, today, past], 1)
    # res = res.drop(columns=res.filter(regex='cur_date_gmt_').columns)
    return res


def show_day_statistic(database: str, path: str = 'subs_.png') -> str:
    """

    :param database: connection string of database
    :param path: image name to save
    :return: text to send
    """
    df = _get_db_data(database)
    df = _transform_db_data(df)

    # make picture
    _make_picture(df, column='subs_hourly')
    # _make_picture(df, column='views_hourly')
    return _statistic_text(df)


def get_yt_info(youtube_token: str, c_id: str = 'UCawxRTnNrCPlXHJRttupImA') -> (int, int):
    """

    :param youtube_token: youtube api token
    :param c_id: youtube channel id
    :return: youtube channel subscribers and sum(all videos views)
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={c_id}&key={youtube_token}"
    data = requests.get(url)
    if data.status_code == 200:
        subs = int(data.json()['items'][0]['statistics']['subscriberCount'])
        views = int(data.json()['items'][0]['statistics']['viewCount'])
        return subs, views
    else:
        print(data.status_code)


def get_weather(weather_token, city_id: int = 550280):  # Khimky
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
