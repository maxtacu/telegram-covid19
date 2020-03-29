#!/usr/bin/python

import config, transtlation
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
    if message.text == '/help':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Message the developer', url='telegram.me/maxtacu'
            )
        )
        help_text = transtlation.helpmessage[language]
        bot.send_message(cid, help_text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        help_text = transtlation.helpmessage[language]
        bot.send_message(cid, help_text, parse_mode="Markdown")
        language_pick(message)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
   data = query.data
   if data.startswith('lang-'):
        user_language_update(query.data, query.message.chat.id)
        if data == 'lang-ru':
            bot.answer_callback_query(query.id, f"Выбран Русский язык")
        elif data == 'lang-eng':
            bot.answer_callback_query(query.id, f"You picked English")
        else:
            bot.answer_callback_query(query.id, f"Você escolheu o português")
        

def user_language_update(language, user):
    c = conn.cursor()
    with conn:
        c.execute(f"UPDATE users SET language='{language}' WHERE user_id=={user}")


def language_pick(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton('English', callback_data='lang-eng'),
        telebot.types.InlineKeyboardButton('Russian', callback_data='lang-ru'),
        telebot.types.InlineKeyboardButton('Portuguese', callback_data='lang-pt'),
    )
    bot.send_message(message.chat.id, "Pick your language:", parse_mode="Markdown", reply_markup=keyboard)

def language_check(userid):
    c = conn.cursor()
    with conn:
        language = c.execute(f"""SELECT language FROM users WHERE user_id == '{userid}'""").fetchone()

    return language

@bot.message_handler(commands=['stats'])
def stats(message):
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    c = conn.cursor()
    with conn:
        c.execute(f"""UPDATE users SET last_check='{now}' WHERE user_id=={message.chat.id}""")
    with conn:
        cases, deaths, recovered, updated, active = c.execute("SELECT * FROM stats").fetchone()
    bot.send_message(message.chat.id, (f"*🦠 Total cases:* {cases} \n"
                                       f"*☠️ Deaths:* {deaths} \n"
                                       f"*☘️ Recovered:* {recovered} \n"
                                       f"*🤒 Active:* {active} \n"
                                       f"*⏰ Updated:* {datetime.fromtimestamp(updated)}"), parse_mode="Markdown")


def check_user(userid, username=None):
    c = conn.cursor()
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with conn:
        user = c.execute(f"""SELECT user_id FROM users WHERE user_id == '{userid}'""").fetchone()
    if not user:
        with conn:
            c.execute(f"INSERT INTO users VALUES ('{userid}', '{username}', '{time.strftime('%d-%m-%Y')}', '{now}', 'lang-eng')")
        logger.info(f"New user detected {userid}-{username}")


def main():
    bot.polling(timeout=30)


if __name__ == '__main__':
    main()
