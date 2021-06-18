# Telegram bot for your youtube channel
1. the bot creates log
2. the bot shows subscribers and view statistic info for selected youtube channel.
3. once every n seconds the bot check the change in the number of subscribers and sends a notification to the designated contacts if the numbers have changed

build on [heroku](https://www.heroku.com/) and use postgres

![day stat](samples/day.png)

![week stat](samples/week.png)

![month stat](samples/month.png)

don't forget to [create tables](samples/make_main_tables.sql) and specify your config vars on Heroku

|**variable name**|type|description|
|:---|:---:|:---|
`CHANNEL_NAME`|str|name of the channel and table to store data in database|
`DATABASE_URL`|str|connection string for your database|
`PROJECT_NAME`|str|just name of your project. use to make heroku web hook|
`TELEGRAM_TOKEN`|str|create your bot and get the token [here](https://tlgrm.ru/docs/bots)|
`YOUTUBE_TOKEN`|str|your token [more info](https://developers.google.com/youtube/registering_an_application)|
`DELAY`|int|sleep time (seconds)|


for local use, create `config.py` with environ variables

```python
import os

os.environ['CHANNEL_NAME'] = 'name of the channel and database you create'
os.environ['DATABASE_URL'] = 'con. string'
os.environ['PROJECT_NAME'] = 'bot name'
os.environ['TELEGRAM_TOKEN'] = '<your token>'
os.environ['YOUTUBE_TOKEN'] = '<your token>'
os.environ['DELAY'] = 900 # sleep time
```

***

# Telegram bot для вашего youtube канала: 
1. пишет логи
2. возвращать по запросу количество просмотров и подписчиков канала на youtube.com
3. раз в n секунд проверять изменение количества подписчиков и отправляет уведомление обозначенным контактам если цифры изменились

Настроен на работу с сервисом [heroku](https://www.heroku.com/) и базой данных posgressql.

![day stat](samples/day.png)

![week stat](samples/week.png)

![month stat](samples/month.png)

Не забудь [создать нужные таблицы](samples/make_main_tables.sql) и прописать переменные окружения в Heroku


|**variable name**|type|description|
|:---|:---:|:---|
`CHANNEL_NAME`|str|name of the channel and table to store data in database|
`DATABASE_URL`|str|connection string for your database|
`PROJECT_NAME`|str|just name of your project. use to make heroku web hook|
`TELEGRAM_TOKEN`|str|create your bot and get the token [here](https://tlgrm.ru/docs/bots)|
`YOUTUBE_TOKEN`|str|your token [more info](https://developers.google.com/youtube/registering_an_application)|
`DELAY`|int|sleep time (seconds)|


Для локального исполнения, создай файл `config.py` с переменными окружения

```python
import os

os.environ['CHANNEL_NAME'] = 'name of the channel and database you create'
os.environ['DATABASE_URL'] = 'con. string'
os.environ['PROJECT_NAME'] = 'bot name'
os.environ['TELEGRAM_TOKEN'] = '<your token>'
os.environ['YOUTUBE_TOKEN'] = '<your token>'
os.environ['DELAY'] = 900 # sleep time
```