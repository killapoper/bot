# Инструкция по деплою (Linux/VPS)

Следуйте этим шагам, чтобы запустить бота на сервере в режиме 24/7.

## 1. Подготовка
- VPS на Linux (рекомендуется Ubuntu 22.04+).
- Установленный Python 3.10 или выше.
- Файлы бота, загруженные на сервер.

## 2. Настройка сервера
Подключитесь к серверу по SSH и выполните:
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и Pip, если они отсутствуют
sudo apt install python3 python3-pip -y
```

## 3. Установка
Перейдите в папку с ботом (например, `/root/Bot`) и установите зависимости:
```bash
# Рекомендуется использовать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установка библиотек
pip install -r requirements.txt
```

## 4. Конфигурация
Убедитесь, что в папке бота есть следующие файлы:

### Создайте файл `.env`:
```
BOT_TOKEN=ваш_токен_бота_от_BotFather
EXCEL_FILE=purchases.xlsx
GOOGLE_DRIVE_FOLDER_NAME=CTMC
ADMIN_IDS=ваш_id,второй_id
```

### Скопируйте файлы:
- `client_secrets.json` (из Google Cloud Console).
- `token.json` (**ВАЖНО**: Сначала запустите бота один раз на своем компьютере, чтобы создать этот файл через браузер, а затем загрузите `token.json` на сервер. На серверах обычно нет браузера для входа).

## 5. Настройка автозапуска (Systemd)
Чтобы бот сам запускался после перезагрузки сервера или сбоев:

1. Создайте файл службы:
   `sudo nano /etc/systemd/system/tgbot.service`

2. Вставьте следующее содержимое (исправьте пути, если они отличаются!):
```ini
[Unit]
Description=Telegram Purchase Bot
After=network.target

[Service]
User=root
# Путь к папке с ботом
WorkingDirectory=/root/Bot
# Путь к интерпретатору Python внутри venv
ExecStart=/root/Bot/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Активируйте и запустите:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tgbot
sudo systemctl start tgbot
```

## 6. Мониторинг и управление
- **Проверить статус**: `sudo systemctl status tgbot`
- **Посмотреть логи**: `tail -f bot.log`
- **Перезапустить**: `sudo systemctl restart tgbot`
