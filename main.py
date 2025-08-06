import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    KeyboardButton, 
    ReplyKeyboardMarkup,
    InputMediaPhoto,
    FSInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройки бота
BOT_TOKEN = "8181220707:AAHt03llUwCNthyHDqbAwFz3X7oagdHagDM"  # Замените на ваш токен
ADMIN_IDS = [1353229675]  # ID администраторов (замените на реальные)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния FSM
class OrderStates(StatesGroup):
    selecting_category = State()
    selecting_item = State()
    entering_quantity = State()
    entering_address = State()
    entering_phone = State()
    confirming_order = State()

class AdminStates(StatesGroup):
    add_item_name = State()
    add_item_desc = State()
    add_item_price = State()
    add_item_image = State()
    add_item_category = State()
    edit_item = State()

# Модели данных
@dataclass
class MenuItem:
    id: int
    name: str
    description: str
    price: float
    category: str
    image_url: str = ""
    available: bool = True

@dataclass
class OrderItem:
    menu_item: MenuItem
    quantity: int
    
    @property
    def total_price(self) -> float:
        return self.menu_item.price * self.quantity

@dataclass
class Order:
    user_id: int
    username: str
    items: List[OrderItem]
    address: str
    phone: str
    payment_method: str
    total_amount: float
    order_time: str
    status: str = "pending"

# Хранилище данных в памяти
class DataStorage:
    def __init__(self):
        self.menu_items: List[MenuItem] = []
        self.orders: List[Order] = []
        self.user_carts: Dict[int, List[OrderItem]] = {}
        self.load_default_menu()
    
    def load_default_menu(self):
        """Загружаем стандартное меню"""
        default_items = [
            MenuItem(1, "🍕 Маргарита", "Классическая пицца с томатами, моцареллой и базиликом", 850, "🍕 Пицца", "https://via.placeholder.com/400x300/FF6347/FFFFFF?text=Маргарита"),
            MenuItem(2, "🍕 Пепперони", "Пицца с пепперони и сыром моцарелла", 950, "🍕 Пицца", "https://via.placeholder.com/400x300/FF4500/FFFFFF?text=Пепперони"),
            MenuItem(3, "🍔 Классический", "Сочный бургер с говядиной, салатом и томатом", 650, "🍔 Бургеры", "https://via.placeholder.com/400x300/8B4513/FFFFFF?text=Классический+Бургер"),
            MenuItem(4, "🍔 Чизбургер", "Бургер с двойным сыром и специальным соусом", 720, "🍔 Бургеры", "https://via.placeholder.com/400x300/FFD700/000000?text=Чизбургер"),
            MenuItem(5, "🍜 Борщ", "Традиционный украинский борщ со сметаной", 450, "🍜 Супы", "https://via.placeholder.com/400x300/DC143C/FFFFFF?text=Борщ"),
            MenuItem(6, "🍜 Солянка", "Мясная солянка с оливками и лимоном", 520, "🍜 Супы", "https://via.placeholder.com/400x300/B22222/FFFFFF?text=Солянка"),
            MenuItem(7, "🥗 Цезарь", "Салат с курицей, пармезаном и соусом цезарь", 680, "🥗 Салаты", "https://via.placeholder.com/400x300/32CD32/FFFFFF?text=Цезарь"),
            MenuItem(8, "🥗 Греческий", "Свежий салат с фетой, оливками и овощами", 580, "🥗 Салаты", "https://via.placeholder.com/400x300/228B22/FFFFFF?text=Греческий"),
            MenuItem(9, "☕ Эспрессо", "Классический итальянский кофе", 180, "☕ Напитки", "https://via.placeholder.com/400x300/8B4513/FFFFFF?text=Эспрессо"),
            MenuItem(10, "🧃 Свежевыжатый сок", "Апельсиновый сок собственного приготовления", 250, "☕ Напитки", "https://via.placeholder.com/400x300/FF8C00/FFFFFF?text=Сок"),
        ]
        self.menu_items = default_items
    
    def get_categories(self) -> List[str]:
        return list(set(item.category for item in self.menu_items if item.available))
    
    def get_items_by_category(self, category: str) -> List[MenuItem]:
        return [item for item in self.menu_items if item.category == category and item.available]
    
    def get_item_by_id(self, item_id: int) -> MenuItem:
        return next((item for item in self.menu_items if item.id == item_id), None)
    
    def add_item(self, item: MenuItem):
        # Генерируем новый ID
        max_id = max([item.id for item in self.menu_items], default=0)
        item.id = max_id + 1
        self.menu_items.append(item)
    
    def update_item(self, item: MenuItem):
        for i, existing_item in enumerate(self.menu_items):
            if existing_item.id == item.id:
                self.menu_items[i] = item
                break
    
    def delete_item(self, item_id: int):
        self.menu_items = [item for item in self.menu_items if item.id != item_id]
    
    def add_to_cart(self, user_id: int, item: MenuItem, quantity: int):
        if user_id not in self.user_carts:
            self.user_carts[user_id] = []
        
        # Проверяем, есть ли уже этот товар в корзине
        for cart_item in self.user_carts[user_id]:
            if cart_item.menu_item.id == item.id:
                cart_item.quantity += quantity
                return
        
        self.user_carts[user_id].append(OrderItem(item, quantity))
    
    def get_cart(self, user_id: int) -> List[OrderItem]:
        return self.user_carts.get(user_id, [])
    
    def clear_cart(self, user_id: int):
        if user_id in self.user_carts:
            self.user_carts[user_id] = []
    
    def remove_from_cart(self, user_id: int, item_id: int):
        if user_id in self.user_carts:
            self.user_carts[user_id] = [
                item for item in self.user_carts[user_id] 
                if item.menu_item.id != item_id
            ]
    
    def save_order(self, order: Order):
        self.orders.append(order)

# Глобальное хранилище
storage = DataStorage()

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Вспомогательные функции для клавиатур
def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🍽️ Меню", callback_data="menu"),
        InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ О ресторане", callback_data="about"),
        InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")
    )
    return builder.as_markup()

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для админов"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Добавить блюдо", callback_data="admin_add_item"),
        InlineKeyboardButton(text="📝 Управление меню", callback_data="admin_menu")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Заказы", callback_data="admin_orders"),
        InlineKeyboardButton(text="📈 Статистика", callback_data="admin_stats")
    )
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"))
    return builder.as_markup()

def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура категорий"""
    builder = InlineKeyboardBuilder()
    categories = storage.get_categories()
    for category in categories:
        builder.row(InlineKeyboardButton(text=category, callback_data=f"category_{category}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"))
    return builder.as_markup()

def get_items_keyboard(category: str) -> InlineKeyboardMarkup:
    """Клавиатура блюд категории"""
    builder = InlineKeyboardBuilder()
    items = storage.get_items_by_category(category)
    for item in items:
        builder.row(InlineKeyboardButton(
            text=f"{item.name} - {item.price}₽", 
            callback_data=f"item_{item.id}"
        ))
    builder.row(InlineKeyboardButton(text="◀️ К категориям", callback_data="menu"))
    return builder.as_markup()

def get_item_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для конкретного блюда"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Добавить в корзину", callback_data=f"add_to_cart_{item_id}"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Назад к меню", callback_data="menu"))
    return builder.as_markup()

def get_quantity_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора количества"""
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.add(InlineKeyboardButton(text=str(i), callback_data=f"quantity_{i}"))
    builder.adjust(5)
    builder.row(InlineKeyboardButton(text="◀️ Отмена", callback_data="menu"))
    return builder.as_markup()

def get_cart_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура корзины"""
    builder = InlineKeyboardBuilder()
    cart = storage.get_cart(user_id)
    
    if cart:
        for item in cart:
            builder.row(InlineKeyboardButton(
                text=f"❌ {item.menu_item.name} ({item.quantity}шт.)",
                callback_data=f"remove_from_cart_{item.menu_item.id}"
            ))
        builder.row(
            InlineKeyboardButton(text="🧹 Очистить корзину", callback_data="clear_cart"),
            InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")
        )
    
    builder.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu"))
    return builder.as_markup()

def get_payment_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура способов оплаты"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💳 Картой", callback_data="payment_card"),
        InlineKeyboardButton(text="💵 Наличными", callback_data="payment_cash")
    )
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="cart"))
    return builder.as_markup()

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления меню для админов"""
    builder = InlineKeyboardBuilder()
    categories = storage.get_categories()
    for category in categories:
        builder.row(InlineKeyboardButton(
            text=f"📝 {category}", 
            callback_data=f"admin_category_{category}"
        ))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel"))
    return builder.as_markup()

def get_admin_items_keyboard(category: str) -> InlineKeyboardMarkup:
    """Клавиатура блюд категории для админов"""
    builder = InlineKeyboardBuilder()
    items = storage.get_items_by_category(category)
    for item in items:
        builder.row(InlineKeyboardButton(
            text=f"✏️ {item.name}", 
            callback_data=f"admin_edit_item_{item.id}"
        ))
    builder.row(InlineKeyboardButton(text="◀️ К категориям", callback_data="admin_menu"))
    return builder.as_markup()

def get_edit_item_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура редактирования блюда"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_item_{item_id}"),
        InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_item_{item_id}")
    )
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu"))
    return builder.as_markup()

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Команда /start"""
    welcome_text = """🍽️ <b>Добро пожаловать в наш ресторан!</b>

Мы рады приветствовать вас в нашем уютном заведении! 
Здесь вы можете:

🍕 Просмотреть наше вкуснейшее меню
🛒 Добавить блюда в корзину  
📞 Оформить заказ с доставкой
💳 Выбрать удобный способ оплаты

<i>Приятного аппетита!</i> ✨"""
    
    await message.answer(
        welcome_text, 
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Команда /admin"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора!")
        return
    
    admin_text = """🔧 <b>Панель администратора</b>

Добро пожаловать в админ-панель!
Здесь вы можете управлять рестораном:

➕ Добавлять новые блюда
📝 Редактировать существующие
📊 Просматривать заказы
📈 Анализировать статистику"""

    await message.answer(
        admin_text,
        reply_markup=get_admin_keyboard(),
        parse_mode='HTML'
    )

# Обработчики callback-запросов
@dp.callback_query(F.data == "main_menu")
async def show_main_menu(callback: types.CallbackQuery):
    """Показать главное меню"""
    welcome_text = """🍽️ <b>Главное меню ресторана</b>

Выберите нужный раздел:"""
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data == "menu")
async def show_menu(callback: types.CallbackQuery, state: FSMContext):
    """Показать категории меню"""
    await state.set_state(OrderStates.selecting_category)
    
    menu_text = """🍽️ <b>Наше меню</b>

Выберите категорию блюд:"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=get_categories_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("category_"))
async def show_category_items(callback: types.CallbackQuery, state: FSMContext):
    """Показать блюда категории"""
    category = callback.data.split("category_")[1]
    await state.update_data(selected_category=category)
    await state.set_state(OrderStates.selecting_item)
    
    items = storage.get_items_by_category(category)
    if not items:
        await callback.answer("В этой категории пока нет блюд!", show_alert=True)
        return
    
    category_text = f"""🍽️ <b>{category}</b>

Выберите блюдо:"""
    
    await callback.message.edit_text(
        category_text,
        reply_markup=get_items_keyboard(category),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("item_"))
async def show_item_details(callback: types.CallbackQuery):
    """Показать детали блюда"""
    item_id = int(callback.data.split("item_")[1])
    item = storage.get_item_by_id(item_id)
    
    if not item:
        await callback.answer("Блюдо не найдено!", show_alert=True)
        return
    
    item_text = f"""🍽️ <b>{item.name}</b>

📝 <i>{item.description}</i>

💰 <b>Цена: {item.price}₽</b>

{'✅ В наличии' if item.available else '❌ Нет в наличии'}"""
    
    try:
        await callback.message.delete()
        if item.image_url:
            await callback.message.answer_photo(
                photo=item.image_url,
                caption=item_text,
                reply_markup=get_item_keyboard(item_id),
                parse_mode='HTML'
            )
        else:
            await callback.message.answer(
                item_text,
                reply_markup=get_item_keyboard(item_id),
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await callback.message.answer(
            item_text,
            reply_markup=get_item_keyboard(item_id),
            parse_mode='HTML'
        )
    
    await callback.answer()

@dp.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: types.CallbackQuery, state: FSMContext):
    """Добавить в корзину - выбор количества"""
    item_id = int(callback.data.split("add_to_cart_")[1])
    await state.update_data(selected_item_id=item_id)
    await state.set_state(OrderStates.entering_quantity)
    
    quantity_text = """🛒 <b>Добавление в корзину</b>

Выберите количество:"""
    
    await callback.message.edit_text(
        quantity_text,
        reply_markup=get_quantity_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("quantity_"))
async def process_quantity(callback: types.CallbackQuery, state: FSMContext):
    """Обработать выбранное количество"""
    quantity = int(callback.data.split("quantity_")[1])
    data = await state.get_data()
    item_id = data.get('selected_item_id')
    
    item = storage.get_item_by_id(item_id)
    if not item:
        await callback.answer("Ошибка! Блюдо не найдено.", show_alert=True)
        return
    
    storage.add_to_cart(callback.from_user.id, item, quantity)
    
    success_text = f"""✅ <b>Добавлено в корзину!</b>

🍽️ {item.name}
📦 Количество: {quantity}
💰 Сумма: {item.price * quantity}₽

Что делаем дальше?"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🛒 Перейти в корзину", callback_data="cart"),
        InlineKeyboardButton(text="🍽️ Продолжить выбор", callback_data="menu")
    )
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    
    await callback.message.edit_text(
        success_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await callback.answer()
    await state.clear()

@dp.callback_query(F.data == "cart")
async def show_cart(callback: types.CallbackQuery):
    """Показать корзину"""
    cart = storage.get_cart(callback.from_user.id)
    
    if not cart:
        empty_text = """🛒 <b>Ваша корзина пуста</b>

Добавьте блюда из нашего меню!"""
        
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🍽️ Перейти к меню", callback_data="menu"))
        builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
        
        await callback.message.edit_text(
            empty_text,
            reply_markup=builder.as_markup(),
            parse_mode='HTML'
        )
    else:
        total = sum(item.total_price for item in cart)
        cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
        
        for item in cart:
            cart_text += f"🍽️ <b>{item.menu_item.name}</b>\n"
            cart_text += f"   💰 {item.menu_item.price}₽ × {item.quantity} = {item.total_price}₽\n\n"
        
        cart_text += f"💳 <b>Общая сумма: {total}₽</b>"
        
        await callback.message.edit_text(
            cart_text,
            reply_markup=get_cart_keyboard(callback.from_user.id),
            parse_mode='HTML'
        )
    
    await callback.answer()

@dp.callback_query(F.data.startswith("remove_from_cart_"))
async def remove_from_cart(callback: types.CallbackQuery):
    """Удалить из корзины"""
    item_id = int(callback.data.split("remove_from_cart_")[1])
    storage.remove_from_cart(callback.from_user.id, item_id)
    
    await show_cart(callback)
    await callback.answer("Товар удален из корзины!")

@dp.callback_query(F.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    """Очистить корзину"""
    storage.clear_cart(callback.from_user.id)
    await show_cart(callback)
    await callback.answer("Корзина очищена!")

@dp.callback_query(F.data == "checkout")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    """Начать оформление заказа"""
    cart = storage.get_cart(callback.from_user.id)
    
    if not cart:
        await callback.answer("Корзина пуста!", show_alert=True)
        return
    
    await state.set_state(OrderStates.entering_address)
    
    address_text = """📍 <b>Оформление заказа</b>

Укажите адрес доставки:
<i>(например: ул. Пушкина, д. 10, кв. 5)</i>"""
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад к корзине", callback_data="cart"))
    
    await callback.message.edit_text(
        address_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.message(StateFilter(OrderStates.entering_address))
async def process_address(message: types.Message, state: FSMContext):
    """Обработать адрес"""
    await state.update_data(address=message.text)
    await state.set_state(OrderStates.entering_phone)
    
    phone_text = """📞 <b>Контактный телефон</b>

Укажите ваш номер телефона:
<i>(например: +7 (900) 123-45-67)</i>"""
    
    await message.answer(phone_text, parse_mode='HTML')

@dp.message(StateFilter(OrderStates.entering_phone))
async def process_phone(message: types.Message, state: FSMContext):
    """Обработать телефон"""
    await state.update_data(phone=message.text)
    
    payment_text = """💳 <b>Способ оплаты</b>

Выберите удобный способ оплаты:"""
    
    await message.answer(
        payment_text,
        reply_markup=get_payment_keyboard(),
        parse_mode='HTML'
    )

@dp.callback_query(F.data.startswith("payment_"))
async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """Обработать способ оплаты"""
    payment_method = "Картой" if callback.data == "payment_card" else "Наличными"
    await state.update_data(payment_method=payment_method)
    
    # Получаем данные заказа
    data = await state.get_data()
    cart = storage.get_cart(callback.from_user.id)
    total = sum(item.total_price for item in cart)
    
    # Формируем подтверждение заказа
    confirmation_text = f"""✅ <b>Подтверждение заказа</b>

👤 <b>Заказчик:</b> @{callback.from_user.username or 'Не указан'}
📍 <b>Адрес:</b> {data['address']}
📞 <b>Телефон:</b> {data['phone']}
💳 <b>Оплата:</b> {payment_method}

📋 <b>Ваш заказ:</b>
"""
    
    for item in cart:
        confirmation_text += f"• {item.menu_item.name} × {item.quantity} = {item.total_price}₽\n"
    
    confirmation_text += f"\n💰 <b>Итого: {total}₽</b>\n\n⏰ Время доставки: 30-45 минут"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cart")
    )
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    """Подтвердить заказ"""
    data = await state.get_data()
    cart = storage.get_cart(callback.from_user.id)
    total = sum(item.total_price for item in cart)
    
    # Создаем заказ
    order = Order(
        user_id=callback.from_user.id,
        username=callback.from_user.username or "Не указан",
        items=cart.copy(),
        address=data['address'],
        phone=data['phone'],
        payment_method=data['payment_method'],
        total_amount=total,
        order_time=datetime.now().strftime("%d.%m.%Y %H:%M")
    )
    
    storage.save_order(order)
    storage.clear_cart(callback.from_user.id)
    
    success_text = f"""🎉 <b>Заказ успешно оформлен!</b>

📋 <b>Номер заказа:</b> #{len(storage.orders)}
💰 <b>Сумма:</b> {total}₽
⏰ <b>Время доставки:</b> 30-45 минут

Спасибо за заказ! Мы свяжемся с вами в ближайшее время.

<i>Приятного аппетита!</i> 🍽️"""
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    
    await callback.message.edit_text(
        success_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    
    # Уведомление админов о новом заказе
    admin_notification = f"""🔔 <b>НОВЫЙ ЗАКАЗ!</b>

📋 <b>Заказ #{len(storage.orders)}</b>
👤 <b>Клиент:</b> @{order.username}
📍 <b>Адрес:</b> {order.address}
📞 <b>Телефон:</b> {order.phone}
💳 <b>Оплата:</b> {order.payment_method}
⏰ <b>Время:</b> {order.order_time}

📋 <b>Состав заказа:</b>
"""
    
    for item in order.items:
        admin_notification += f"• {item.menu_item.name} × {item.quantity} = {item.total_price}₽\n"
    
    admin_notification += f"\n💰 <b>Итого: {order.total_amount}₽</b>"
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_notification, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу {admin_id}: {e}")
    
    await callback.answer()
    await state.clear()

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    """Показать информацию о ресторане"""
    about_text = """ℹ️ <b>О нашем ресторане</b>

🍽️ <b>"Вкусное место"</b> - это уютный семейный ресторан, где каждое блюдо готовится с любовью и заботой о наших гостях.

🌟 <b>Наши преимущества:</b>
• Свежие и качественные продукты
• Быстрая доставка (30-45 минут)
• Большой выбор блюд на любой вкус
• Доступные цены
• Дружелюбный персонал

⏰ <b>Время работы:</b>
Ежедневно с 10:00 до 23:00

🚚 <b>Доставка:</b>
Бесплатная доставка от 1000₽
Платная доставка - 200₽"""
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu"))
    
    await callback.message.edit_text(
        about_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: types.CallbackQuery):
    """Показать контакты"""
    contacts_text = """📞 <b>Наши контакты</b>

📍 <b>Адрес:</b>
г. Ташкент, ул. Амира Темура, 15

📞 <b>Телефон:</b>
+998 90 123-45-67

📧 <b>Email:</b>
info@vkusnoe-mesto.uz

🌐 <b>Социальные сети:</b>
@vkusnoe_mesto - Telegram
@vkusnoe.mesto - Instagram

⏰ <b>Время работы:</b>
Пн-Вс: 10:00 - 23:00

🗺️ <i>Мы находимся в самом центре города!</i>"""
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu"))
    
    await callback.message.edit_text(
        contacts_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await callback.answer()

# Админские обработчики
@dp.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: types.CallbackQuery):
    """Показать админ-панель"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    admin_text = """🔧 <b>Панель администратора</b>

Управление рестораном:"""
    
    await callback.message.edit_text(
        admin_text,
        reply_markup=get_admin_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_add_item")
async def admin_add_item_start(callback: types.CallbackQuery, state: FSMContext):
    """Начать добавление нового блюда"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    await state.set_state(AdminStates.add_item_name)
    
    add_text = """➕ <b>Добавление нового блюда</b>

Введите название блюда:"""
    
    await callback.message.edit_text(add_text, parse_mode='HTML')
    await callback.answer()

@dp.message(StateFilter(AdminStates.add_item_name))
async def admin_add_item_name(message: types.Message, state: FSMContext):
    """Получить название блюда"""
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.add_item_desc)
    
    await message.answer("📝 Введите описание блюда:")

@dp.message(StateFilter(AdminStates.add_item_desc))
async def admin_add_item_desc(message: types.Message, state: FSMContext):
    """Получить описание блюда"""
    await state.update_data(description=message.text)
    await state.set_state(AdminStates.add_item_price)
    
    await message.answer("💰 Введите цену блюда (в рублях):")

@dp.message(StateFilter(AdminStates.add_item_price))
async def admin_add_item_price(message: types.Message, state: FSMContext):
    """Получить цену блюда"""
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await state.set_state(AdminStates.add_item_category)
        
        categories = storage.get_categories()
        category_text = f"📁 Выберите категорию или введите новую:\n\n"
        category_text += "Существующие категории:\n"
        for cat in categories:
            category_text += f"• {cat}\n"
        
        await message.answer(category_text)
    except ValueError:
        await message.answer("❌ Неверный формат цены! Введите число:")

@dp.message(StateFilter(AdminStates.add_item_category))
async def admin_add_item_category(message: types.Message, state: FSMContext):
    """Получить категорию блюда"""
    await state.update_data(category=message.text)
    await state.set_state(AdminStates.add_item_image)
    
    await message.answer("🖼️ Отправьте изображение блюда или введите 'пропустить':")

@dp.message(StateFilter(AdminStates.add_item_image))
async def admin_add_item_image(message: types.Message, state: FSMContext):
    """Получить изображение блюда"""
    data = await state.get_data()
    
    image_url = ""
    if message.photo:
        # В реальном боте здесь был бы код для загрузки изображения
        image_url = "https://via.placeholder.com/400x300/FFB6C1/000000?text=" + data['name']
    elif message.text and message.text.lower() != 'пропустить':
        image_url = message.text
    
    # Создаем новое блюдо
    new_item = MenuItem(
        id=0,  # ID будет присвоен автоматически
        name=data['name'],
        description=data['description'],
        price=data['price'],
        category=data['category'],
        image_url=image_url
    )
    
    storage.add_item(new_item)
    
    success_text = f"""✅ <b>Блюдо успешно добавлено!</b>

🍽️ <b>Название:</b> {new_item.name}
📝 <b>Описание:</b> {new_item.description}
💰 <b>Цена:</b> {new_item.price}₽
📁 <b>Категория:</b> {new_item.category}"""
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_panel"))
    
    await message.answer(
        success_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await state.clear()

@dp.callback_query(F.data == "admin_menu")
async def admin_show_menu(callback: types.CallbackQuery):
    """Показать меню для администратора"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    menu_text = """📝 <b>Управление меню</b>

Выберите категорию для редактирования:"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=get_admin_menu_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_category_"))
async def admin_show_category_items(callback: types.CallbackQuery):
    """Показать блюда категории для администратора"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    category = callback.data.split("admin_category_")[1]
    
    items_text = f"""📝 <b>Управление категорией: {category}</b>

Выберите блюдо для редактирования:"""
    
    await callback.message.edit_text(
        items_text,
        reply_markup=get_admin_items_keyboard(category),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_edit_item_"))
async def admin_edit_item_menu(callback: types.CallbackQuery):
    """Показать меню редактирования блюда"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    item_id = int(callback.data.split("admin_edit_item_")[1])
    item = storage.get_item_by_id(item_id)
    
    if not item:
        await callback.answer("Блюдо не найдено!", show_alert=True)
        return
    
    edit_text = f"""✏️ <b>Редактирование блюда</b>

🍽️ <b>Название:</b> {item.name}
📝 <b>Описание:</b> {item.description}
💰 <b>Цена:</b> {item.price}₽
📁 <b>Категория:</b> {item.category}
{'✅ В наличии' if item.available else '❌ Нет в наличии'}"""
    
    await callback.message.edit_text(
        edit_text,
        reply_markup=get_edit_item_keyboard(item_id),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("delete_item_"))
async def admin_delete_item(callback: types.CallbackQuery):
    """Удалить блюдо"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    item_id = int(callback.data.split("delete_item_")[1])
    item = storage.get_item_by_id(item_id)
    
    if not item:
        await callback.answer("Блюдо не найдено!", show_alert=True)
        return
    
    storage.delete_item(item_id)
    
    await callback.answer(f"✅ Блюдо '{item.name}' удалено!")
    
    # Возвращаемся к управлению меню
    await admin_show_menu(callback)

@dp.callback_query(F.data == "admin_orders")
async def admin_show_orders(callback: types.CallbackQuery):
    """Показать заказы"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    orders = storage.orders
    
    if not orders:
        orders_text = """📊 <b>Заказы</b>

Пока нет заказов."""
    else:
        orders_text = f"📊 <b>Последние заказы ({len(orders)})</b>\n\n"
        
        # Показываем последние 5 заказов
        for i, order in enumerate(reversed(orders[-5:]), 1):
            orders_text += f"<b>#{len(orders) - i + 1}</b> @{order.username}\n"
            orders_text += f"💰 {order.total_amount}₽ | {order.payment_method}\n"
            orders_text += f"⏰ {order.order_time} | {order.status}\n\n"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Админ-панель", callback_data="admin_panel"))
    
    await callback.message.edit_text(
        orders_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_stats")
async def admin_show_stats(callback: types.CallbackQuery):
    """Показать статистику"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    orders = storage.orders
    total_orders = len(orders)
    total_revenue = sum(order.total_amount for order in orders)
    
    # Статистика по категориям
    category_stats = {}
    for order in orders:
        for item in order.items:
            category = item.menu_item.category
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += item.quantity
    
    stats_text = f"""📈 <b>Статистика ресторана</b>

📊 <b>Общая статистика:</b>
• Всего заказов: {total_orders}
• Общая выручка: {total_revenue}₽
• Среднее на заказ: {total_revenue/max(total_orders, 1):.2f}₽

🍽️ <b>Популярные категории:</b>
"""
    
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        stats_text += f"• {category}: {count} заказов\n"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Админ-панель", callback_data="admin_panel"))
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await callback.answer()

# Обработчик неизвестных callback-запросов
@dp.callback_query()
async def unknown_callback(callback: types.CallbackQuery):
    """Обработчик неизвестных callback-запросов"""
    await callback.answer("❌ Неизвестная команда!")

# Обработчик текстовых сообщений вне состояний
@dp.message()
async def handle_text(message: types.Message):
    """Обработка текстовых сообщений"""
    help_text = """❓ <b>Помощь</b>

Используйте кнопки в меню для навигации по боту.

📝 <b>Доступные команды:</b>
/start - Главное меню
/admin - Панель администратора (только для админов)

Для заказа используйте кнопку "🍽️ Меню"."""
    
    await message.answer(
        help_text,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

# Основная функция запуска
async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск ресторанного бота...")
    
    # Устанавливаем команды бота
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🏠 Главное меню"),
        types.BotCommand(command="admin", description="🔧 Панель администратора"),
    ])
    
    # Запускаем поллинг
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")