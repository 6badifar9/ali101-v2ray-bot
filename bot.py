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
            x.strip()
            for x in f.readlines()
            if x.strip()
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

    protocols = [
        "vless://",
        "vmess://",
        "trojan://",
        "ss://"
    ]

    return any(
        config.startswith(p)
        for p in protocols
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


def rename_config(config, name):

    if "#" in config:
        config = config.split("#")[0]

    return config + "#" + name



async def main():

    bot = Bot(token=TOKEN)

    configs = load_configs()

    index = get_index()

    while index < len(configs):

        raw_config = configs[index]

        if is_valid_config(raw_config):
            break

        index += 1


    if index >= len(configs):
        index = 0
        raw_config = configs[0]


    config_name = f"Ali101-{index+101}"

    config = rename_config(
        raw_config,
        config_name
    )


    protocol = detect_protocol(config)


    message = (
        "🚀 Ali 101 | Free V2Ray Config 🇮🇷\n\n"

        f"🔹 Config ID:\n"
        f"{config_name}\n\n"

        f"⚡ Protocol:\n"
        f"{protocol}\n\n"

        "✅ Status:\n"
        "Checked & Working\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "```\n"
        f"{config}\n"
        "```\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "📱 Compatible:\n"
        "V2RayNG | V2Box | Nekoray\n\n"

        "🔥 Free V2Ray Config\n"
        "⚡ Fast Stable VPN\n"
        "🔄 Updated Daily\n\n"

        "📢 Channel:\n"
        "[ @Ali101_free_V2ray ]"
        "(https://t.me/Ali101_free_V2ray)\n\n"

        "#V2Ray #VLESS #Reality\n"
        "#FreeV2Ray #VPN\n"
        "#کانفیگ_رایگان\n\n"

        "🚀 Ali101 Free VPN"
    )


    await bot.send_message(
        chat_id=CHANNEL,
        text=message,
        parse_mode="Markdown"
    )


    save_index(index + 1)



asyncio.run(main())
