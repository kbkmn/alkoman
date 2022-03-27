#!/usr/bin/env python
# pylint: disable=C0116,W0613

import logging
import os
from urllib import response
import psycopg2
import re
from uuid import uuid4

from profanity import *

TOKEN = "5270782462:AAFuIEkdog1H_zJi9FO-qIwPw3dOf8fl3oc"
PORT = int(os.environ.get("PORT", "8443"))
DB_URI = "postgres://autbcwmqanqzil:f0ec489225f5d2b112f0f835f3fbd00f731a68c5bb81a480bd7d985f4165f11e@ec2-44-194-92-192.compute-1.amazonaws.com:5432/ddt46vatb24f46"

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, ParseMode, InputLocationMessageContent, InputVenueMessageContent, InputContactMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, InlineQueryHandler
from telegram.utils.helpers import escape_markdown

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
        update.effective_chat.send_message("Иди на хуй!")
    else:
        message = "Главные пиздаболы:\n"
        for i, item in enumerate(result):
            message += f"{i + 1}. {item[0].strip()} – {'%s %s' % (int(item[1]), pluralize(int(item[1]), ['слово', 'слова', 'слов']))}\n"

        update.effective_chat.send_message(message)

def faggots(update: Update, context: CallbackContext) -> None:
    db_object.execute("SELECT username, slur_count FROM users ORDER BY slur_count DESC LIMIT 3")
    result = db_object.fetchall()

    if not result:
        update.effective_chat.send_message("Иди на хуй!")
    else:
        message = "Главные матершинники:\n"
        for i, item in enumerate(result):
            message += f"{i + 1}. {item[0].strip()} – {'%s %s' % (int(item[1]), pluralize(int(item[1]), ['слово', 'слова', 'слов']))}\n"

        update.effective_chat.send_message(message)

def stat(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    result = get_count(user.id)

    if not result:
        update.effective_chat.send_message("Начинай пездеть, кузнечик!")
    else:
        message_count = '%s %s' % (int(result[1]), pluralize(int(result[1]), ['сообщение', 'сообщения', 'сообщений']))
        word_count = '%s %s' % (int(result[2]), pluralize(int(result[3]), ['слово', 'слова', 'слов']))
        slur_count = f"{result[3]} {pluralize(int(result[2]), ['слово', 'слова', 'слов'])} матершины"

        update.effective_chat.send_message(f"{result[0]}, ты напездел {message_count} – {word_count} ({slur_count})")

def help(update: Update, context: CallbackContext) -> None:
    update.effective_chat.send_message(f"Иди на хуй!")

def count(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    message = update.message.text.strip()

    if check_for_kadyrov(message):
        update.effective_chat.send_message(f"Извините дон")
    
    words = message.split()
    word_count = len(list(filter(lambda value: len(value) >= 3, words)))
    slur_count = check_for_profanity(message)

    check_if_user_exists(user.id, user.first_name)
    update_count(user.id, word_count, slur_count)


    # U+1F1FA U+1F1E6

# def inlinequery(update: Update, context: CallbackContext) -> None:
#     query = update.inline_query.query

#     if query == "":
#         return

#     results = [
#          InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="U+1F1FA",
#             input_message_content=InputTextMessageContent(query.upper()),
#         ),
#         InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="U+1F1E6",
#             input_message_content=InputTextMessageContent(query.upper()),
#         ),
#         InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="\U0001F1FA",
#             input_message_content=InputTextMessageContent(query.upper()),
#         ),
#         InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="\U0001F1E6",
#             input_message_content=InputTextMessageContent(query.upper()),
#         ),
#         InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="\U+1F1FA",
#             input_message_content=InputTextMessageContent(query.upper()),
#         ),
#         InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="\U+1F1E6",
#             input_message_content=InputTextMessageContent(query.upper()),
#         ),
#     ]

#     update.inline_query.answer(results)

def debug(update: Update, context: CallbackContext) -> None:
    resp = "U+1F1FA U+1F1E6 \U0001F1FA \U0001F1E6 \U+1F1FA \U+1F1E6"

    update.effective_chat.send_message(resp.encode('utf-8'))


def check_for_kadyrov(message):
    if re.search(r'к[ао]дыров', message, re.I):
        return True
    
    return False

def check_if_user_exists(user_id, username):
    db_object.execute(f"SELECT id FROM users WHERE id = {user_id}")
    result = db_object.fetchone()

    if not result:
        db_object.execute("INSERT INTO users(id, username, message_count, word_count) VALUES (%s, %s, %s, %s)", (user_id, username, 0, 0))
        db_connection.commit()

def get_count(user_id):
    db_object.execute(f"SELECT username, message_count, word_count, slur_count FROM users WHERE id = {user_id}")
    return db_object.fetchone()

def update_count(user_id, word_count, slur_count):
    db_object.execute(f"UPDATE users SET message_count = (message_count + 1), word_count = (word_count + {word_count}), slur_count = (slur_count + {slur_count}) WHERE id = {user_id}")
    db_connection.commit()

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("top", callback=top))
    dispatcher.add_handler(CommandHandler("faggots", callback=faggots))
    dispatcher.add_handler(CommandHandler("stat", callback=stat))
    dispatcher.add_handler(CommandHandler("help", callback=help))
    dispatcher.add_handler(CommandHandler("debug", debug))

    # dispatcher.add_handler(InlineQueryHandler(inlinequery))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, callback=count))

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url="https://aqueous-tor-53426.herokuapp.com/" + TOKEN
    )

    updater.idle()

def pluralize(number, forms):
    number = abs(number) % 100

    number_1 = number % 10

    if number > 10 and number < 20:
        return forms[2]
    if number_1 > 1 and number_1 < 5:
        return forms[1]
    if number_1 == 1:
        return forms[0]

    return forms[2]

if __name__ == '__main__':
    main()