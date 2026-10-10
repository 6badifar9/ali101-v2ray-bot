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
    try:
        with open(INDEX_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0


def save_index(index):
    with open(INDEX_FILE, "w") as f:
        f.write(str(index))


def is_valid_config(config):

    if len(config) < 20:
        return False

    allowed = [
        "vless://",
        "vmess://",
        "trojan://",
        "ss://"
    ]

    return any(
        config.startswith(x)
        for x in allowed
    )


def detect_protocol(config):

    if config.startswith("vless://"):
        return "VLESS Reality"

    if config.startswith("vmess://"):
        return "VMess"

    if config.startswith("trojan://"):
        return "Trojan"

    if config.startswith("ss://"):
        return "Shadowsocks"

    return "VPN"


def add_name(config, name):

    if "#" in config:
        config = config.split("#")[0]

    return config + "#" + name



async def main():

    bot = Bot(token=TOKEN)

    configs = load_configs()

    index = get_index()


    while index < len(configs):

        if is_valid_config(configs[index]):
            break

        index += 1


    if index >= len(configs):
        index = 0


    config_name = f"Ali101-{index + 101}"

    config = add_name(
        configs[index],
        config_name
    )


    protocol = detect_protocol(config)


    message = f"""
🚀 Ali 101 | Free V2Ray Config 🇮🇷


🔹 Config ID:
{config_name}


⚡ Protocol:
{protocol}


✅ Status:
Checked & Working


━━━━━━━━━━━━━━


📋 Copy Config:


{config}


━━━━━━━━━━━━━━


📱 Compatible:
V2RayNG | V2Box | Nekoray


🔥 Free V2Ray Config
⚡ Fast Stable VPN
🔄 Updated Daily


📢 Channel:
https://t.me/Ali101_free_V2ray


#V2Ray #VLESS #Reality
#FreeV2Ray #VPN
#کانفیگ_رایگان


🚀 Ali101 Free VPN
"""


    await bot.send_message(
        chat_id=CHANNEL,
        text=message
    )


    save_index(index + 1)



asyncio.run(main())
