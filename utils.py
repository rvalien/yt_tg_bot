# -*- coding: utf-8 -*-
import requests


def get_weather(weather_token, city_id: int = 550280):  # Khimky
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': weather_token})
    data = res.json()
    res_text = f"температура: {round(data['main']['temp'], 1)}C, {data['weather'][0]['description']}"
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
