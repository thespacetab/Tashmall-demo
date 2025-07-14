import telebot
from telebot import types
import requests
import json
from datetime import datetime, timedelta
import os

# Configuration
BOT_TOKEN = "7779332599:AAFQ6K9GpYmKSoHwq8F3BmUrDGDOs9yAmyk"
API_BASE = "http://localhost:8000/api"

bot = telebot.TeleBot(BOT_TOKEN)

# User states for conversation flow
user_states = {}

class UserState:
    def __init__(self):
        self.state = "main"
        self.data = {}

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = UserState()
    return user_states[user_id]

# Main menu keyboard
def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        types.KeyboardButton("🏪 Магазины"),
        types.KeyboardButton("📅 Мероприятия"),
        types.KeyboardButton("🤝 Партнеры"),
        types.KeyboardButton("📊 Статистика"),
        types.KeyboardButton("👤 Профиль"),
        types.KeyboardButton("❓ Помощь")
    )
    return keyboard

# Admin keyboard
def get_admin_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        types.KeyboardButton("➕ Создать магазин"),
        types.KeyboardButton("➕ Добавить товар"),
        types.KeyboardButton("📅 Создать мероприятие"),
        types.KeyboardButton("👥 Управление пользователями"),
        types.KeyboardButton("📈 Аналитика"),
        types.KeyboardButton("🔙 Главное меню")
    )
    return keyboard

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.first_name
    
    welcome_text = f"""
🎉 Добро пожаловать в Commercio!

Привет, {user_name}! Я ваш помощник в управлении бизнесом.

Что вы хотите сделать?
    """
    
    bot.reply_to(message, welcome_text, reply_markup=get_main_keyboard())
    
    # Check if user exists in database
    try:
        response = requests.get(f"{API_BASE}/user/{user_id}")
        if response.status_code == 404:
            # User doesn't exist, offer registration
            register_keyboard = types.InlineKeyboardMarkup()
            register_keyboard.add(
                types.InlineKeyboardButton("📝 Зарегистрироваться", callback_data="register")
            )
            bot.send_message(message.chat.id, 
                           "Для полного доступа к функциям необходимо зарегистрироваться.",
                           reply_markup=register_keyboard)
    except:
        pass

# Handle main menu buttons
@bot.message_handler(func=lambda message: message.text in ["🏪 Магазины", "📅 Мероприятия", "🤝 Партнеры", "📊 Статистика", "👤 Профиль", "❓ Помощь"])
def handle_main_menu(message):
    user_id = message.from_user.id
    
    if message.text == "🏪 Магазины":
        show_shops(message)
    elif message.text == "📅 Мероприятия":
        show_events(message)
    elif message.text == "🤝 Партнеры":
        show_partners(message)
    elif message.text == "📊 Статистика":
        show_statistics(message)
    elif message.text == "👤 Профиль":
        show_profile(message)
    elif message.text == "❓ Помощь":
        show_help(message)

# Show shops
def show_shops(message):
    try:
        response = requests.get(f"{API_BASE}/shops")
        shops = response.json()
        
        if not shops:
            bot.reply_to(message, "Пока нет доступных магазинов.")
            return
        
        text = "🏪 Доступные магазины:\n\n"
        for shop in shops[:5]:  # Show first 5 shops
            text += f"📦 {shop['name']}\n"
            if shop.get('description'):
                text += f"   {shop['description'][:50]}...\n"
            text += f"   ID: {shop['id']}\n\n"
        
        if len(shops) > 5:
            text += f"... и еще {len(shops) - 5} магазинов"
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("🔍 Найти магазин", callback_data="search_shop"),
            types.InlineKeyboardButton("📋 Все магазины", callback_data="all_shops")
        )
        
        bot.reply_to(message, text, reply_markup=keyboard)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки магазинов: {str(e)}")

# Show events
def show_events(message):
    try:
        response = requests.get(f"{API_BASE}/events")
        events = response.json()
        
        if not events:
            bot.reply_to(message, "Пока нет запланированных мероприятий.")
            return
        
        text = "📅 Ближайшие мероприятия:\n\n"
        for event in events[:3]:  # Show first 3 events
            date = datetime.strptime(event['date'], '%Y-%m-%d').strftime('%d.%m.%Y')
            text += f"🎯 {event['title']}\n"
            text += f"📅 {date} в {event['time']}\n"
            text += f"📍 {event['location']}\n"
            text += f"👥 {event['current_attendees']}/{event['max_attendees']} участников\n\n"
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("📅 Все мероприятия", callback_data="all_events"),
            types.InlineKeyboardButton("✅ Регистрация", callback_data="register_event")
        )
        
        bot.reply_to(message, text, reply_markup=keyboard)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки мероприятий: {str(e)}")

# Show partners
def show_partners(message):
    try:
        response = requests.get(f"{API_BASE}/partners")
        partners = response.json()
        
        if not partners:
            bot.reply_to(message, "Пока нет зарегистрированных партнеров.")
            return
        
        text = "🤝 Наши партнеры:\n\n"
        for partner in partners[:5]:  # Show first 5 partners
            text += f"👤 {partner['name']}\n"
            text += f"💼 {partner['role']}\n"
            if partner.get('company'):
                text += f"🏢 {partner['company']}\n"
            text += f"📊 {partner['projects_count']} проектов\n\n"
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("🤝 Стать партнером", callback_data="become_partner"),
            types.InlineKeyboardButton("📋 Все партнеры", callback_data="all_partners")
        )
        
        bot.reply_to(message, text, reply_markup=keyboard)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки партнеров: {str(e)}")

# Show statistics
def show_statistics(message):
    try:
        response = requests.get(f"{API_BASE}/dashboard/stats")
        stats = response.json()
        
        text = "📊 Статистика Commercio:\n\n"
        text += f"👥 Пользователей: {stats['total_users']}\n"
        text += f"🏪 Магазинов: {stats['total_shops']}\n"
        text += f"📦 Товаров: {stats['total_products']}\n"
        text += f"📅 Мероприятий: {stats['total_events']}\n"
        text += f"💰 Общий оборот: {stats['total_revenue']:,.0f} UZS\n"
        text += f"🎯 Предстоящих событий: {stats['upcoming_events']}\n"
        
        bot.reply_to(message, text)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки статистики: {str(e)}")

# Show profile
def show_profile(message):
    user_id = message.from_user.id
    
    try:
        response = requests.get(f"{API_BASE}/user/{user_id}")
        if response.status_code == 200:
            users = response.json()
            if users:
                user = users[0]
                text = f"👤 Профиль пользователя:\n\n"
                text += f"📝 Имя: {user['name']}\n"
                text += f"🎭 Роль: {user['role']}\n"
                if user.get('email'):
                    text += f"📧 Email: {user['email']}\n"
                if user.get('phone'):
                    text += f"📱 Телефон: {user['phone']}\n"
                text += f"📅 Регистрация: {user['created_at'][:10]}\n"
                
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    types.InlineKeyboardButton("✏️ Редактировать", callback_data="edit_profile"),
                    types.InlineKeyboardButton("📋 Мои заказы", callback_data="my_orders")
                )
                
                bot.reply_to(message, text, reply_markup=keyboard)
            else:
                bot.reply_to(message, "Профиль не найден.")
        else:
            bot.reply_to(message, "Для просмотра профиля необходимо зарегистрироваться.")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки профиля: {str(e)}")

# Show help
def show_help(message):
    help_text = """
❓ Помощь по использованию Commercio

🏪 Магазины - просмотр и поиск магазинов
📅 Мероприятия - информация о событиях и регистрация
🤝 Партнеры - список партнеров и возможности сотрудничества
📊 Статистика - общая статистика платформы
👤 Профиль - управление личным профилем

Команды:
/start - главное меню
/help - эта справка
/register - регистрация
/profile - профиль пользователя

По всем вопросам обращайтесь к администрации.
    """
    
    bot.reply_to(message, help_text)

# Handle callback queries
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "register":
        start_registration(call.message)
    elif call.data == "search_shop":
        search_shop(call.message)
    elif call.data == "all_shops":
        show_all_shops(call.message)
    elif call.data == "all_events":
        show_all_events(call.message)
    elif call.data == "register_event":
        register_for_event(call.message)
    elif call.data == "become_partner":
        become_partner(call.message)
    elif call.data == "all_partners":
        show_all_partners(call.message)
    elif call.data == "edit_profile":
        edit_profile(call.message)
    elif call.data == "my_orders":
        show_my_orders(call.message)
    
    bot.answer_callback_query(call.id)

# Registration flow
def start_registration(message):
    user_state = get_user_state(message.from_user.id)
    user_state.state = "registration_name"
    user_state.data = {}
    
    bot.reply_to(message, "📝 Регистрация в Commercio\n\nВведите ваше имя пользователя:")

@bot.message_handler(func=lambda message: get_user_state(message.from_user.id).state == "registration_name")
def handle_registration_name(message):
    user_state = get_user_state(message.from_user.id)
    user_state.data["name"] = message.text
    user_state.state = "registration_role"
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        types.KeyboardButton("Покупатель"),
        types.KeyboardButton("Продавец"),
        types.KeyboardButton("Партнер")
    )
    
    bot.reply_to(message, "Выберите вашу роль:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: get_user_state(message.from_user.id).state == "registration_role")
def handle_registration_role(message):
    user_state = get_user_state(message.from_user.id)
    
    role_map = {
        "Покупатель": "buyer",
        "Продавец": "seller", 
        "Партнер": "partner"
    }
    
    if message.text not in role_map:
        bot.reply_to(message, "Пожалуйста, выберите роль из предложенных вариантов.")
        return
    
    user_state.data["role"] = role_map[message.text]
    user_state.state = "registration_password"
    
    bot.reply_to(message, "Введите пароль (минимум 6 символов):", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: get_user_state(message.from_user.id).state == "registration_password")
def handle_registration_password(message):
    if len(message.text) < 6:
        bot.reply_to(message, "Пароль должен содержать минимум 6 символов. Попробуйте еще раз:")
        return
    
    user_state = get_user_state(message.from_user.id)
    user_state.data["password"] = message.text
    user_state.state = "registration_email"
    
    bot.reply_to(message, "Введите ваш email (необязательно, нажмите /skip для пропуска):")

@bot.message_handler(func=lambda message: get_user_state(message.from_user.id).state == "registration_email")
def handle_registration_email(message):
    user_state = get_user_state(message.from_user.id)
    
    if message.text == "/skip":
        user_state.data["email"] = ""
    else:
        user_state.data["email"] = message.text
    
    user_state.state = "registration_phone"
    bot.reply_to(message, "Введите ваш телефон (необязательно, нажмите /skip для пропуска):")

@bot.message_handler(func=lambda message: get_user_state(message.from_user.id).state == "registration_phone")
def handle_registration_phone(message):
    user_state = get_user_state(message.from_user.id)
    
    if message.text == "/skip":
        user_state.data["phone"] = ""
    else:
        user_state.data["phone"] = message.text
    
    # Complete registration
    complete_registration(message)

def complete_registration(message):
    user_state = get_user_state(message.from_user.id)
    user_data = user_state.data
    
    try:
        response = requests.post(f"{API_BASE}/user", json={
            "telegram_id": message.from_user.id,
            "name": user_data["name"],
            "role": user_data["role"],
            "password": user_data["password"],
            "email": user_data["email"],
            "phone": user_data["phone"]
        })
        
        if response.status_code == 201:
            bot.reply_to(message, 
                        f"✅ Регистрация успешна!\n\nДобро пожаловать в Commercio, {user_data['name']}!",
                        reply_markup=get_main_keyboard())
        else:
            error_data = response.json()
            if error_data.get("error") == "name taken":
                bot.reply_to(message, "❌ Имя пользователя уже занято. Попробуйте другое имя.")
            else:
                bot.reply_to(message, "❌ Ошибка регистрации. Попробуйте позже.")
        
        # Reset user state
        user_state.state = "main"
        user_state.data = {}
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка регистрации: {str(e)}")
        user_state.state = "main"
        user_state.data = {}

# Additional callback handlers
def search_shop(message):
    bot.reply_to(message, "🔍 Введите название магазина для поиска:")
    get_user_state(message.from_user.id).state = "searching_shop"

def show_all_shops(message):
    try:
        response = requests.get(f"{API_BASE}/shops")
        shops = response.json()
        
        if not shops:
            bot.reply_to(message, "Пока нет доступных магазинов.")
            return
        
        text = "🏪 Все магазины:\n\n"
        for i, shop in enumerate(shops, 1):
            text += f"{i}. {shop['name']}\n"
            if shop.get('description'):
                text += f"   {shop['description'][:50]}...\n"
            text += f"   ID: {shop['id']}\n\n"
        
        bot.reply_to(message, text)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки магазинов: {str(e)}")

def show_all_events(message):
    try:
        response = requests.get(f"{API_BASE}/events")
        events = response.json()
        
        if not events:
            bot.reply_to(message, "Пока нет запланированных мероприятий.")
            return
        
        text = "📅 Все мероприятия:\n\n"
        for i, event in enumerate(events, 1):
            date = datetime.strptime(event['date'], '%Y-%m-%d').strftime('%d.%m.%Y')
            text += f"{i}. {event['title']}\n"
            text += f"   📅 {date} в {event['time']}\n"
            text += f"   📍 {event['location']}\n"
            text += f"   👥 {event['current_attendees']}/{event['max_attendees']}\n\n"
        
        bot.reply_to(message, text)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки мероприятий: {str(e)}")

def register_for_event(message):
    bot.reply_to(message, "✅ Для регистрации на мероприятие перейдите на сайт Commercio или обратитесь к организатору.")

def become_partner(message):
    bot.reply_to(message, "🤝 Для получения статуса партнера свяжитесь с администрацией Commercio.")

def show_all_partners(message):
    try:
        response = requests.get(f"{API_BASE}/partners")
        partners = response.json()
        
        if not partners:
            bot.reply_to(message, "Пока нет зарегистрированных партнеров.")
            return
        
        text = "🤝 Все партнеры:\n\n"
        for i, partner in enumerate(partners, 1):
            text += f"{i}. {partner['name']}\n"
            text += f"   💼 {partner['role']}\n"
            if partner.get('company'):
                text += f"   🏢 {partner['company']}\n"
            text += f"   📊 {partner['projects_count']} проектов\n\n"
        
        bot.reply_to(message, text)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки партнеров: {str(e)}")

def edit_profile(message):
    bot.reply_to(message, "✏️ Для редактирования профиля перейдите на сайт Commercio.")

def show_my_orders(message):
    user_id = message.from_user.id
    
    try:
        response = requests.get(f"{API_BASE}/orders/{user_id}")
        if response.status_code == 200:
            orders = response.json()
            
            if not orders:
                bot.reply_to(message, "У вас пока нет заказов.")
                return
            
            text = "📋 Ваши заказы:\n\n"
            for order in orders[:5]:  # Show last 5 orders
                text += f"🛒 Заказ #{order['id']}\n"
                text += f"🏪 {order.get('shop_name', 'Неизвестный магазин')}\n"
                text += f"💰 {order['total_amount']:,.0f} UZS\n"
                text += f"📊 Статус: {order['status']}\n"
                text += f"📅 {order['created_at'][:10]}\n\n"
            
            if len(orders) > 5:
                text += f"... и еще {len(orders) - 5} заказов"
            
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, "Для просмотра заказов необходимо зарегистрироваться.")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка загрузки заказов: {str(e)}")

# Handle shop search
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id).state == "searching_shop")
def handle_shop_search(message):
    try:
        response = requests.get(f"{API_BASE}/shops")
        shops = response.json()
        
        search_term = message.text.lower()
        found_shops = [shop for shop in shops if search_term in shop['name'].lower()]
        
        if not found_shops:
            bot.reply_to(message, f"Магазины с названием '{message.text}' не найдены.")
        else:
            text = f"🔍 Результаты поиска '{message.text}':\n\n"
            for shop in found_shops:
                text += f"🏪 {shop['name']}\n"
                if shop.get('description'):
                    text += f"   {shop['description'][:50]}...\n"
                text += f"   ID: {shop['id']}\n\n"
            
            bot.reply_to(message, text)
        
        # Reset state
        get_user_state(message.from_user.id).state = "main"
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка поиска: {str(e)}")
        get_user_state(message.from_user.id).state = "main"

# Error handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Используйте кнопки меню для навигации или команду /help для справки.")

# Run bot
if __name__ == "__main__":
    print("Commercio Bot started...")
    bot.polling(none_stop=True) 