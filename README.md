# telegram bot for your youtube channel
# create a log where store data
# you can see subscribers and view statistic info.
# additionally informs about the weather and the rest of the Internet traffic (oly for my provider)


### сейчас это простой бот может: по запросу возвращать погоду (получаем используюя апи https://openweathermap.org/),
### возврашать по запросу количетво подписчиков канала на youtube.com, и в виде граффика динамику просмотров
### раз в n секунд проверять изменение количества подписчиков и отправляет уведомление обозначенным контактам
### настроен на работу с сервисом https://www.heroku.com/ и базой данных posgressql.

![day stat](readme/day.png)

![week stat](readme/week.png)

![month stat](readme/month.png)


не забудь создать нужнык таблицы

и прописать переменные окружения
CHANNEL_NAME
DATABASE_URL
PROJECT_NAME
TELEGRAM_TOKEN
WEATHER_TOKEN
YOUTUBE_TOKEN
