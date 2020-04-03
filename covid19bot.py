#!/usr/bin/python

import config
import telebot
import logging
import sqlite3
import time
from datetime import datetime

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
    language = language_check(cid)
    help_text = config.translations[language]["help"]
    if message.text == '/help':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                config.translations[language]["dm"], url='telegram.me/maxtacu'
            )
        )
        bot.send_message(cid, help_text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        bot.send_message(cid, help_text, parse_mode="Markdown")
        language_pick_buttons(message, language)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
   data = query.data
   if data.startswith('lang-'):
        user_language_update(query.data, query.message.chat.id)
        language = language_check(query.message.chat.id)
        bot.answer_callback_query(query.id, config.translations[language]["pick"])
        

def user_language_update(language, user):
    c = conn.cursor()
    with conn:
        c.execute(f"UPDATE users SET language='{language}' WHERE user_id=={user}")


def language_pick_buttons(message, language):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('English', callback_data='lang-eng'),
        telebot.types.InlineKeyboardButton('Русский', callback_data='lang-ru'),
        telebot.types.InlineKeyboardButton('Español', callback_data='lang-es')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Português', callback_data='lang-pt'),
        telebot.types.InlineKeyboardButton('Română', callback_data='lang-ro')
    )
    bot.send_message(message.chat.id, config.translations[language]["pickrequest"], parse_mode="Markdown", reply_markup=keyboard)


def language_check(userid):
    c = conn.cursor()
    with conn:
        language = c.execute(f"""SELECT language FROM users WHERE user_id == '{userid}'""").fetchone()
    return language[0]


@bot.message_handler(commands=['stats'])
def stats(message):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    language = language_check(message.chat.id)
    c = conn.cursor()
    with conn:
        c.execute(f"""UPDATE users SET last_check='{now}' WHERE user_id=={message.chat.id}""")
    with conn:
        *stats, = c.execute("SELECT * FROM stats").fetchone()
    bot.send_message(message.chat.id, config.translations[language]["stats"].format(*stats), parse_mode="Markdown")


# @bot.message_handler(commands=['top'])
# def top(message):
#     now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
#     # language = language_check(message.chat.id)
#     c = conn.cursor()
#     with conn:
#         c.execute(f"""UPDATE users SET last_check='{now}' WHERE user_id=={message.chat.id}""")
#     with conn:
#         *stats, = c.execute("SELECT * FROM countries LIMIT 5").fetchall()
#         print(*stats)
#     for country in *stats:

#     # bot.send_message(message.chat.id, config.translations[language]["stats"].format(*stats), parse_mode="Markdown")


def check_user(userid, username=None):
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with conn:
        user = c.execute(f"""SELECT user_id FROM users WHERE user_id == '{userid}'""").fetchone()
    if not user:
        with conn:
            c.execute(f"INSERT INTO users VALUES ('{userid}', '{username}', '{time.strftime('%d-%m-%Y')}', '{now}', 'lang-eng')")
        logger.info(f"New user detected {userid}-{username}")


def main():
    bot.infinity_polling(timeout=30)
    # bot.polling(timeout=30)


if __name__ == '__main__':
    main()
