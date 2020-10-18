import telebot
import config
from dbmodels import User

ANNOUNCEMENT = """
    Just a quick reminder! You can *just type any country name* and the bot will show you detailed stats for that country. 
    Check out /help for more stats, commands and features.
"""

BOT = telebot.TeleBot(config.TELEGRAM["token"])
for user in User.select():
    try:
        BOT.send_message(user.id, ANNOUNCEMENT, parse_mode="Markdown", disable_web_page_preview=True)
        print(f"message sent to {user.id}-{user.username}")
    except:
        pass