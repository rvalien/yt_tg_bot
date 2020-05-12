# -*- coding: utf-8 -*-
import json
import requests
import psycopg2
import datetime
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import ticker


def get_yt(youtube_token: str, c_id: str = 'UCawxRTnNrCPlXHJRttupImA') -> (int, int):
    """
    :param youtube_token: youtube api token
    :param c_id: youtube channel id
    :return: youtube channel subscribers and sum(all videos views)
    """

    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={c_id}&key={youtube_token}"
    data = requests.get(url)
    if data.status_code == 200:
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


def prepare_day_query(day_depth=0):
    date = datetime.datetime.now().date() - datetime.timedelta(day_depth)
    columns = ', '.join(list(map(lambda x: f"{x}\n", range(0, 24))))
    values = ', '.join(list(map(lambda x: f"hour_{x} ->> 'viewCount'\n", range(0, 24))))
    query = f"""select unnest(array[{columns}]) as hour, unnest(array[{values}]) as "{date}"
    from channel_statistics cs 
    where stat_date = current_date - {day_depth} """
    return query


def get_data_day(database: str, n_days: int = 1) -> pd.DataFrame:
    conn = psycopg2.connect(database)
    result = pd.DataFrame()
    for i in range(0, n_days):
        df = pd.read_sql(prepare_day_query(i), conn)
        df = df.set_index(df.columns[0]).dropna().astype(int)
        result = pd.concat([df, result], axis=1, sort=False)
    return result


def get_data_week(database: str) -> pd.DataFrame:
    conn = psycopg2.connect(database)
    with open("./sql_queries/week.sql") as q:
        query = q.read()
    df = pd.read_sql(query, conn)
    res = pd.DataFrame({"day of week": ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'mon']})
    for week in df["week_num"].unique().astype(int):
        tdf = df[df["week_num"] == week].drop(
            columns=['week_num']).rename({"day_views": f"week_{week}"}, axis=1)
        res = pd.merge(tdf, res, left_on='day of week', right_on='day of week', how="outer")
    df = res.drop_duplicates()
    df = df.set_index('day of week')
    return df


def get_data_month(database: str) -> pd.DataFrame:
    conn = psycopg2.connect(database)

    with open("./sql_queries/month.sql") as q:
        query = q.read()
    df = pd.read_sql(query, conn)
    res = pd.DataFrame({"day of month": list(range(1, 32))})
    for item in df["month_num"].unique().astype(int):
        tdf = df[df["month_num"] == item].drop(
            columns=['month_num']).rename({"day_views": f"month_{item}"}, axis=1)
        res = pd.merge(tdf, res, left_on='day of month', right_on='day of month', how="outer")
    df = res.drop_duplicates()
    df = df.set_index('day of month')
    df.sort_index(inplace=True)
    return df


def make_picture(df: pd.DataFrame):
    name = df.index.name
    x_label = df.index.name
    x = df.index.values
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    width = 3
    for column in df.columns:
        ax.plot(x, df[column], label=column, linewidth=width)
        width += 2
    ax.set(xlim=[0, df.index.values.shape[0] - 1])
    ax.set_xlabel(x_label, fontsize=15)
    ax.set_ylabel('views', fontsize=15)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.title(f"views statistic by {name}", fontsize=22)
    leg = plt.legend()
    plt.savefig(f'{name}.png')


def prepare_text(dataframe, json_response) -> str:
    df_text = ""
    for i in dataframe.columns:
        df_text += f"{i.replace('_', ' ')}: {int(dataframe[i].max() - dataframe[i].min())} \n"
    sum_stat = f"""
    {json_response.get("items")[0].get("statistics").get("subscriberCount")} подписчиков\n
    {json_response.get("items")[0].get("statistics").get("viewCount")} просмотов"""
    # TODO поправить функцию что бы она дала корректный тест
    text = f"статистика просмотров за {dataframe.shape[1]} {dataframe.index}\n{df_text}\nобщая статистика канала:\n{sum_stat}"
    return text


if __name__ == '__main__':
    pass
