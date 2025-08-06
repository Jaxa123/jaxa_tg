# Complete Aiogram Telegram Bot Guide - From Zero to Restaurant Bot

## Table of Contents
1. [Getting Started](#getting-started)
2. [Environment Setup](#environment-setup)
3. [Creating Your First Bot](#creating-your-first-bot)
4. [Understanding Aiogram Basics](#understanding-aiogram-basics)
5. [Building a Restaurant Bot](#building-a-restaurant-bot)
6. [Advanced Features](#advanced-features)
7. [Deployment](#deployment)
8. [Extending to Other Projects](#extending-to-other-projects)

---

## Getting Started

### Step 1: Create a Bot with BotFather

1. **Open Telegram** and search for `@BotFather`
2. **Start a conversation** with BotFather by clicking "Start"
3. **Create a new bot** by sending: `/newbot`
4. **Choose a name** for your bot (e.g., "My Restaurant Bot")
5. **Choose a username** ending with "bot" (e.g., "myrestaurant_bot")
6. **Save your token** - BotFather will give you a token like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

⚠️ **Important**: Keep your token secret! Never share it publicly.

### Step 2: Optional Bot Settings

While talking to BotFather, you can also:
- Set bot description: `/setdescription`
- Set bot picture: `/setuserpic`
- Set commands menu: `/setcommands`

---

## Environment Setup

### Step 1: Install Python
Make sure you have Python 3.8+ installed. Check with:
```bash
python --version
```

### Step 2: Create Project Directory
```bash
mkdir my-telegram-bot
cd my-telegram-bot
```

### Step 3: Create Virtual Environment
```bash
# Create virtual environment
python -m venv bot_env

# Activate it
# On Windows:
bot_env\Scripts\activate
# On Mac/Linux:
source bot_env/bin/activate
```

### Step 4: Install Aiogram
```bash
pip install aiogram
```

### Step 5: Create Project Structure
```
my-telegram-bot/
├── bot.py              # Main bot file
├── config.py           # Configuration
├── handlers/           # Message handlers
│   ├── __init__.py
│   ├── start.py
│   └── menu.py
├── keyboards/          # Inline keyboards
│   ├── __init__.py
│   └── main_keyboard.py
├── database/           # Database (simple JSON for now)
│   └── data.json
└── requirements.txt    # Dependencies
```

Create these files and folders:
```bash
mkdir handlers keyboards database
touch bot.py config.py handlers/__init__.py handlers/start.py handlers/menu.py
touch keyboards/__init__.py keyboards/main_keyboard.py database/data.json
```

---

## Creating Your First Bot

### Step 1: Configuration (`config.py`)
```python
import os
from dataclasses import dataclass

@dataclass
class BotConfig:
    token: str
    admin_id: int  # Your Telegram user ID

# Get your token from environment variable or put it directly
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))  # Replace with your Telegram ID

config = BotConfig(
    token=BOT_TOKEN,
    admin_id=ADMIN_ID
)
```

**How to get your Telegram ID:**
1. Send a message to `@userinfobot`
2. It will reply with your user ID

### Step 2: Basic Bot Structure (`bot.py`)
```python
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from handlers import start, menu

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize Bot instance with default bot properties
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize Dispatcher
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
```

### Step 3: Start Handler (`handlers/start.py`)
```python
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_keyboard import get_main_keyboard

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"👋 Hello, {message.from_user.full_name}!\n"
        f"Welcome to our Restaurant Bot!\n\n"
        f"I can help you:\n"
        f"🍽️ Browse our menu\n"
        f"📞 Get contact information\n"
        f"📍 Find our location\n"
        f"⏰ Check opening hours",
        reply_markup=get_main_keyboard()
    )
```

### Step 4: Basic Keyboard (`keyboards/main_keyboard.py`)
```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽️ Menu", callback_data="menu"),
            InlineKeyboardButton(text="📞 Contact", callback_data="contact")
        ],
        [
            InlineKeyboardButton(text="📍 Location", callback_data="location"),
            InlineKeyboardButton(text="⏰ Hours", callback_data="hours")
        ]
    ])
    return keyboard
```

### Step 5: Menu Handler (`handlers/menu.py`)
```python
from aiogram import Router, types
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: CallbackQuery):
    menu_text = """
🍽️ <b>Our Menu</b>

<b>🍕 Pizza</b>
• Margherita - $12
• Pepperoni - $14
• Hawaiian - $15

<b>🍔 Burgers</b>
• Classic Burger - $10
• Cheese Burger - $11
• Veggie Burger - $9

<b>🥗 Salads</b>
• Caesar Salad - $8
• Greek Salad - $9
• Garden Salad - $7

<b>🥤 Drinks</b>
• Soft Drinks - $3
• Coffee - $4
• Fresh Juice - $5
    """
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "contact")
async def show_contact(callback: CallbackQuery):
    contact_text = """
📞 <b>Contact Information</b>

📱 Phone: +1 (555) 123-4567
📧 Email: info@restaurant.com
🌐 Website: www.restaurant.com

<b>Follow us:</b>
📘 Facebook: @restaurant
📷 Instagram: @restaurant
🐦 Twitter: @restaurant
    """
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "location")
async def show_location(callback: CallbackQuery):
    await callback.message.edit_text(
        "📍 <b>Our Location</b>\n\n"
        "123 Main Street\n"
        "City Center, State 12345\n\n"
        "We're located in the heart of downtown!",
        reply_markup=get_back_keyboard()
    )
    # You can also send actual location
    await callback.message.answer_location(
        latitude=40.7128,  # Replace with actual coordinates
        longitude=-74.0060
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "hours")
async def show_hours(callback: CallbackQuery):
    hours_text = """
⏰ <b>Opening Hours</b>

<b>Monday - Thursday:</b> 11:00 AM - 10:00 PM
<b>Friday - Saturday:</b> 11:00 AM - 11:00 PM
<b>Sunday:</b> 12:00 PM - 9:00 PM

<b>Kitchen closes 30 minutes before closing time</b>
    """
    
    await callback.message.edit_text(
        hours_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "back")
async def go_back(callback: CallbackQuery):
    from keyboards.main_keyboard import get_main_keyboard
    
    await callback.message.edit_text(
        f"👋 Welcome back!\n\n"
        f"What would you like to do?",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

def get_back_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="back")]
    ])
    return keyboard
```

### Step 6: Update handlers/__init__.py
```python
from . import start, menu

__all__ = ['start', 'menu']
```

### Step 7: Test Your Bot
1. **Add your bot token** to `config.py`
2. **Run the bot**:
```bash
python bot.py
```
3. **Test in Telegram** by sending `/start` to your bot

---

## Building a Restaurant Bot

Now let's expand our basic bot into a full-featured restaurant bot with ordering capabilities.

### Step 1: Enhanced Data Structure (`database/data.json`)
```json
{
  "menu": {
    "pizza": [
      {"id": 1, "name": "Margherita", "price": 12.00, "description": "Fresh tomatoes, mozzarella, basil"},
      {"id": 2, "name": "Pepperoni", "price": 14.00, "description": "Pepperoni, mozzarella, tomato sauce"},
      {"id": 3, "name": "Hawaiian", "price": 15.00, "description": "Ham, pineapple, mozzarella"}
    ],
    "burgers": [
      {"id": 4, "name": "Classic Burger", "price": 10.00, "description": "Beef patty, lettuce, tomato, onion"},
      {"id": 5, "name": "Cheese Burger", "price": 11.00, "description": "Beef patty, cheese, lettuce, tomato"},
      {"id": 6, "name": "Veggie Burger", "price": 9.00, "description": "Plant-based patty, lettuce, tomato"}
    ],
    "drinks": [
      {"id": 7, "name": "Coca Cola", "price": 3.00, "description": "Classic soft drink"},
      {"id": 8, "name": "Coffee", "price": 4.00, "description": "Fresh brewed coffee"},
      {"id": 9, "name": "Orange Juice", "price": 5.00, "description": "Fresh squeezed orange juice"}
    ]
  },
  "orders": {},
  "settings": {
    "delivery_fee": 2.50,
    "min_order": 15.00
  }
}
```

### Step 2: Database Helper (`database/db_helper.py`)
```python
import json
import os
from typing import Dict, List, Any

class DatabaseHelper:
    def __init__(self, db_file: str = "database/data.json"):
        self.db_file = db_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"menu": {}, "orders": {}, "settings": {}}
    
    def save_data(self):
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get_menu_category(self, category: str) -> List[Dict]:
        return self.data.get("menu", {}).get(category, [])
    
    def get_item_by_id(self, item_id: int) -> Dict:
        for category in self.data.get("menu", {}).values():
            for item in category:
                if item["id"] == item_id:
                    return item
        return {}
    
    def add_to_cart(self, user_id: int, item_id: int, quantity: int = 1):
        user_str = str(user_id)
        if user_str not in self.data["orders"]:
            self.data["orders"][user_str] = {"items": {}, "total": 0}
        
        if str(item_id) in self.data["orders"][user_str]["items"]:
            self.data["orders"][user_str]["items"][str(item_id)] += quantity
        else:
            self.data["orders"][user_str]["items"][str(item_id)] = quantity
        
        self.update_cart_total(user_id)
        self.save_data()
    
    def update_cart_total(self, user_id: int):
        user_str = str(user_id)
        total = 0
        if user_str in self.data["orders"]:
            for item_id, quantity in self.data["orders"][user_str]["items"].items():
                item = self.get_item_by_id(int(item_id))
                if item:
                    total += item["price"] * quantity
        
        self.data["orders"][user_str]["total"] = total
    
    def get_cart(self, user_id: int) -> Dict:
        return self.data["orders"].get(str(user_id), {"items": {}, "total": 0})
    
    def clear_cart(self, user_id: int):
        user_str = str(user_id)
        if user_str in self.data["orders"]:
            self.data["orders"][user_str] = {"items": {}, "total": 0}
            self.save_data()

# Global database instance
db = DatabaseHelper()
```

### Step 3: Enhanced Menu Handler (`handlers/menu.py`)
```python
from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db

router = Router()

@router.callback_query(F.data == "menu")
async def show_menu_categories(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍕 Pizza", callback_data="category_pizza"),
            InlineKeyboardButton(text="🍔 Burgers", callback_data="category_burgers")
        ],
        [
            InlineKeyboardButton(text="🥤 Drinks", callback_data="category_drinks"),
            InlineKeyboardButton(text="🛒 Cart", callback_data="cart")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data="back")
        ]
    ])
    
    await callback.message.edit_text(
        "🍽️ <b>Choose a category:</b>",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def show_category_items(callback: CallbackQuery):
    category = callback.data.split("_")[1]
    items = db.get_menu_category(category)
    
    if not items:
        await callback.answer("This category is empty!", show_alert=True)
        return
    
    keyboard_buttons = []
    text = f"🍽️ <b>{category.title()}</b>\n\n"
    
    for item in items:
        text += f"<b>{item['name']}</b> - ${item['price']:.2f}\n"
        text += f"<i>{item['description']}</i>\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"➕ Add {item['name']}", 
                callback_data=f"add_{item['id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    item = db.get_item_by_id(item_id)
    
    if not item:
        await callback.answer("Item not found!", show_alert=True)
        return
    
    db.add_to_cart(callback.from_user.id, item_id)
    
    await callback.answer(f"✅ {item['name']} added to cart!", show_alert=True)

@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    cart = db.get_cart(callback.from_user.id)
    
    if not cart["items"]:
        await callback.message.edit_text(
            "🛒 <b>Your cart is empty</b>\n\n"
            "Add some items from the menu!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🍽️ Browse Menu", callback_data="menu")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
            ])
        )
        await callback.answer()
        return
    
    text = "🛒 <b>Your Cart:</b>\n\n"
    total = 0
    
    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if item:
            item_total = item["price"] * quantity
            total += item_total
            text += f"<b>{item['name']}</b>\n"
            text += f"${item['price']:.2f} x {quantity} = ${item_total:.2f}\n\n"
    
    delivery_fee = db.data.get("settings", {}).get("delivery_fee", 2.50)
    text += f"<b>Subtotal:</b> ${total:.2f}\n"
    text += f"<b>Delivery:</b> ${delivery_fee:.2f}\n"
    text += f"<b>Total:</b> ${total + delivery_fee:.2f}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Checkout", callback_data="checkout"),
            InlineKeyboardButton(text="🗑️ Clear Cart", callback_data="clear_cart")
        ],
        [
            InlineKeyboardButton(text="🍽️ Add More Items", callback_data="menu"),
            InlineKeyboardButton(text="⬅️ Back", callback_data="back")
        ]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    db.clear_cart(callback.from_user.id)
    await callback.answer("🗑️ Cart cleared!", show_alert=True)
    await show_cart(callback)

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    cart = db.get_cart(callback.from_user.id)
    
    if not cart["items"]:
        await callback.answer("Your cart is empty!", show_alert=True)
        return
    
    # Here you would integrate with payment systems
    # For now, we'll just show order confirmation
    
    order_text = "🎉 <b>Order Confirmed!</b>\n\n"
    order_text += "📞 We'll call you shortly to confirm delivery details.\n"
    order_text += "⏱️ Estimated delivery: 30-45 minutes\n\n"
    order_text += "<b>Order Summary:</b>\n"
    
    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if item:
            order_text += f"• {item['name']} x{quantity}\n"
    
    delivery_fee = db.data.get("settings", {}).get("delivery_fee", 2.50)
    order_text += f"\n<b>Total: ${cart['total'] + delivery_fee:.2f}</b>"
    
    # Clear the cart after order
    db.clear_cart(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back")]
    ])
    
    await callback.message.edit_text(order_text, reply_markup=keyboard)
    await callback.answer()

# Keep the other handlers (contact, location, hours, back) from previous version
@router.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery):
    contact_text = """
📞 <b>Contact Information</b>

📱 Phone: +1 (555) 123-4567
📧 Email: info@restaurant.com
🌐 Website: www.restaurant.com

<b>Follow us:</b>
📘 Facebook: @restaurant
📷 Instagram: @restaurant
🐦 Twitter: @restaurant
    """
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "location")
async def show_location(callback: CallbackQuery):
    await callback.message.edit_text(
        "📍 <b>Our Location</b>\n\n"
        "123 Main Street\n"
        "City Center, State 12345\n\n"
        "We're located in the heart of downtown!",
        reply_markup=get_back_keyboard()
    )
    await callback.message.answer_location(
        latitude=40.7128,
        longitude=-74.0060
    )
    await callback.answer()

@router.callback_query(F.data == "hours")
async def show_hours(callback: CallbackQuery):
    hours_text = """
⏰ <b>Opening Hours</b>

<b>Monday - Thursday:</b> 11:00 AM - 10:00 PM
<b>Friday - Saturday:</b> 11:00 AM - 11:00 PM
<b>Sunday:</b> 12:00 PM - 9:00 PM

<b>Kitchen closes 30 minutes before closing time</b>
    """
    
    await callback.message.edit_text(
        hours_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery):
    from keyboards.main_keyboard import get_main_keyboard
    
    await callback.message.edit_text(
        f"👋 Welcome back, {callback.from_user.full_name}!\n\n"
        f"What would you like to do?",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="back")]
    ])
    return keyboard
```

### Step 4: Update Main Keyboard (`keyboards/main_keyboard.py`)
```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽️ Menu", callback_data="menu"),
            InlineKeyboardButton(text="🛒 My Cart", callback_data="cart")
        ],
        [
            InlineKeyboardButton(text="📞 Contact", callback_data="contact"),
            InlineKeyboardButton(text="📍 Location", callback_data="location")
        ],
        [
            InlineKeyboardButton(text="⏰ Hours", callback_data="hours")
        ]
    ])
    return keyboard
```

---

## Advanced Features

### Step 1: Admin Panel (`handlers/admin.py`)
```python
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import config
from database.db_helper import db

router = Router()

# Middleware to check if user is admin
def is_admin(user_id: int) -> bool:
    return user_id == config.admin_id

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats"),
            InlineKeyboardButton(text="📝 Orders", callback_data="admin_orders")
        ],
        [
            InlineKeyboardButton(text="🍽️ Manage Menu", callback_data="admin_menu"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings")
        ]
    ])
    
    await message.answer(
        "🔧 <b>Admin Panel</b>\n\n"
        "What would you like to manage?",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    # Calculate statistics
    total_users = len(db.data.get("orders", {}))
    total_orders = sum(1 for user_data in db.data.get("orders", {}).values() 
                      if user_data.get("items"))
    
    stats_text = f"""
📊 <b>Bot Statistics</b>

👥 <b>Total Users:</b> {total_users}
📦 <b>Active Carts:</b> {total_orders}
🍽️ <b>Menu Items:</b> {sum(len(category) for category in db.data.get("menu", {}).values())}

<b>Menu Categories:</b>
"""
    
    for category, items in db.data.get("menu", {}).items():
        stats_text += f"• {category.title()}: {len(items)} items\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(stats_text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats"),
            InlineKeyboardButton(text="📝 Orders", callback_data="admin_orders")
        ],
        [
            InlineKeyboardButton(text="🍽️ Manage Menu", callback_data="admin_menu"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings")
        ]
    ])
    
    await callback.message.edit_text(
        "🔧 <b>Admin Panel</b>\n\n"
        "What would you like to manage?",
        reply_markup=keyboard
    )
    await callback.answer()
```

### Step 2: Update Bot with Admin Handler (`bot.py`)
```python
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from handlers import start, menu, admin

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(admin.router)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
```

---

## Deployment

### Step 1: Create requirements.txt
```text
aiogram==3.1.1
```

### Step 2: Environment Variables
Create a `.env` file:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
```

### Step 3: Production Configuration
```python
# config.py - Updated for production
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    token: str
    admin_id: int
    webhook_url: str = None
    webhook_path: str = "/webhook"
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8000

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

config = BotConfig(
    token=BOT_TOKEN,
    admin_id=ADMIN_ID,
    webhook_url=WEBHOOK_URL
)
```

### Step 4: Webhook Bot for Production (`webhook_bot.py`)
```python
import asyncio
import logging
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import config
from handlers import start, menu, admin

# Configure logging
logging.basicConfig(level=logging.INFO)

async def on_startup(bot: Bot) -> None:
    # Set webhook
    await bot.set_webhook(f"{config.webhook_url}{config.webhook_path}")

def main() -> None:
    # Initialize Bot and Dispatcher
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Register startup function
    dp.startup.register(on_startup)
    
    # Register handlers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(admin.router)
    
    # Create aiohttp application
    app = web.Application()
    
    # Create SimpleRequestHandler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    # Register webhook handler on desired path
    webhook_requests_handler.register(app, path=config.webhook_path)
    
    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)
    
    # Start server
    web.run_app(app, host=config.webapp_host, port=config.webapp_port)

if __name__ == "__main__":
    main()
```

### Step 5: Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "webhook_bot.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - WEBHOOK_URL=${WEBHOOK_URL}
    volumes:
      - ./database:/app/database
    restart: unless-stopped
```

---

## Extending to Other Projects

### Business Types You Can Adapt This Bot For:

#### 1. **E-commerce Store**
```python
# Changes needed:
# - Replace menu categories with product categories
# - Add product images, sizes, colors
# - Integrate payment gateways
# - Add shipping options
# - Inventory management

# Example modifications:
def get_product_keyboard(product):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Size S", callback_data=f"size_{product['id']}_S"),
            InlineKeyboardButton(text="Size M", callback_data=f"size_{product['id']}_M"),
            InlineKeyboardButton(text="Size L", callback_data=f"size_{product['id']}_L")
        ],
        [
            InlineKeyboardButton(text="Add to Cart", callback_data=f"add_{product['id']}")
        ]
    ])
    return keyboard
```

#### 2. **Service Booking (Salon, Clinic, etc.)**
```python
# Changes needed:
# - Replace menu with services
# - Add appointment scheduling
# - Staff availability
# - Time slot management

# Example calendar integration:
from datetime import datetime, timedelta

def get_available_slots():
    slots = []
    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    for i in range(7):  # Next 7 days
        current_date = start_date + timedelta(days=i)
        for hour in range(9, 18):  # 9 AM to 6 PM
            slot_time = current_date.replace(hour=hour)
            slots.append({
                "datetime": slot_time,
                "available": True  # Check against bookings
            })
    
    return slots
```

#### 3. **Educational Course Platform**
```python
# Changes needed:
# - Replace menu with courses
# - Add lesson tracking
# - Progress monitoring
# - Certificate generation

# Example course structure:
course_data = {
    "courses": {
        "python": {
            "name": "Python Programming",
            "lessons": [
                {"id": 1, "title": "Variables and Data Types", "completed": False},
                {"id": 2, "title": "Control Structures", "completed": False},
                {"id": 3, "title": "Functions", "completed": False}
            ]
        }
    }
}
```

#### 4. **Hotel/Accommodation Booking**
```python
# Changes needed:
# - Replace menu with room types
# - Add date selection
# - Availability checking
# - Guest information collection

# Example room booking:
def get_room_availability(check_in, check_out, room_type):
    # Check database for availability
    # Return available rooms
    pass

def create_booking(user_id, room_id, check_in, check_out):
    booking = {
        "user_id": user_id,
        "room_id": room_id,
        "check_in": check_in,
        "check_out": check_out,
        "status": "confirmed"
    }
    # Save to database
    return booking
```

### Step-by-Step Adaptation Guide:

#### 1. **Identify Your Business Model**
- **Products/Services**: What are you selling?
- **User Journey**: How do customers interact with your business?
- **Payment Method**: How do customers pay?
- **Delivery/Fulfillment**: How is the service delivered?

#### 2. **Modify Data Structure**
```python
# Generic business data structure
business_data = {
    "categories": {
        "category_name": [
            {
                "id": 1,
                "name": "Item Name",
                "price": 0.00,
                "description": "Item description",
                "availability": True,
                "metadata": {}  # Store additional fields
            }
        ]
    },
    "customers": {},
    "orders": {},
    "settings": {
        "business_name": "Your Business",
        "currency": "$",
        "tax_rate": 0.08,
        "service_fee": 0.00
    }
}
```

#### 3. **Customize User Interface**
```python
# Generic main keyboard
def get_business_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛍️ Browse", callback_data="browse"),
            InlineKeyboardButton(text="🛒 My Orders", callback_data="orders")
        ],
        [
            InlineKeyboardButton(text="📞 Support", callback_data="support"),
            InlineKeyboardButton(text="ℹ️ About", callback_data="about")
        ]
    ])
    return keyboard
```

#### 4. **Add Business-Specific Features**

**For Subscription Services:**
```python
@router.message(Command("subscribe"))
async def handle_subscription(message: Message):
    plans = [
        {"name": "Basic", "price": 9.99, "features": ["Feature 1", "Feature 2"]},
        {"name": "Premium", "price": 19.99, "features": ["All Basic", "Feature 3", "Feature 4"]}
    ]
    
    keyboard_buttons = []
    text = "💎 <b>Choose Your Plan:</b>\n\n"
    
    for plan in plans:
        text += f"<b>{plan['name']} - ${plan['price']}/month</b>\n"
        for feature in plan['features']:
            text += f"✓ {feature}\n"
        text += "\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"Choose {plan['name']}", 
                callback_data=f"subscribe_{plan['name'].lower()}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer(text, reply_markup=keyboard)
```

**For Appointment Booking:**
```python
@router.callback_query(F.data == "book_appointment")
async def show_calendar(callback: CallbackQuery):
    # Generate calendar keyboard
    today = datetime.now()
    calendar_buttons = []
    
    # Create calendar for next 14 days
    for i in range(14):
        date = today + timedelta(days=i)
        if date.weekday() < 6:  # Monday to Saturday
            calendar_buttons.append([
                InlineKeyboardButton(
                    text=date.strftime("%d %b"),
                    callback_data=f"date_{date.strftime('%Y-%m-%d')}"
                )
            ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=calendar_buttons)
    await callback.message.edit_text(
        "📅 <b>Select a Date:</b>",
        reply_markup=keyboard
    )
```

#### 5. **Integration Examples**

**Payment Integration (Stripe):**
```python
import stripe

stripe.api_key = "your_stripe_secret_key"

async def create_payment_intent(amount, currency="usd"):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe uses cents
            currency=currency,
        )
        return intent
    except stripe.error.StripeError as e:
        return None
```

**Email Notifications:**
```python
import smtplib
from email.mime.text import MIMEText

async def send_order_confirmation(email, order_details):
    msg = MIMEText(f"Your order has been confirmed!\n\n{order_details}")
    msg['Subject'] = 'Order Confirmation'
    msg['From'] = 'your-email@business.com'
    msg['To'] = email
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@business.com', 'your-password')
        server.send_message(msg)
```

**Database Integration (PostgreSQL):**
```python
import asyncpg

class DatabaseManager:
    def __init__(self, database_url):
        self.database_url = database_url
    
    async def create_connection(self):
        return await asyncpg.connect(self.database_url)
    
    async def add_order(self, user_id, items, total):
        conn = await self.create_connection()
        try:
            order_id = await conn.fetchval(
                "INSERT INTO orders (user_id, items, total, created_at) "
                "VALUES ($1, $2, $3, NOW()) RETURNING id",
                user_id, json.dumps(items), total
            )
            return order_id
        finally:
            await conn.close()
```

### Step 6: **Testing Your Adapted Bot**

#### 1. **Create Test Data**
```python
# test_data.py
test_users = [
    {"id": 123456789, "first_name": "Test", "last_name": "User"},
    {"id": 987654321, "first_name": "Another", "last_name": "Tester"}
]

test_scenarios = [
    "User browsing products",
    "User adding items to cart",
    "User checking out",
    "User contacting support",
    "Admin viewing statistics"
]
```

#### 2. **Unit Testing**
```python
import unittest
from unittest.mock import AsyncMock, patch

class TestBotHandlers(unittest.TestCase):
    
    async def test_start_command(self):
        # Mock message object
        message = AsyncMock()
        message.from_user.full_name = "Test User"
        
        # Test start handler
        await start_handler(message)
        
        # Assert message.answer was called
        message.answer.assert_called_once()
        
        # Check if correct text was sent
        args, kwargs = message.answer.call_args
        self.assertIn("Welcome", args[0])
```

### Step 7: **Deployment Checklist**

- [ ] **Environment Variables Set**
  - BOT_TOKEN
  - ADMIN_ID
  - DATABASE_URL (if using external DB)
  - WEBHOOK_URL (for production)

- [ ] **Security Measures**
  - Token stored securely
  - Admin access restricted
  - Input validation implemented
  - Rate limiting added

- [ ] **Monitoring**
  - Error logging configured
  - Usage analytics setup
  - Performance monitoring

- [ ] **Backup Strategy**
  - Database backups automated
  - Code repository backed up
  - Configuration files secured

### Step 8: **Scaling Considerations**

```python
# For high-traffic bots, consider:

# 1. Database connection pooling
import asyncpg

async def create_pool():
    return await asyncpg.create_pool(
        database_url,
        min_size=10,
        max_size=20
    )

# 2. Redis for caching
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379")

async def cache_user_data(user_id, data):
    await redis_client.setex(f"user:{user_id}", 3600, json.dumps(data))

# 3. Queue system for heavy operations
from celery import Celery

celery_app = Celery('bot_tasks')

@celery_app.task
def send_bulk_notifications(user_ids, message):
    # Handle bulk operations asynchronously
    pass
```

---

## Conclusion

This guide provides you with a complete, production-ready Telegram bot using aiogram that can be adapted for virtually any business type. The restaurant bot example demonstrates all the core concepts you need:

- **User interaction flow**
- **Data management**
- **Admin functionality**
- **Error handling**
- **Scalability considerations**

### Next Steps:
1. **Deploy your bot** using the provided deployment methods
2. **Customize the data structure** for your specific business
3. **Add payment integration** for real transactions
4. **Implement advanced features** like analytics and reporting
5. **Scale your bot** as your business grows

### Key Takeaways:
- **aiogram is beginner-friendly** with clean, intuitive syntax
- **The bot structure is modular** and easy to extend
- **Business logic is separated** from bot handlers
- **The same pattern works** for any type of business
- **Production deployment** is straightforward with proper setup

Remember: Start simple, test thoroughly, and gradually add features as needed. This foundation will serve you well for any Telegram bot project!

---

## Resources

- **aiogram Documentation**: https://docs.aiogram.dev/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Python Async Programming**: https://docs.python.org/3/library/asyncio.html
- **BotFather Commands**: https://core.telegram.org/bots#6-botfather