# Screenshot Bot
Телеграм-бот для создания скриншотов веб-страниц.
Бот получает от пользователя ссылку, переходит по ней и 
делает скриншот страницы и сохраняет код ответа страницы. 
Полученный скриншот и код страницы отправляется обратно пользователю.
Скриншоты страниц сохраняются в папку (путь до неё настраивается в файле .env) 
с именем в формате «YYYY-MM-DD_HH:mm_<link>.jpg».


### Требования
1. Docker version 20.10.21
2. Telegram. Требуется получить специальный токен, 
который необходим для авторизации бота и работы с Bot API.
Получить его можно на канале @botfather -
официальном сервисе для настройки и управления созданными телеграм-ботами.
3. Screenshot API - бесплатный сервис для создания 
скриншотов веб-страниц. После прохождения простой регистрации 
будет доступен токен, с помощью которого будет осуществляться доступ
к функционалу API: https://www.screenshotmachine.com/register.php

### Инструкция по запуску
1. Клонируем репозиторий
```sh
git clone git@github.com:artemyev1003/screenshot_bot.git
```
2. Определяем переменные среды (без пробелов и кавычек, например:
SCREENSHOTS_DIR=/Users/user/screenshots)
- SCREENSHOTS_DIR - путь к папке, в которую будут сохраняться скриншоты
- TG_TOKEN - токен Telegram Bot API
- SCREENSHOTMACHINE_API_KEY - токен Screenshot API
```sh
echo SCREENSHOTS_DIR=... > .env
echo TG_TOKEN=... >> .env
echo SCREENSHOTMACHINE_API_KEY=... >> .env
```
3. Собираем образ и запускаем контейнер 
(с использованием значения SCREENSHOTS_DIR в качестве одного из параметров) 
```sh
source .env
echo $SCREENSHOTS_DIR
docker build -t screenshots_bot .
docker run -d -v $SCREENSHOTS_DIR:/app/screenshots --env-file .env --name bot screenshots_bot
```