# Commercio Frontend

Фронтенд часть платформы Commercio - современный интернет-магазин с поддержкой мероприятий и партнерств.

## 🚀 Быстрый запуск

### 1. Откройте index.html в браузере
Просто дважды кликните на `index.html` или откройте через браузер.

### 2. Или используйте локальный сервер
```bash
# Python 3
python -m http.server 3000

# Node.js
npx serve .

# PHP
php -S localhost:3000
```

Затем откройте `http://localhost:3000`

## 📁 Структура файлов

- `index.html` - Главная страница
- `events.html` - Страница мероприятий
- `partners.html` - Страница партнеров
- `shop.html` - Страница магазина
- `style.css` - Основные стили
- `script.js` - Основной JavaScript
- `events.js` - JavaScript для мероприятий
- `shop.js` - JavaScript для магазина

## 🔧 Требования

- Современный браузер (Chrome, Firefox, Safari, Edge)
- Backend API должен быть запущен на `http://localhost:8000`

## 🎨 Особенности дизайна

- Адаптивная верстка
- Современные градиенты и анимации
- Font Awesome иконки
- Шрифт Inter
- Темная/светлая тема

## 📱 Поддерживаемые устройства

- Desktop (1920px+)
- Tablet (768px - 1024px)
- Mobile (320px - 768px)

## 🔗 Интеграция

Frontend интегрируется с:
- Backend API (Flask)
- Telegram Bot
- База данных SQLite

## 🚀 Развертывание

Для продакшена:
1. Соберите статические файлы
2. Загрузите на CDN или веб-сервер
3. Обновите API_BASE в JavaScript файлах

---
**Commercio Frontend** - современный и отзывчивый интерфейс! 🎨 