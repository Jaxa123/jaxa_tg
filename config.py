import os
from dataclasses import dataclass

@dataclass
class BotConfig:
    token: str
    admin_id: int  # Your Telegram user ID

# Get your token from environment variable or put it directly
BOT_TOKEN = os.getenv('BOT_TOKEN', '8181220707:AAHt03llUwCNthyHDqbAwFz3X7oagdHagDM')
ADMIN_ID = int(os.getenv('ADMIN_ID', '1353229675'))  # Replace with your Telegram ID

config = BotConfig(
    token=BOT_TOKEN,
    admin_id=ADMIN_ID
)