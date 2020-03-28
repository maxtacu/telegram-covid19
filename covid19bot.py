import config
import telebot
import logging
import sqlite3
import time

bot = telebot.TeleBot(config.telegram["token"])

conn = sqlite3.connect(config.database["filename"], check_same_thread=False)
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    cid = message.chat.id
    username = message.chat.username
    check_user(cid, username)
    if message.text == '/help':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Message the developer', url='telegram.me/maxtacu'
            )
        )
        help_text = config.telegram["helptext"]
        bot.send_message(cid, help_text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        help_text = config.telegram["helptext"]
        bot.send_message(cid, help_text, parse_mode="Markdown")


@bot.message_handler(commands=['stats'])
def stats(message):
    c = conn.cursor()
    with conn:
        cases, deaths, recovered, updated, active = c.execute("SELECT * FROM stats").fetchone()
    bot.send_message(message.chat.id, (f"*🦠 Total cases:* {cases} \n"
                                       f"*☠️ Deaths:* {deaths} \n"
                                       f"*☘️ Recovered:* {recovered} \n"
                                       f"*🤒 Active:* {active} \n"
                                       f"*⏰ Updated:* {time.ctime(updated)}"), parse_mode="Markdown")


def check_user(userid, username=None):
    c = conn.cursor()
    with conn:
        user = c.execute(f"""SELECT user_id FROM users WHERE user_id == '{userid}'""").fetchone()
    if not user:
        with conn:
            c.execute(f"INSERT INTO users VALUES ('{userid}', '{username}', '{time.strftime('%d-%m-%Y')}', NULL)")
        logger.info(f"New user detected {userid}-{username}")


def main():
    bot.polling(timeout=30)


if __name__ == '__main__':
    main()
