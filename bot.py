import os
import asyncio
from telegram import Bot


TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")

CONFIG_FILE = "configs.txt"
INDEX_FILE = "index.txt"


def load_configs():
    with open(CONFIG_FILE, "r") as f:
        return [x.strip() for x in f.readlines() if x.strip()]


def get_index():
    with open(INDEX_FILE, "r") as f:
        return int(f.read())


def save_index(index):
    with open(INDEX_FILE, "w") as f:
        f.write(str(index))


async def main():

    bot = Bot(token=TOKEN)

    configs = load_configs()

    index = get_index()

    if index >= len(configs):
        index = 0


    config = configs[index]

    if "#" in config:
        config = config.split("#")[0]


    name = f"Ali101-{index+101}"

    config = config + "#" + name


    text = (
        f"🚀 Ali 101 | V2Ray Free Config 🇮🇷\n\n"
        f"🔹 Config ID: {name}\n\n"
        f"⚡ Protocol: VLESS / VMess / Reality\n"
        f"✅ Status: Tested & Working\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{config}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📱 V2RayNG Compatible\n\n"
        f"#V2Ray #VLESS #Reality\n"
        f"#کانفیگ_رایگان #VPN\n\n"
        f"👤 Ali 101"
    )


    await bot.send_message(
        chat_id=CHANNEL,
        text=text
    )


    save_index(index + 1)


asyncio.run(main())
