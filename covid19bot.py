#!/usr/bin/python

import telebot
import logging
import sqlite3
import time
from datetime import datetime, timedelta
import config
import plotting


BOT = telebot.TeleBot(config.TELEGRAM["token"])
WRITER = sqlite3.connect(config.DATABASE["filename"], check_same_thread=False, isolation_level=None)
WRITER.execute('pragma journal_mode=wal;') # write-ahead-logging (WAL)
READER = sqlite3.connect(config.DATABASE["filename"], check_same_thread=False, isolation_level=None)
READER.execute('pragma journal_mode=wal;') # write-ahead-logging (WAL)
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)


@BOT.message_handler(commands=['start', 'help'])
def start(message):
    check_user(message.chat.id, message.chat.username)
    language = language_check(message.chat.id)
    help_text = config.TRANSLATIONS[language]["help"]
    if message.text == '/help':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                config.TRANSLATIONS[language]["dm"], url='telegram.me/maxtacu'
            )
        )
        BOT.send_message(message.chat.id, help_text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        BOT.send_message(message.chat.id, help_text, parse_mode="Markdown")
        language_pick_buttons(message, language)


@BOT.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    """
    Callback query handler
    """
    language = language_check(query.message.chat.id)
    if query.data.startswith('lang-'):
        user_language_update(query.data, query.message.chat.id)
        BOT.answer_callback_query(query.id, config.TRANSLATIONS[language]["pick"])
    if query.data.startswith('graph-'):
        countryname = query.data.replace('graph-', '')
        BOT.answer_callback_query(query.id, config.TRANSLATIONS[language]["show-graph-alert"])
        graph = show_graph_query(countryname)
        BOT.send_photo(query.message.chat.id, graph)
    if query.data.startswith('notif-'):
        if query.data == 'notif-remove':
            remove_notif(query)
        else:
            edit_notif_callback_message(query)


def remove_notif(query):
    """
    Remove notification entry from the database
    """
    try:
        WRITER.execute(
            f"DELETE FROM notifications WHERE user_id=={query.message.chat.id} AND country=='{query.message.text}'")
        BOT.answer_callback_query(query.id, "Notification successfully removed")
    except:
        BOT.answer_callback_query(query.id, "An error occured. Try again")


def edit_notif_callback_message(query):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton('Remove', callback_data='notif-remove')
    )
    BOT.edit_message_text(
        f"*{query.data.replace('notif-','')}*",
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


def user_language_update(language, user):
    WRITER.execute(f"UPDATE users SET language='{language}' WHERE user_id=={user}")


def language_pick_buttons(message, language):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('English', callback_data='lang-en'),
        telebot.types.InlineKeyboardButton('Русский', callback_data='lang-ru'),
        telebot.types.InlineKeyboardButton('Español', callback_data='lang-es')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Português', callback_data='lang-pt'),
        telebot.types.InlineKeyboardButton('Română', callback_data='lang-ro')
    )
    BOT.send_message(
        message.chat.id,
        config.TRANSLATIONS[language]["pickrequest"],
        parse_mode="Markdown",
        reply_markup=keyboard
    )


def language_check(userid):
    language = READER.execute(f"SELECT language FROM users WHERE user_id=='{userid}'").fetchone()
    return language[0]


def update_user_checktime(user_id):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    WRITER.execute(f"UPDATE users SET last_check='{now}' WHERE user_id=={user_id}")


@BOT.message_handler(commands=['stats'])
def allstats(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    update_user_checktime(message.chat.id)
    language = language_check(message.chat.id)
    stats = READER.execute("SELECT * FROM stats").fetchone()
    stats = change_time_representation(stats)
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            config.TRANSLATIONS[language]["show-graph"],
            callback_data=f'graph-all')
        )
    BOT.send_message(
        message.chat.id,
        config.TRANSLATIONS[language]["stats"].format(*stats),
        parse_mode="Markdown",
        reply_markup=keyboard)

def change_time_representation(data): # I expect time data as the last object
    """
    Calculates updated time as 'X ago' instead of fixed UTC time
    """
    data = list(data)   # change it to list to be able to update the value
    data[-1] = datetime.now() - datetime.strptime(data[-1], "%Y-%m-%d %H:%M:%S")
    data[-1] = data[-1] - timedelta(microseconds=data[-1].microseconds) # removing microseconds
    data = tuple(data)  # change it back to tuple
    return data

@BOT.message_handler(commands=['topcases'])
def top_confirmed(message):
    language = language_check(message.chat.id)
    top_stats_message = config.TRANSLATIONS[language]["topconfirmed"] + '\n\n'
    update_user_checktime(message.chat.id)
    stats = READER.execute(
        "SELECT country,cases FROM countries ORDER BY cases DESC LIMIT 10").fetchall()
    for country in stats:
        top_stats_message += config.TRANSLATIONS["bycountry"].format(countryname=country[0], cases=country[1])
    BOT.send_message(message.chat.id, top_stats_message, parse_mode="Markdown")


@BOT.message_handler(commands=['toprecovered'])
def top_recovered(message):
    language = language_check(message.chat.id)
    top_stats_message = config.TRANSLATIONS[language]["toprecovered"] + '\n\n'
    update_user_checktime(message.chat.id)
    stats = READER.execute(
        "SELECT country,recovered FROM countries ORDER BY recovered DESC LIMIT 10").fetchall()
    for country in stats:
        top_stats_message += config.TRANSLATIONS["bycountry"].format(countryname=country[0], cases=country[1])
    BOT.send_message(message.chat.id, top_stats_message, parse_mode="Markdown")


@BOT.message_handler(commands=['topdeaths'])
def top_deaths(message):
    language = language_check(message.chat.id)
    top_stats_message = config.TRANSLATIONS[language]["topdeaths"] + '\n\n'
    update_user_checktime(message.chat.id)
    stats = READER.execute(
        "SELECT country,deaths FROM countries ORDER BY deaths DESC LIMIT 10").fetchall()
    for country in stats:
        top_stats_message += config.TRANSLATIONS["bycountry"].format(countryname=country[0], cases=country[1])
    BOT.send_message(message.chat.id, top_stats_message, parse_mode="Markdown")


@BOT.message_handler(commands=['graph'])
def send_graph(message):
    language = language_check(message.chat.id)
    country_arg = extract_arg(message.text)
    update_user_checktime(message.chat.id)
    try:
        if country_arg:
            countryname = check_country(message, country_arg[0])
            plot = plotting.create_graph(countryname)
            BOT.send_photo(message.chat.id, plot)
            plot.close()
        else:
            BOT.send_message(message.chat.id, config.TRANSLATIONS[language]["country-type"])
            BOT.register_next_step_handler(message, show_graph)
    except:
        BOT.send_message(message.chat.id, "An error occured. Try again")


def extract_arg(arg):
    return arg.split()[1:]


def show_graph(message):
    try:
        countryname = check_country(message)
        plot = plotting.create_graph(countryname)
        BOT.send_photo(message.chat.id, plot)
    except:
        BOT.send_message(message.chat.id, "An error occured. Try again")


def show_graph_query(countryname):
    if countryname == 'all':
        plot = plotting.create_graph('all')
    else:
        plot = plotting.create_graph(countryname)
    return plot


@BOT.message_handler(commands=['mynotif'])
def notification_check(message):
    # language = language_check(message.chat.id)
    update_user_checktime(message.chat.id)
    try:
        countries = READER.execute(
            f"SELECT country FROM notifications WHERE user_id=={message.chat.id}").fetchall()
        if not countries:
            BOT.send_message(
                message.chat.id,
                """No notifications are set. This feature is not working yet and is still under development"""
            )
            # BOT.register_next_step_handler(message, add_notification)
        else:
            keyboard = existing_notifications_buttons(countries)
            BOT.send_message(
                message.chat.id,
                "Here are your activated notifications",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    except:
        BOT.send_message(message.chat.id, "An error occured. Try again")


def existing_notifications_buttons(countrylist):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for country in countrylist:
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                country[0],
                callback_data=f'notif-{country[0]}'
            )
        )
    return keyboard


@BOT.message_handler(commands=['setnotif'])
def notification_set(message):
    # language = language_check(message.chat.id)
    update_user_checktime(message.chat.id)
    try:
        BOT.send_message(message.chat.id, "This feature is not working yet and is still under development")
        BOT.register_next_step_handler(message, add_notification)
    except:
        BOT.send_message(message.chat.id, "An error occured. Try again")


def add_notification(message):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # language = language_check(message.chat.id)
    countryname = check_country(message)
    notif_exists = READER.execute(
        f"SELECT country FROM notifications WHERE country=='{countryname}' AND user_id=={message.chat.id}").fetchone()
    if notif_exists:
        BOT.send_message(message.chat.id, f'Notification for {countryname} is already existing. Cancelling..')
    else:
        if countryname:
            WRITER.execute(
                f"INSERT INTO notifications VALUES ('{message.chat.id}', '{message.chat.username}', '{countryname}', '{now}')")
            BOT.reply_to(message, f'Notification for {countryname} successfully added')
        else:
            BOT.register_next_step_handler(message, add_notification)


@BOT.message_handler(content_types=["text"])
def country_stats(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-text-{message.text}")
    language = language_check(message.chat.id)
    countryname = check_country(message)
    keyboard = telebot.types.InlineKeyboardMarkup()
    if countryname:
        try:
            update_user_checktime(message.chat.id)
            stats = READER.execute(
                f"SELECT * FROM countries WHERE country=='{countryname}'").fetchone()
            stats = change_time_representation(stats)
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    config.TRANSLATIONS[language]["show-graph"],
                    callback_data=f'graph-{countryname}')
            )
            BOT.send_message(
                message.chat.id,
                config.TRANSLATIONS[language]["stats-per-country"].format(*stats),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except:
            pass


def check_country(message, text=None):
    """
    Check country in the database.
    """
    language = language_check(message.chat.id)
    try:
        if text:
            countryname = READER.execute(
                f"SELECT country FROM countries WHERE country LIKE '%{text}%' ORDER BY cases DESC").fetchone()
        else:
            countryname = READER.execute(
                f"SELECT country FROM countries WHERE country LIKE '%{message.text}%' ORDER BY cases DESC").fetchone()
        if not countryname[0]:
            BOT.send_message(message.chat.id, config.TRANSLATIONS[language]["wrong-country"])
            return None
        return countryname[0]
    except:
        BOT.send_message(message.chat.id, config.TRANSLATIONS[language]["wrong-country"])


def check_user(userid, username=None):
    """
    Check the user in the database.
    In case it doesnt exist it will add it with ENG default language
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = READER.execute(f"SELECT user_id FROM users WHERE user_id=='{userid}'").fetchone()
    if not user:
        WRITER.execute(f"""INSERT INTO users VALUES (
            '{userid}', '{username}',
            '{time.strftime('%d-%m-%Y')}',
            '{now}',
            'lang-en')""")
        LOGGER.info(f"New user detected {userid}-{username}")


def main():
    BOT.infinity_polling(timeout=30)


if __name__ == '__main__':
    main()
