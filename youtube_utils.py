# -*- coding: utf-8 -*-
import requests
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib import ticker
import datetime
import json


def printer(subs: int, views: int) -> str:
    """
    :param subs:
    :param views:
    :return:
    """

    s1 = "{:,d}".format(subs) + " подписчиков! 🍾🎉🍾"
    s2 = "{:,d}".format(views) + " просмотов! 🎈🎈🎈"
    return f'{s1}\n{s2}'


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


def get_yt_info_new(youtube_token: str, c_id: str = 'UCawxRTnNrCPlXHJRttupImA') -> (int, int):
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
        return data.json()
    else:
        print(data.status_code)


def write_data(database, request_data, table='channel_statistics'):
    conn = psycopg2.connect(database)
    cursor = conn.cursor()
    time = datetime.datetime.now().time()
    date = datetime.datetime.now().date()
    statistics = request_data.get("items")[0].get("statistics")
    # insert / update
    query = f'''
    insert into {table} (stat_date, hour_{time.hour})
    values('{date.strftime('%Y-%m-%d')}', '{json.dumps(statistics)}')
    ON CONFLICT (stat_date)
    DO UPDATE SET hour_{time.hour} = '{json.dumps(statistics)}'
    WHERE {table}.stat_date = '{date.strftime('%Y-%m-%d')}'
    and {table}.hour_{time.hour} is null '''
    cursor.execute(query)
    conn.commit()
    conn.close()


def _get_db_data(database: str, query_name: str = 'statistic_query', period: str = None) -> pd.DataFrame:
    """
    :param database: postgresql database connection string
    :param query_name: sql query name from dir (sql_queries)
    :param period: week or month day)
    :return: dataframe
    """

    conn = psycopg2.connect(database)
    with open(f'./sql_queries/{query_name}.sql', encoding='utf-8', mode='r') as o:
        query = o.read()
    if period == 'day':
        query = query.format('day', (0, 24), 'hour')
    elif period == 'week':
        query = query.format('week', (1, 7), 'isodow')
    elif period == 'month':
        query = query.format('month', (1, 31), 'day')
    df = pd.read_sql(query, conn)
    df = df.set_index(df.columns[0]).dropna(axis=0, how='all')
    return df


def _get_db_data_new(database: str, n_days: int = 1) -> pd.DataFrame:
    conn = psycopg2.connect(database)
    result = pd.DataFrame()
    for i in range(0, n_days):
        df = pd.read_sql(get_day_stat_query(i), conn)
        df = df.set_index(df.columns[0]).dropna().astype(int)
        result = pd.concat([df, result], axis=1, sort=False)
    return result


def _make_picture(df: pd.DataFrame):
    """
    make picture and save to .
    :param df:
    :return: none
    """
    name = df.index.name
    df = df.filter(like='views')
    x_lable = 'day'
    x = df.index.values
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    width = 6
    for column in df.filter(like='views').columns:
        ax.plot(x, df[column], label=column.replace('_', ' '), linewidth=width)
        width -= 3
    ax.set(xlim=[x.min(), x.max()])
    ax.set_xlabel(x_lable, fontsize=15)
    ax.set_ylabel('views', fontsize=15)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.title(f"views statistic by {name}", fontsize=22)
    leg = plt.legend()
    plt.savefig(f'{name}.png')


def _make_picture_new(df: pd.DataFrame):
    name = df.index.name
    x_label = df.index.name
    x = df.index.values
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    width = 3
    for column in df.columns:
        ax.plot(x, df[column], label=column, linewidth=width)
        width += 2
    ax.set(xlim=[x.min(), x.max()])
    ax.set_xlabel(x_label, fontsize=15)
    ax.set_ylabel('views', fontsize=15)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.title(f"views statistic by {name}", fontsize=22)
    leg = plt.legend()
    plt.savefig(f'{name}.png')


def statistic_text(df: pd.DataFrame) -> str:
    """
    count views from dataframe adn format it to string
    :param df:
    :return: string
    """
    text = ''
    for i in df.filter(like='views').columns:
        text += f"{i.replace('_', ' ')}: {int(df[i].max() - df[i].min())} \n"
    return text


def get_day_stat_query(day_depth=0):
    date = datetime.datetime.now().date() - datetime.timedelta(day_depth)
    columns = ', '.join(list(map(lambda x: f"{x}\n", range(0, 24))))
    values = ', '.join(list(map(lambda x: f"hour_{x} ->> 'viewCount'\n", range(0, 24))))
    query = f"""select unnest(array[{columns}]) as hour, unnest(array[{values}]) as "{date}"
    from channel_statistics cs 
    where stat_date = current_date - {day_depth} """
    return query


if __name__ == '__main__':
    pass
