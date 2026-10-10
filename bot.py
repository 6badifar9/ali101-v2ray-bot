import os
import asyncio
from telegram import Bot


TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")

CONFIG_FILE = "configs.txt"
INDEX_FILE = "index.txt"


def load_configs():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f.readlines()
            if line.strip()
        ]


def get_index():
    with open(INDEX_FILE, "r") as f:
        return int(f.read().strip())


def save_index(index):
    with open(INDEX_FILE, "w") as f:
        f.write(str(index))


def detect_protocol(config):

    if config.startswith("vless://"):
        return "VLESS Reality"

    elif config.startswith("vmess://"):
        return "VMess"

    elif config.startswith("trojan://"):
        return "Trojan"

    elif config.startswith("ss://"):
        return "Shadowsocks"

    else:
        return "VPN"


def rename_config(config, name):

    # حذف remark قبلی
    if "#" in config:
        config = config.split("#")[0]

    # اضافه کردن نام Ali101
    return config + "#" + name



async def main():

    bot = Bot(token=TOKEN)

    configs = load_configs()

    index = get_index()


    # اگر رسید آخر دوباره از اول شروع شود
    if index >= len(configs):
        index = 0


    original_config = configs[index]


    config_name = f"Ali101-{index+101}"


    protocol = detect_protocol(original_config)


    config = rename_config(
        original_config,
        config_name
    )


    message = f"""
🚀 Ali 101 | Free V2Ray Config 🇮🇷

🔹 Config ID:
{config_name}

⚡ Protocol:
{protocol}

✅ Status:
Tested & Working

━━━━━━━━━━━━━━
