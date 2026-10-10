import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode


TOKEN = os.getenv("BOT_TOKEN")

CHANNEL = "@Ali101_free_V2ray"


bot = Bot(TOKEN)


START_NUMBER = 101


def load_configs():

    with open("configs.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    configs = []

    for line in lines:
        line = line.strip()

        if line and (
            line.startswith("vless://")
            or line.startswith("vmess://")
            or line.startswith("trojan://")
        ):
            configs.append(line)

    return configs



def get_protocol(config):

    if config.startswith("vless://"):
        return "VLESS Reality"

    if config.startswith("vmess://"):
        return "VMess"

    if config.startswith("trojan://"):
        return "Trojan"

    return "Unknown"



async def send_configs():

    configs = load_configs()

    counter = START_NUMBER


    for i in range(0, len(configs), 5):

        batch = configs[i:i+5]


        text = (
            "🚀 <b>Ali101 Free VPN #V2ray</b>\n\n"
            "🔥 <b>Fresh Configs</b>\n"
            "✅ Tested & Working\n\n"
        )


        buttons = []


        for config in batch:

            name = f"Ali101-{counter}"

            protocol = get_protocol(config)


            text += (
                f"🔹 <b>{name}</b>\n"
                f"⚡ Protocol: {protocol}\n"
                f"📋 Copy button below\n\n"
            )


            buttons.append(
                [
                    InlineKeyboardButton(
                        f"📋 Copy {name}",
                        callback_data=f"copy_{counter}"
                    )
                ]
            )


            counter += 1



        text += (
            "━━━━━━━━━━━━━━\n"
            "📢 Channel:\n"
            f"{CHANNEL}\n\n"
            "#V2Ray #VLESS #Reality\n"
            "#FreeVPN #کانفیگ_رایگان"
        )


        await bot.send_message(
            chat_id=CHANNEL,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


        await asyncio.sleep(1200)



async def main():

    await send_configs()



if __name__ == "__main__":

    asyncio.run(main())
