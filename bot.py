import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")


async def main():

    bot = Bot(token=TOKEN)

    text = """
🚀 تست ربات Ali101 موفق بود ✅

V2Ray Free Config Bot
"""

    await bot.send_message(
        chat_id=CHANNEL,
        text=text
    )


asyncio.run(main())
