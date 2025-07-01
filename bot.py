import asyncio
import requests
import bcrypt
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
)

API_TOKEN = "7985144948:AAHAbF3p4TifpfI_NRwFSWTDJQEWvhwX4Es"
BACKEND_API_URL = "http://localhost:8000/api"
TASHMALL_WEBAPP_URL = "https://tashmall-project.vercel.app/"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def api_get_users_by_telegram_id(telegram_id):
    resp = requests.get(f"{BACKEND_API_URL}/user/{telegram_id}")
    if resp.status_code == 200:
        users = resp.json()
        if isinstance(users, list):
            return users
        return []
    return []

def api_get_user_by_username(username):
    resp = requests.get(f"{BACKEND_API_URL}/user_by_username/{username}")
    if resp.status_code == 200:
        return resp.json()
    return None

def api_create_user(telegram_id, name, password, role):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    resp = requests.post(f"{BACKEND_API_URL}/user", json={
        "telegram_id": telegram_id, "name": name, "role": role, "password": hashed
    })
    return resp.status_code == 201

def api_delete_user(telegram_id):
    resp = requests.delete(f"{BACKEND_API_URL}/user/{telegram_id}")
    return resp.status_code == 204

def api_check_password(username, password):
    user = api_get_user_by_username(username)
    if not user or 'password' not in user:
        return False, None
    return bcrypt.checkpw(password.encode(), user['password'].encode()), user

def api_create_shop(owner_telegram_id, name):
    resp = requests.post(f"{BACKEND_API_URL}/shops", json={
        "owner_telegram_id": owner_telegram_id,
        "name": name
    })
    return resp.status_code == 201

def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Зарегистрироваться"), KeyboardButton(text="Войти")]
        ],
        resize_keyboard=True
    )

def account_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Удалить аккаунт'), KeyboardButton(text='Выйти')]
        ],
        resize_keyboard=True
    )

def role_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Я покупатель'), KeyboardButton(text='Я продавец')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def seller_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛒 Tashmall", web_app=WebAppInfo(url=TASHMALL_WEBAPP_URL))
        ],
        [
            InlineKeyboardButton(text="➕ Создать магазин", callback_data="create_shop"),
            InlineKeyboardButton(text="📋 Мои магазины", callback_data="my_shops")
        ]
    ])

def buyer_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛒 Tashmall", web_app=WebAppInfo(url=TASHMALL_WEBAPP_URL))
        ],
        [
            InlineKeyboardButton(text="🔍 Найти товар", callback_data="find_product"),
            InlineKeyboardButton(text="🏬 Смотреть магазины", callback_data="see_shops")
        ]
    ])

user_state = {}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    users = api_get_users_by_telegram_id(telegram_id)
    state = user_state.get(telegram_id, {})
    if users and not state.get("auth", False):
        names = ", ".join([u['name'] for u in users])
        await message.answer(
            f"👋 Добро пожаловать обратно в Tashmall!\n\nПохоже, у вас уже есть аккаунты: {names}\nВойдите снова или создайте новый профиль, чтобы продолжить удивительное путешествие по миру покупок!",
            reply_markup=start_keyboard()
        )
        return
    if users and state.get("auth", False):
        user = users[0]
        await message.answer(
            f"🎉 С возвращением, {user['name']}!\nВаша роль: {user['role']}\n\nГотовы к новым возможностям?",
            reply_markup=account_keyboard()
        )
        await show_role_menu(message, user['role'])
        return
    await message.answer(
        "✨ Приветствуем в Tashmall — магазине новых открытий!\n\nГотовы зарегистрироваться или войти? Выберите действие ниже:",
        reply_markup=start_keyboard()
    )

@dp.message(lambda m: m.text == "Удалить аккаунт")
async def delete_account(message: types.Message):
    telegram_id = message.from_user.id
    ok = api_delete_user(telegram_id)
    user_state.pop(telegram_id, None)
    if ok:
        await message.answer("Ваши аккаунты удалены.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Ошибка при удалении аккаунта.")

@dp.message(lambda m: m.text == "Выйти")
async def logout(message: types.Message):
    telegram_id = message.from_user.id
    user_state[telegram_id] = {"auth": False}
    await message.answer("Вы успешно вышли из аккаунта.", reply_markup=ReplyKeyboardRemove())

@dp.message(lambda m: m.text == "Зарегистрироваться")
async def registration_start(message: types.Message):
    telegram_id = message.from_user.id
    users = api_get_users_by_telegram_id(telegram_id)
    state = user_state.get(telegram_id, {})
    if users and state.get("auth", False):
        user = users[0]
        await message.answer("У вас уже есть аккаунт!", reply_markup=account_keyboard())
        await show_role_menu(message, user['role'])
        return
    if len(users) >= 3:
        await message.answer("Вы уже создали максимальное количество аккаунтов (3) для этого Telegram ID.")
        return
    user_state[telegram_id] = {"step": "register_name"}
    await message.answer("Введите ваше имя пользователя для регистрации:")

@dp.message(lambda m: m.text == "Войти")
async def login_start(message: types.Message):
    telegram_id = message.from_user.id
    user_state[telegram_id] = {"step": "login_name"}
    await message.answer("Введите имя пользователя:")

async def show_role_menu(message, role):
    if role == "seller":
        await message.answer(
            "Меню продавца:\n— Создавайте магазины\n— Управляйте товарами\n— Смотрите свои магазины",
            reply_markup=seller_menu()
        )
    else:
        await message.answer(
            "Меню покупателя:\n— Ищите товары\n— Просматривайте магазины\n— Оформляйте покупки",
            reply_markup=buyer_menu()
        )

@dp.callback_query(lambda c: c.data == "create_shop")
async def create_shop_callback(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    user_state[telegram_id] = {"step": "shop_name"}
    await callback.message.answer("Для создания магазина введите его название текстом:")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "my_shops")
async def my_shops_callback(callback: types.CallbackQuery):
    await callback.message.answer("Здесь будет список ваших магазинов.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "find_product")
async def find_product_callback(callback: types.CallbackQuery):
    await callback.message.answer("Введите название товара для поиска:")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "see_shops")
async def see_shops_callback(callback: types.CallbackQuery):
    await callback.message.answer("Здесь будет список всех магазинов.")
    await callback.answer()

@dp.message()
async def global_handler(message: types.Message):
    telegram_id = message.from_user.id
    st = user_state.get(telegram_id, {})
    step = st.get("step")

    if step == "register_name":
        if api_get_user_by_username(message.text):
            await message.answer("Это имя уже занято, попробуйте другое:")
            return
        st["name"] = message.text
        st["step"] = "register_password"
        user_state[telegram_id] = st
        await message.answer("Придумайте пароль:")
        return

    if step == "register_password":
        st["password"] = message.text
        st["step"] = "register_role"
        user_state[telegram_id] = st
        await message.answer("Выберите роль:", reply_markup=role_keyboard())
        return

    if step == "register_role":
        if message.text not in ["Я покупатель", "Я продавец"]:
            await message.answer("Пожалуйста, выберите роль с клавиатуры.")
            return
        role = "buyer" if message.text == "Я покупатель" else "seller"
        st["role"] = role
        ok = api_create_user(
            telegram_id=telegram_id,
            name=st["name"],
            password=st["password"],
            role=role
        )
        if ok:
            user_state[telegram_id] = {"auth": True}
            await message.answer("Регистрация успешна! Добро пожаловать в Tashmall.", reply_markup=account_keyboard())
            await show_role_menu(message, role)
        else:
            user_state.pop(telegram_id, None)
            await message.answer("Ошибка регистрации. Возможно, вы уже создали 3 аккаунта или имя занято. Попробуйте снова /start.")
        return

    if step == "login_name":
        st["name"] = message.text
        st["step"] = "login_password"
        user_state[telegram_id] = st
        await message.answer("Введите пароль:")
        return

    if step == "login_password":
        username = st.get("name")
        password = message.text
        success, user = api_check_password(username, password)
        if success:
            user_state[telegram_id] = {"auth": True}
            await message.answer(
                f"Вы успешно вошли!\nИмя: {user['name']}\nРоль: {user['role']}",
                reply_markup=account_keyboard()
            )
            await show_role_menu(message, user['role'])
        else:
            user_state[telegram_id] = {"auth": False}
            await message.answer("Имя пользователя или пароль неверны. Попробуйте снова /start.")
        return

    if step == "shop_name":
        shop_name = message.text.strip()
        ok = api_create_shop(telegram_id, shop_name)
        if ok:
            await message.answer(f'Магазин "{shop_name}" успешно создан!')
        else:
            await message.answer("Ошибка при создании магазина.")
        user_state[telegram_id] = {"auth": True}
        return

    # Если ни одно состояние не подошло
    await message.answer("Неизвестная команда или не выбрана операция. Используйте /start.")

async def main():
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем (Ctrl+C)")