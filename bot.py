import os
import asyncio
from telegram import Bot


TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")


CONFIG_FILE = "configs.txt"
INDEX_FILE = "index.txt"


def get_index():
    with open(INDEX_FILE, "r") as f:
        return int(f.read().strip())


def save_index(index):
    with open(INDEX_FILE, "w") as f:
        f.write(str(index))


def load_configs():
    with open(CONFIG_FILE, "r") as f:
        return [
            x.strip()
            for x in f.readlines()
            if x.strip()
        ]


async def send_config():

    bot = Bot(token=TOKEN)

    configs = load_configs()

    index = get_index()

    if index >= len(configs):
        index = 0


    config = configs[index]


    # حذف نام قبلی کانفیگ
    if "#" in config:
        config = config.split("#")[0]


    config_name = f"Ali101-{index+101}"


    # اضافه کردن نام برند
    config = config + "#" + config_name


    text = f"""
🚀 Ali 101 | V2Ray Free Config 🇮🇷

🔹 Config ID: {config_name}

⚡ Protocol: VLESS / VMess / Reality
✅ Status: Tested & Working

━━━━━━━━━━━━━━

```txt
{config}
