import bs4
import sys
import smtplib
import sqlite3
import datetime
import requests
import os

# from config import *
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart


db_name = 'bot.db'


def get_info(price, link):
    r = requests.get(link)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    try:
        result = soup.find("meta", {"name": "price"})['content']
        family_r = soup.find("meta", {"name": "changed_family_price"})['content']
        prs = (result.split('.')[0])
        if family_r:
            prs = (family_r.split('.')[0])
        prs = prs.replace(chr(32), '')
        prs = prs.replace(chr(160), '')
        if price <= int(prs):
            pass
        else:
            return soup.title.text, prs, link, price
    except TypeError as e:
        print('что-то пошло не так', e, link)


def load_data(cursor):
    cursor.execute(f"select price, link from ikea")
    res = cursor.fetchall()
    return res


def update_db(cursor, name, price, item_link):
    now = datetime.datetime.now()
    q = f"update ikea set price = {price}, date = '{now}' where link = '{item_link}'"
    cursor.execute(q)
    print(f'{name} updated')


def add_new_to_db(link):
    r = requests.get(link)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    result = soup.find("meta", {"name": "price"})['content']
    family_r = soup.find("meta", {"name": "changed_family_price"})['content']
    prs = (result.split('.')[0])
    if family_r:
        prs = (family_r.split('.')[0])
    prs = prs.replace(chr(32), '')
    prs = prs.replace(chr(160), '')
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    now = datetime.datetime.now()
    print(soup.title.text, prs, link, 'added')
    q = f"insert into ikea(title, price, link, date) values('{soup.title.text}', {prs}, '{link}', '{now}')"
    cursor.execute(q)
    conn.commit()
    conn.close()


def show_db_items():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    q = f"select * from ikea"
    cursor.execute(q)
    result = cursor.fetchall()
    print('elements: ', len(result))
    for item in result:
        print(item)
    conn.close()


def main():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    data_from_db = load_data(cursor)
    for item in data_from_db:
        data_from_site = (get_info(*item))
        # print(data_from_site)
        if data_from_site:
            update_db(cursor, *data_from_site[:-1])
            conn.commit()
            conn.close()
            return f'{data_from_site[0]} new price {data_from_site[1]}, old price {data_from_site[3]},' \
                f' {data_from_site[2]}'
        else:
            pass
    conn.close()
    return 'ничего нового'




if __name__ == '__main__':
    # add_new_to_db('https://www.ikea.com/ru/ru/catalog/products/20370547/')
    # show_db_items()
    print(main())
    # print(get_info(199, 'https://www.ikea.com/ru/ru/catalog/products/30375139/'))