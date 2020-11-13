#!/usr/bin/python

import telebot
import logging
import time
from datetime import datetime, timedelta
import config
import plotting
import requests, json
from dbmodels import GlobalStats, CountryStats, User, Notification

BOT = telebot.TeleBot(config.TELEGRAM["token"])

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)

# Vaccine data
response = requests.get("https://disease.sh/v3/covid-19/vaccine")
data = response.json()
with open('vaccinedata.json', 'w') as f:
    json.dump(data, f, indent = 4, sort_keys = True)
f.close()

with open('vaccinedata.json') as f:
    VACCINE_DATA = json.load(f)
f.close()


@BOT.message_handler(commands=['start', 'help'])
def start(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-command:{message.text}")
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
    if query.data.startswith('lang-'):
        LOGGER.info(f"{query.message.chat.id}-{query.message.chat.username}-query:{query.data}")
        user_language_update(query.data, query.message.chat.id)
        BOT.answer_callback_query(query.id, config.TRANSLATIONS[query.data]["pick"])

    if query.data.startswith('graph-'):
        LOGGER.info(f"{query.message.chat.id}-{query.message.chat.username}-query:{query.data}")
        language = language_check(query.message.chat.id)
        countryname = query.data.replace('graph-', '')
        callback_answer = config.TRANSLATIONS[language]["show-graph-alert"].format(15)
        BOT.answer_callback_query(query.id, callback_answer)
        graph = show_graph_query(countryname)
        BOT.send_photo(query.message.chat.id, graph)

    if query.data.startswith('graphperday-'):
        LOGGER.info(f"{query.message.chat.id}-{query.message.chat.username}-query:{query.data}")
        language = language_check(query.message.chat.id)
        countryname = query.data.replace('graphperday-', '')
        callback_answer = config.TRANSLATIONS[language]["show-graph-alert"].format(30)
        BOT.answer_callback_query(query.id, callback_answer)
        graph = show_graph_perday_query(countryname)
        BOT.send_photo(query.message.chat.id, graph)

    if query.data.startswith('notif-'):
        LOGGER.info(f"{query.message.chat.id}-{query.message.chat.username}-query:{query.data}")
        if query.data == 'notif-remove':
            remove_notif(query)
        else:
            edit_notif_callback_message(query)

    if query.data.startswith('vaccine-'):
        LOGGER.info(f"{query.message.chat.id}-{query.message.chat.username}-query:{query.data}")
        if query.data.startswith('vaccine-details'):
            candidate_number = int(query.data.replace('vaccine-details-', ''))
            show_vaccine_description(query, candidate_number)
        else:
            candidate_number = int(query.data.replace('vaccine-data-', ''))
            get_vaccine_details(query, candidate_number)
        

def show_vaccine_description(query, candidate):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if candidate == 0:
        keyboard.add(
            telebot.types.InlineKeyboardButton('Next', callback_data=f"vaccine-data-{candidate + 1}")
        )
    elif candidate == 50:
        keyboard.add(
            telebot.types.InlineKeyboardButton('Previous', callback_data=f"vaccine-data-{candidate - 1}")
        )
    else:
        keyboard.row(
            telebot.types.InlineKeyboardButton('Previous', callback_data=f"vaccine-data-{candidate - 1}"),
            telebot.types.InlineKeyboardButton('Next', callback_data=f"vaccine-data-{candidate + 1}"),
        )
    BOT.answer_callback_query(query.id)
    BOT.edit_message_text(
        VACCINE_DATA['data'][candidate]['details'],
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


def get_vaccine_details(query, candidate):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if candidate == 0:
        keyboard.add(
            telebot.types.InlineKeyboardButton('Next', callback_data=f"vaccine-data-{candidate + 1}")
        )
    elif candidate == 50:
        keyboard.add(
            telebot.types.InlineKeyboardButton('Previous', callback_data=f"vaccine-data-{candidate - 1}")
        )
    else:
        keyboard.row(
            telebot.types.InlineKeyboardButton('Previous', callback_data=f"vaccine-data-{candidate - 1}"),
            telebot.types.InlineKeyboardButton('Next', callback_data=f"vaccine-data-{candidate + 1}"),
        )
    keyboard.add(
            telebot.types.InlineKeyboardButton('Description', callback_data=f"vaccine-details-{candidate}")
        )
    responseMessage = f"""
*💉 Candidate:* {VACCINE_DATA['data'][candidate]['candidate']}
*🧬 Mechanism:* {VACCINE_DATA['data'][candidate]['mechanism']}
*💸 Sponsors:* {VACCINE_DATA['data'][candidate]['sponsors']}
*⚖️ Trial Phase:* {VACCINE_DATA['data'][candidate]['trialPhase']}
*🏥 Institutions:* {VACCINE_DATA['data'][candidate]['institutions']}
        """.replace("'", "")
    BOT.answer_callback_query(query.id)
    BOT.edit_message_text(
        responseMessage,
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


def remove_notif(query):
    """
    Remove notification entry from the database
    """
    try:
        Notification.delete().where(
            (Notification.user_id == query.message.chat.id) & (Notification.country == query.message.text)
        )
        BOT.answer_callback_query(query.id, "Notification successfully removed")
    except:
        BOT.answer_callback_query(query.id, "An error occured. Try again")


def edit_notif_callback_message(query):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton('Remove', callback_data='notif-remove')
    )
    BOT.edit_message_text(
        f"*{query.data.replace('notif-', '')}*",
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


def user_language_update(queryData, user):
    queryData = queryData.replace('lang-', '')
    User.update(language=queryData).where(User.id == user).execute()


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
    language = User.get(User.id == userid).language
    return 'lang-' + language


def update_user_checktime(user_id):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    User.update(last_check=now).where(User.id == user_id).execute()


@BOT.message_handler(commands=['stats'])
def all_stats(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-command:{message.text}")
    keyboard = telebot.types.InlineKeyboardMarkup()
    update_user_checktime(message.chat.id)
    language = language_check(message.chat.id)

    global_stats = GlobalStats.get_or_none()
    global_stats = change_time_representation(global_stats)
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            config.TRANSLATIONS[language]["show-graph"],
            callback_data=f'graph-all'),
        telebot.types.InlineKeyboardButton(
            config.TRANSLATIONS[language]["show-graph-perday"],
            callback_data=f'graphperday-all')
    )
    BOT.send_message(
        message.chat.id,
        config.TRANSLATIONS[language]["stats"].format(global_stats),
        parse_mode="Markdown",
        reply_markup=keyboard)


@BOT.message_handler(commands=['vacs'])
def get_vaccine_data(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-command:{message.text}")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton('Details', callback_data='vaccine-data-0')
    )
    responseMessage = f"🧪*Total Candidates:*  {VACCINE_DATA['totalCandidates']}"
    for phases in VACCINE_DATA['phases']:
        phaseStage = f"{phases['phase']}: "
        candidates = phases['candidates']
        responseMessage += "\n" + phaseStage + candidates
    BOT.send_message(
        message.chat.id,
        responseMessage,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


def change_time_representation(stats):  # I expect time data as the last object
    """
    Calculates updated time as 'X ago' instead of fixed UTC time
    """
    stats.updated = datetime.now() - datetime.strptime(str(stats.updated), "%Y-%m-%d %H:%M:%S")
    stats.updated = stats.updated - timedelta(microseconds=stats.updated.microseconds)  # removing microseconds
    return stats


@BOT.message_handler(commands=['topcases'])
def top_confirmed(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-command:{message.text}")
    language = language_check(message.chat.id)
    top_stats_message = config.TRANSLATIONS[language]["topconfirmed"] + '\n\n'
    update_user_checktime(message.chat.id)
    stats = CountryStats.select().order_by(CountryStats.cases.desc()).limit(10)
    for country in stats:
        print(country)
        top_stats_message += config.TRANSLATIONS["bycountry"].format(country)
    BOT.send_message(message.chat.id, top_stats_message, parse_mode="Markdown")


@BOT.message_handler(commands=['toprecovered'])
def top_recovered(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-command:{message.text}")
    language = language_check(message.chat.id)
    top_stats_message = config.TRANSLATIONS[language]["toprecovered"] + '\n\n'
    update_user_checktime(message.chat.id)
    stats = CountryStats.select().order_by(CountryStats.recovered.desc()).limit(10)
    for country in stats:
        top_stats_message += config.TRANSLATIONS["bycountry"].format(country)
    BOT.send_message(message.chat.id, top_stats_message, parse_mode="Markdown")


@BOT.message_handler(commands=['topdeaths'])
def top_deaths(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-command:{message.text}")
    language = language_check(message.chat.id)
    top_stats_message = config.TRANSLATIONS[language]["topdeaths"] + '\n\n'
    update_user_checktime(message.chat.id)
    stats = CountryStats.select().order_by(CountryStats.deaths.desc()).limit(10)
    for country in stats:
        top_stats_message += config.TRANSLATIONS["bycountry"].format(country)
    BOT.send_message(message.chat.id, top_stats_message, parse_mode="Markdown")


@BOT.message_handler(commands=['graph'])
def send_graph(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-command:{message.text}")
    language = language_check(message.chat.id)
    country_arg = extract_arg(message.text)
    update_user_checktime(message.chat.id)
    try:
        if country_arg:
            countrydata = check_country(message, country_arg[0])
            plot = plotting.history_graph(countrydata.country)
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
        countrydata = check_country(message)
        plot = plotting.history_graph(countrydata.country)
        BOT.send_photo(message.chat.id, plot)
    except:
        BOT.send_message(message.chat.id, "An error occured. Try again")


def show_graph_query(countryname):
    if countryname == 'all':
        plot = plotting.history_graph('all')
    else:
        plot = plotting.history_graph(countryname)
    return plot


def show_graph_perday_query(countryname):
    if countryname == 'all':
        plot = plotting.graph_per_day('all')
    else:
        plot = plotting.graph_per_day(countryname)
    return plot


@BOT.message_handler(commands=['mynotif'])
def notification_check(message):
    # language = language_check(message.chat.id)
    update_user_checktime(message.chat.id)
    try:
        # countries = READER.execute(
        #     f"SELECT country FROM notifications WHERE user_id=={message.chat.id}").fetchall()
        notif = Notification.get_or_none(Notification.user_id == message.chat.id)
        if not notif:
            BOT.send_message(
                message.chat.id,
                """No notifications are set. This feature is not working yet and is still under development"""
            )
            # BOT.register_next_step_handler(message, add_notification)
        else:
            keyboard = existing_notifications_buttons(notif)
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
    language = language_check(message.chat.id)
    update_user_checktime(message.chat.id)
    try:
        BOT.send_message(message.chat.id, "This feature is not working yet and is still under development")
        BOT.register_next_step_handler(message, add_notification)
    except:
        BOT.send_message(message.chat.id, "An error occured. Try again")


def add_notification(message):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    language = language_check(message.chat.id)
    countrydata = check_country(message)
    notif_exists, created = Notification.get_or_create(
        country=countrydata.country,
        user_id=message.chat.id,
        username=message.chat.username
    )
    if not created:
        BOT.send_message(message.chat.id, f'Notification for {countrydata.country} is already existing. Cancelling..')
    else:
        if notif_exists:
            BOT.reply_to(message, f'Notification for {countrydata.country} successfully added')
        else:
            BOT.register_next_step_handler(message, add_notification)


@BOT.message_handler(content_types=["text"])
def get_country_stats(message):
    LOGGER.info(f"{message.chat.id}-{message.chat.username}-text:{message.text}")
    language = language_check(message.chat.id)
    country_stats = check_country(message)
    keyboard = telebot.types.InlineKeyboardMarkup()
    update_user_checktime(message.chat.id)
    if country_stats:
        try:
            country_stats = change_time_representation(country_stats)
            keyboard.row(
                telebot.types.InlineKeyboardButton(
                    config.TRANSLATIONS[language]["show-graph"],
                    callback_data=f'graph-{country_stats.country}'),
                telebot.types.InlineKeyboardButton(
                    "Cases per day",
                    callback_data=f'graphperday-{country_stats.country}')
            )
            BOT.send_message(
                message.chat.id,
                config.TRANSLATIONS[language]["stats-per-country"].format(country_stats),
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
            countrystats = CountryStats.select().where(CountryStats.country.contains(text)).order_by(
                CountryStats.cases.desc()).get()
        else:
            countrystats = CountryStats.select().where(CountryStats.country.contains(message.text)).order_by(
                CountryStats.cases.desc()).get()

        if not countrystats:
            BOT.send_message(message.chat.id, config.TRANSLATIONS[language]["wrong-country"])
            return None
        return countrystats
    except:
        BOT.send_message(message.chat.id, config.TRANSLATIONS[language]["wrong-country"])


def check_user(userid, username):
    """
    Check the user in the database.
    In case it doesnt exist it will add it with ENG default language
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    user = User.get_or_none(User.id == userid)
    
    if not user:
        if not username:
            User.create(
                id=userid,
                started_date=time.strftime('%d-%m-%Y'),
                last_check=now,
                language='en'
            )
        else:
            User.create(
                id=userid,
                username=username,
                started_date=time.strftime('%d-%m-%Y'),
                last_check=now,
                language='en'
            )
        LOGGER.info(f"New user detected {userid}-{username}")


def main():
    BOT.infinity_polling(timeout=40)


if __name__ == '__main__':
    main()
