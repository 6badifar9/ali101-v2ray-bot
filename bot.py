import os
import asyncio
from telegram import Bot


TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")

CONFIG_FILE = "configs.txt"
INDEX_FILE = "index.txt"


def load_configs():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return [x.strip() for x in f.readlines() if x.strip()]


def get_index():
    with open(INDEX_FILE, "r") as f:
        return int(f.read().strip())


def save_index(index):
    with open(INDEX_FILE, "w") as f:
        f.write(str(index))


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

    if index >= len(configs):
        index = 0


    config_name = "Ali101-" + str(index + 101)

    config = rename_config(
        configs[index],
        config_name
    )


    protocol = detect_protocol(config)


    message = (
        "🚀 Ali 101 | Free V2Ray Config 🇮🇷\n\n"
        "🔹 Config ID:\n"
        + config_name +
        "\n\n"
        "⚡ Protocol:\n"
        + protocol +
        "\n\n"
        "✅ Status:\n"
        "Tested & Working\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "```\n"
        + config +
        "\n```\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📱 Compatible:\n"
        "V2RayNG | V2Box | Nekoray\n\n"
        "🔥 Free V2Ray Config\n"
        "⚡ Fast Stable VPN\n"
        "🔄 Updated Daily\n\n"
        "#V2Ray #VLESS #VMess #Reality\n"
        "#FreeV2Ray #VPN\n"
        "#کانفیگ_رایگان #کانفیگ_واقعی\n\n"
        "👤 Ali 101"
    )


    await bot.send_message(
        chat_id=CHANNEL,
        text=message,
        parse_mode="Markdown"
    )


    save_index(index + 1)



asyncio.run(main())
