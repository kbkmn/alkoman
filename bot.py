#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import psycopg2

TOKEN = "5270782462:AAFuIEkdog1H_zJi9FO-qIwPw3dOf8fl3oc"
PORT = int(os.environ.get("PORT", "8443"))
DB_URI = "postgres://autbcwmqanqzil:f0ec489225f5d2b112f0f835f3fbd00f731a68c5bb81a480bd7d985f4165f11e@ec2-44-194-92-192.compute-1.amazonaws.com:5432/ddt46vatb24f46"

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()

def top(update: Update, context: CallbackContext) -> None:
    db_object.execute("SELECT username, word_count FROM users ORDER BY word_count DESC LIMIT 3")
    result = db_object.fetchall()

    if not result:
        update.message.reply_text("Иди на хуй!")
    else:
        message = "Главные пиздаболы:\n"
        for i, item in enumerate(result):
            reply_message += f"{i + 1}. {item[0].strip()} – {item[1]} слов\n"

        update.message.reply_text(message)
            

def stats(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    result = get_count(user.id)
    message_count = int(result['message_count'])
    word_count = int(result['message_count'])

    update.message.reply_markdown_v2(
        fr'{user.mention_markdown_v2()}, ты напездел {message_count} сообщений и {word_count} слов',
        reply_markup=ForceReply(selective=True),
    )

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Иди на хуй!")

def count(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    
    words = update.message.text.strip().split()
    word_count = len(list(filter(lambda value: len(value) >= 3, words)))

    check_if_user_exists(user.id, user.username)
    update_count(user.id, word_count)

def check_if_user_exists(user_id, username):
    db_object.execute(f"SELECT id FROM users WHERE id = {user_id}")
    result = db_object.fetchone()

    if not result:
        db_object.execute("INSERT INTO users(id, username, message_count, word_count) VALUES (%s, %s, %s, %s)", (user_id, username, 0, 0))
        db_connection.commit()

def get_count(user_id):
    db_object.execute("SELECT message_count, word_count FROM users WHERE id = {user_id}")
    return db_object.fetchone()

def update_count(user_id, word_count):
    db_object.execute(f"UPDATE users SET message_count = (message_count + 1), word_count = (word_count + {word_count}) WHERE id = {user_id}")
    db_connection.commit()

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("top", top))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(CommandHandler("help", help))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, count))

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url="https://aqueous-tor-53426.herokuapp.com/" + TOKEN
    )

    updater.idle()

if __name__ == '__main__':
    main()