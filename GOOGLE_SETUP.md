# Настройка Google Drive API (OAuth 2.0)

Мы используем метод **OAuth 2.0** (приложение для ПК), чтобы бот мог загружать файлы от вашего имени и использовать ваше место на Диске.

## Шаг 1: Создание проекта (если еще нет)
1.  Перейдите в [Google Cloud Console](https://console.cloud.google.com/).
2.  Выберите или создайте проект.

## Шаг 2: Включение API (если еще нет)
1.  **APIs & Services** -> **Library**.
2.  Найдите `Google Drive API` и нажмите **Enable**.

## Шаг 3: Настройка экрана доступа (OAuth Consent Screen)
*(Если вы делаете это впервые)*
1.  **APIs & Services** -> **OAuth consent screen**.
2.  User Type: **External** -> Create.
3.  App Name: `TelegramBot`. Email: ваш.
4.  Нажимайте **Save and Continue** на всех этапах (Scopes можно пропустить).
5.  **Важно:** В разделе **Test Users** нажмите **Add Users** и добавьте свой Gmail (которого будете использовать). Без этого может не пустить.

## Шаг 4: Создание ключей (Credentials)
1.  **APIs & Services** -> **Credentials**.
2.  Нажмите **Create Credentials** -> **OAuth client ID**.
3.  Application type: **Desktop app**.
4.  Name: `BotClient`.
5.  Нажмите **Create**.
6.  Скачайте JSON файл (кнопка "Download JSON").
7.  **Переименуйте** файл в `client_secrets.json`.
8.  **Положите** его в папку с ботом: `d:\desktop\Bot\client_secrets.json`.

## Шаг 5: Первый запуск
1.  Запустите бота: `python main.py`.
2.  Автоматически откроется браузер.
3.  Выберите свой аккаунт Google.
4.  Если Google скажет "Google hasn’t verified this app" (Приложение не проверено) — нажмите **Advanced** (Дополнительно) -> **Go to ... (unsafe)**. Это нормально, так как вы сами создали это приложение только что.
5.  Нажмите **Continue** / **Allow**.
6.  Вы увидите сообщение "The authentication flow has completed".

Теперь в папке бота появится файл `token.json`.
Бот готов к работе!

## Как перенести на сервер (хостинг)?
Просто скопируйте файл `token.json` вместе с остальными файлами бота на сервер.
Там браузер уже не понадобится.
