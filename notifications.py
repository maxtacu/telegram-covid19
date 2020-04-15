import config
import telebot
import logging
import sqlite3
import time


bot = telebot.TeleBot(config.telegram["token"])
conn = sqlite3.connect(config.database["filename"], check_same_thread=False)

while True:
    c = conn.cursor()
    with conn:
        all_stats = c.execute(f"SELECT * FROM countries")
        print("waiting 30 sec")
    conn.close()
    time.sleep(30)
    with conn:
        all_stats_new = c.execute(f"SELECT * FROM countries")
    conn.close()
    if all_stats != all_stats_new:
        print(all_stats_new)
    else:
        print("no data change")

# bot.send_message("713962279", "testmessage")