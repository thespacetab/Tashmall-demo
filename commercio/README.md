# Commercio - Платформа для бизнеса и мероприятий

Современная платформа для развития бизнеса, организации мероприятий и создания сильного сообщества предпринимателей.

## 📁 Структура проекта

```
frontend/           # Весь фронтенд (HTML, CSS, JS)
│   ├── index.html
│   ├── events.html
│   ├── partners.html
│   ├── style.css
│   ├── script.js
│   └── events.js
commercio/
├── backend/         # Flask backend API и документация
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
├── bot/             # Telegram-бот
│   └── bot.py
└── README.md        # Общая инструкция по проекту
```

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd <project-root>
```

### 2. Backend (API)
```bash
cd commercio/backend
pip install -r requirements.txt
python app.py
```
Сервер запустится на `http://localhost:8000`

### 3. Telegram Bot
```bash
cd ../bot
python bot.py
```

### 4. Frontend
Откройте файл `frontend/index.html` в браузере или используйте локальный сервер:
```bash
cd ../frontend
python -m http.server 3000
```

## 🛠 Технологии
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python Flask
- **Database**: SQLite
- **Telegram Bot**: pyTelegramBotAPI

## 🔧 Основные API Endpoints (см. commercio/backend/README.md)

## 🤖 Telegram Bot Команды
- `/start` — главное меню
- `/help` — справка
- `/register` — регистрация
- `/profile` — профиль пользователя

## 📈 Бизнес-модель и возможности
- Мультимагазинная платформа
- Telegram интеграция
- Аналитика и статистика
- Партнерская программа
- Мероприятия и нетворкинг

## 📞 Поддержка
- Email: support@commercio.com
- Telegram: @commercio_support

---
**Commercio** — создавайте, развивайте и масштабируйте свой бизнес! 🚀 