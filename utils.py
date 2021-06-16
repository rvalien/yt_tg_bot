# -*- coding: utf-8 -*-
import random
import requests


def get_weather(weather_token: str, city_id: int = 550280) -> str:
    """
    get
    :param weather_token: api token from openweathermap
    :param city_id:  default Khimky Russia
    :return: short weather info in 1 string in celsius
    """
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': weather_token})
    data = res.json()
    return f"{round(data['main']['temp'], 1)}C, {data['weather'][0]['description']}"


def get_ststel_data(login: str, password: str) -> dict:
    """

    :param login:
    :param password:
    :return:
    """
    url = 'http://ststel.ru/lk/submit.php'
    header = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0"}
    payload = {'phone': str(login), 'pass': str(password)}
    a, b, i = 0, 0, 0
    with requests.Session() as s:
        # we need while because ststel returns zeroes some times
        while a == 0 and b == 0:
            print(i)
            r = s.post(url, data=payload, headers=header)
            if r.status_code != 200:
                return f'ошибка авторизации {r.status_code} {r.text}'
            else:
                foo = r.json()['customers']
                if len(foo) != 1:
                    print(f"error: {foo=}, {len(foo)=}")
                else:
                    foo = foo[0]
                    a, b = foo['ctnInfo']['balance'], foo['ctnInfo']['rest_internet_current']
                i += 1
        return foo['ctnInfo']


def get_all_mobile_bills(all_users):
    result = dict()
    for item in all_users:
        result[item[0]] = get_ststel_data(**item)
    return result


def print_ststel_info(data: dict) -> str:
    """

    :param data: data from
    :return: short string
    """
    internet = int(data['rest_internet_current'])

    if internet >= 1024:
        i = 'Gb'
        internet = round(internet / 1024, 2)
    else:
        i = 'Mb'

    if int(data['balance']) != int(data['effectiveBalance']):
        balans = data['balance']
    else:
        balans = data['balance'], data['effectiveBalance']

    return f'''Осталось {internet} {i}. Баланс: {balans} р. '''


def free_time(message, redis_client) -> str:

    """
    :return: short string
    """
    # TODO прототип для изучения редис. Переписать на использование списков
    keyword = "exp2"
    opportunities = ["книга", "покер", "шахматная доска", "ванна", "сон", "дуэлька"]

    if redis_client.get(keyword) is None:
        redis_client.set(keyword, ", ".join(opportunities))

    base = redis_client.get(keyword)
    param = message.text.split("/time ")

    if param == ['/time']:
        opportunity = random.choice(base.decode().split(", "))

        return f"Тебя ждёт {opportunity.decode()}"

    else:
        if param[-1] == "all":
            return f"Весь список:\n{redis_client.get(keyword).decode()}"

        elif len(param[-1]) > 0:
            base = ", ".join([base.decode(), param[-1]])
            redis_client.set(keyword, base)

            return f"{param[-1]} добавлено в список."
        else:
            return 'ничего не понял.'


if __name__ == '__main__':
    pass
