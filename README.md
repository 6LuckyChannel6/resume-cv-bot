# Telegram CV Bot

Python-бот для Telegram, который собирает данные о кандидате и генерирует PDF-резюме.

## Возможности

- Пошаговый диалог в Telegram.
- Интерфейс бота на трех языках: қазақша, русский, English.
- Выбор одного из четырех визуальных шаблонов: Gray, Neon, Brown и Navy.
- Предложение добавить фото кандидата или пропустить этот шаг.
- Вопросы по структуре образца CV: ФИО, программа, образование, дата рождения,
  город, семейное положение, контакты, практика/опыт, курсы, квалификация,
  профессиональные навыки, личные качества, достижения и дополнительная информация.
- Один PDF-файл с тремя автоматически переведенными версиями резюме:
  қазақша, русский, English.
- Поддержка кириллицы и казахских символов.

## Запуск

1. Создайте бота через [BotFather](https://t.me/BotFather) и получите токен.
2. Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Создайте `.env`:

```bash
cp .env.example .env
```

4. Вставьте токен в `.env`:

```env
BOT_TOKEN=ваш_токен
```

5. Запустите бота:

```bash
python bot.py
```

В Telegram отправьте боту `/start`.

## Деплой на Koyeb

Проект подготовлен для Koyeb:

- `Dockerfile` - сборка контейнера.
- `deploy_koyeb.sh` - деплой напрямую из локальной папки через Koyeb CLI.
- `/health` - HTTP health check для Koyeb.
- Webhook-режим включается автоматически, если Koyeb задает `KOYEB_PUBLIC_DOMAIN`.

Перед деплоем нужен Koyeb API token. Его можно создать в Koyeb в настройках
аккаунта/API. Токен не нужно записывать в файлы проекта.

```bash
export KOYEB_TOKEN="ваш_koyeb_api_token"
./deploy_koyeb.sh
```

Скрипт берет `BOT_TOKEN` из локального `.env`, создает чистую временную папку
только с файлами приложения и деплоит ее на Koyeb как `resume-cv-bot/web`.

После успешного деплоя остановите локальный macOS LaunchAgent, чтобы локальный
polling не конфликтовал с Koyeb webhook:

```bash
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.lucky.cvbot.plist"
```

## Деплой на Render

Если Koyeb просит оплату, можно развернуть проект на Render Free Web Service.
Для Render добавлен `render.yaml`:

- `runtime: docker` - Render соберет контейнер из `Dockerfile`.
- `plan: free` - бесплатный web service.
- `PORT=10000` и `/health` - корректная проверка доступности сервиса.
- `BOT_TOKEN` задается вручную в Render как secret/environment variable.
- Webhook-режим включается автоматически через `RENDER_EXTERNAL_URL`.

После деплоя локальный polling тоже нужно остановить, чтобы он не конфликтовал
с webhook:

```bash
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.lucky.cvbot.plist"
```

## Автозапуск на macOS

Для этого проекта уже можно использовать LaunchAgent:

```bash
launchctl print "gui/$(id -u)/com.lucky.cvbot"
launchctl kickstart -k "gui/$(id -u)/com.lucky.cvbot"
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.lucky.cvbot.plist"
```

Логи автозапуска:

- `data/bot.launchd.log`
- `data/bot.launchd.err.log`

## Структура

- `bot.py` - логика Telegram-бота и диалог.
- `cv_generator.py` - генерация PDF.
- `data/` - готовые PDF-файлы и логи.

## Команды бота

- `/start` - начать создание резюме.
- `/skip` - пропустить фото.
- `/cancel` - отменить текущий диалог.
- `/help` - показать подсказку.

После `/start` бот сначала предложит выбрать язык интерфейса:
`Қазақша`, `Русский` или `English`.

## Автоперевод

Бот использует `deep-translator` для автоматического перевода пользовательского
текста на казахский, русский и английский. ФИО, телефон, email и дата рождения
не переводятся. Технические термины вроде `Python`, `SQL`, `HTML / CSS`
сохраняются без перевода.
