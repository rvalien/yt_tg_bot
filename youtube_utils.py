# -*- coding: utf-8 -*-
import requests
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib import ticker


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


def _get_db_data(database: str, quary_name: str = 'day', period=None, depth: int = 1, tz: int = 3) -> pd.DataFrame:
    """
    :param database: postgresql database connection string
    :param quary_name: sql query name from dir (sql_queries)
    :param period: week or month (use only if query name != day)
    :param depth: how many days ago you need to get from DB
    :param tz: tz: correct timezone from UTC to GMT +3 (Russia/Moscow)
    :return: dataframe
    """
    conn = psycopg2.connect(database)
    with open(f'./sql_queries/{quary_name}.sql', encoding='utf-8', mode='r') as o:
        query = o.read()
    query = query.format(tz, depth, period, os.environ['CHANNEL_NAME'])
    df = pd.read_sql(query, conn)
    return df


def day_stat(database: str) -> pd.DataFrame:
    """
    prepare dataframe with 2 last days statistic
    :param database: postgresql database connection string
    :return: dataftame
    """

    df = _get_db_data(database, quary_name='day', period='day')
    df.loc[df['views'] < 0, ['views']] = None
    df = df.fillna(method='backfill')
    res = pd.DataFrame(index=list(range(0, 24)))
    for i in df['day'].unique():
        temp_df = df.loc[df['day'] == i][['views', 'hour']].set_index('hour').add_suffix(f'_{int(i)}')
        res = pd.merge(res, temp_df, how='outer', left_index=True, right_index=True)
    return res


def week_stat(database: str) -> pd.DataFrame:
    """
    prepare dataframe with week statistic
    :param database: postgresql database connection string
    :return: dataftame
    """
    df = _get_db_data(database, quary_name='ststistic_query', period='week')
    df.loc[df['views'] < 0, ['views']] = None
    df = df.fillna(method='backfill')
    df['dayofweek'] = df['dayofweek'].astype(int)
    res = pd.DataFrame(index=list(range(1, 8)))
    for i in df['week'].unique():
        temp_df = df.loc[df['week'] == i][[
            'views', 'dayofweek']].set_index('dayofweek').add_suffix(f'_{int(i)}')
        res = pd.merge(res, temp_df, how='outer', left_index=True, right_index=True)
    return res


def month_stat(database: str) -> pd.DataFrame:
    """
    prepare dataframe with month statistic
    :param database: postgresql database connection string
    :return: dataftame
    """
    df = _get_db_data(database, quary_name='ststistic_query', period='month')
    df.loc[df['views'] < 0, ['views']] = None
    df = df.fillna(method='backfill')
    res = pd.DataFrame(index=list(range(1, 32)))
    for i in df['month'].unique():
        temp_df = df.loc[df['month'] == i][[
            'views', 'day']].set_index('day').add_suffix(f'_{int(i)}')
        res = pd.merge(res, temp_df, how='outer', left_index=True, right_index=True)

    return res


def _make_picture(df: pd.DataFrame):
    """
    make picture and save to .
    :param df:
    :return: none
    """
    name = 'day'
    x_lable = 'day'
    df = df.filter(like='views')
    x = df.index.values
    if df.shape[0] == 7:
        name = 'week'
    elif df.shape[0] == 31:
        name = 'month'
    else:
        x_lable = 'hour'

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    width = 3
    for i in df.columns:
        ax.plot(x, df[i], label=f"{name} № {i.split('_')[1]} views:{int(df[i].max() - df[i].min())} ", linewidth=width)
        width += 5
    ax.set(xlim=[x.min(), x.max()])
    ax.set_xlabel(x_lable, fontsize=15, )
    ax.set_ylabel('views', fontsize=15, )
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.title(f"views statistic by {name}", fontsize=22)
    leg = plt.legend()

    plt.savefig(f'{name}.png')


def statistic_text(df):
    name = 'day'
    if df.shape[0] == 7:
        name = 'week'
    elif df.shape[0] > 27:
        name = 'month'
    text = ''
    for i in df.columns:
        text += f"{name} №{i.split('_')[1]} views: {int(df[i].max() - df[i].min())} \n"
    return text


if __name__ == '__main__':
    pass

