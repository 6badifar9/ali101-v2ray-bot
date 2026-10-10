import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")

bot = Bot(TOKEN)

with open("configs.txt","r") as f:
    configs = [x.strip() for x in f.readlines() if x.strip()]


async def send_config():

    for i, config in enumerate(configs):

        text = f"""
🚀 V2Ray Free Config 🇮🇷

⚡ VLESS Reality
🌍 Fast Server
✅ Tested & Working

```txt
{config}

  await bot.send_message(
    chat_id="@Ali101_free_V2ray",
    text="🚀 تست ربات Ali101 موفق بود ✅"
)

    break

    
