#!/usr/bin/env python
# pylint: disable=C0116,W0613

import logging
import os
import psycopg2
import re
import datetime

from profanity import *

TOKEN = "5270782462:AAFuIEkdog1H_zJi9FO-qIwPw3dOf8fl3oc"
PORT = int(os.environ.get("PORT", "8443"))
DB_URI = "postgres://autbcwmqanqzil:f0ec489225f5d2b112f0f835f3fbd00f731a68c5bb81a480bd7d985f4165f11e@ec2-44-194-92-192.compute-1.amazonaws.com:5432/ddt46vatb24f46"
VODKA_CHAT_ID=-1001036605543

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, ParseMode, InputLocationMessageContent, InputVenueMessageContent, InputContactMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, InlineQueryHandler
from telegram.utils.helpers import escape_markdown

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()

def top(context: CallbackContext) -> None:
    db_object.execute("SELECT username, word_count_today FROM users ORDER BY word_count_today DESC LIMIT 3")
    result = db_object.fetchall()

    if not result:
        context.bot.send_message(VODKA_CHAT_ID, "Иди на хуй!")
    else:
        message = "Главные пиздаболы:\n"
        for i, item in enumerate(result):
            message += f"{i + 1}. {item[0].strip()} – {'%s %s' % (int(item[1]), pluralize(int(item[1]), ['слово', 'слова', 'слов']))}\n"

        db_object.execute("SELECT username, tennis_count_today FROM users WHERE id = 213533559")
        result = db_object.fetchone()

        message += f"{result[0]} воспомнил про теннис {result[1]} {pluralize(int(result[1]), ['раз', 'раза', 'раз'])}"

        context.bot.send_message(VODKA_CHAT_ID, message)

    db_object.execute(f"UPDATE users SET word_count_today = 0, tennis_count_today = 0")
    db_connection.commit()

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
        message_count = int(result[1])
        word_count = int(result[2])
        slur_count = int(result[3])
        male = result[4]

        if user.id == 213533559:
            message = f"{result[0]}, ти надіслав {message_count} {pluralize(message_count, ['повідомлення', 'повідомлення', 'повідомлень'])} – {word_count} {pluralize(message_count, ['слово', 'слова', 'слiв'])} ({slur_count} {pluralize(slur_count, ['слово', 'слова', 'слiв'])} матюки) 🇺🇦"
        else:
            if male:
                message = f"{result[0]}, ты напездел {message_count} {pluralize(message_count, ['сообщение', 'сообщения', 'сообщений'])} – {word_count} {pluralize(word_count, ['слово', 'слова', 'слов'])} ({slur_count} {pluralize(slur_count, ['слово', 'слова', 'слов'])} матершины)"
            else:
                message = f"{result[0]}, ты напездела {message_count} {pluralize(message_count, ['сообщение', 'сообщения', 'сообщений'])} – {word_count} {pluralize(word_count, ['слово', 'слова', 'слов'])} ({slur_count} {pluralize(slur_count, ['слово', 'слова', 'слов'])} матершины)"

        update.effective_chat.send_message(message)

def help(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    db_object.execute(f"SELECT username FROM users WHERE id = {user.id}")
    result = db_object.fetchone()

    update.effective_chat.send_message(f"{result[0]}, иди на хуй!")

def count(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    message = update.message.text.strip()

    if check_for_kadyrov(message):
        update.effective_chat.send_message(f"Извините дон")
    
    words = message.split()
    word_count = len(list(filter(lambda value: len(value) >= 3, words)))
    slur_count = check_for_profanity(message)
    tennis_count = check_for_tennis(message)

    check_if_user_exists(user.id, user.first_name)
    update_count(user.id, word_count, slur_count, tennis_count)

def debug(update: Update, context: CallbackContext) -> None:
    # update.effective_chat.send_message(update.effective_chat.id)
    # update.effective_chat.send_message(update.message.chat_id)
    # context.bot.send_message(-1001036605543, "group message")

    # mention = f"[fucker](tg://user?id={118248895}) fuck you nigger"
    # context.bot.send_message(chat_id=118248895, text=mention, parse_mode=ParseMode.MARKDOWN_V2)

    # mention = f"[fucker](tg://user?id={213533559}) fuck you nigger"
    # context.bot.send_message(chat_id=118248895, text=mention, parse_mode=ParseMode.MARKDOWN_V2)

    pass

def scheduler(context: CallbackContext) -> None:
    db_object.execute(f"SELECT id, username FROM users ORDER BY RANDOM()")
    result = db_object.fetchall()

    if not result:
        context.bot.send_message(VODKA_CHAT_ID, "Хуй вам, а не опрос")
    else:
        message = "Конец дня наступил и конец рабочий недели вместе с ним. Рассказывайте, что у вас интересного случилось давайте, чего видели/слышали, есть ли движухи какие. В общем делитесь клёвым и неклёвым тоже\n"
        for i, item in enumerate(result):
            message += f"[{item[1]}](tg://user?id={item[0]}) "
        
        context.bot.send_message(chat_id=VODKA_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN_V2)

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
    db_object.execute(f"SELECT username, message_count, word_count, slur_count, gender FROM users WHERE id = {user_id}")
    return db_object.fetchone()

def update_count(user_id, word_count, slur_count, tennis_count):
    db_object.execute(f"UPDATE users SET message_count = (message_count + 1), word_count = (word_count + {word_count}), slur_count = (slur_count + {slur_count}), word_count_today = (word_count_today + {word_count}), tennis_count_todya = (tennis_count_today + {tennis_count}) WHERE id = {user_id}")
    db_connection.commit()

def main() -> None:
    updater = Updater(TOKEN)
    job_queue = updater.job_queue
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("stat", callback=stat))
    dispatcher.add_handler(CommandHandler("help", callback=help))
    
    # dispatcher.add_handler(CommandHandler("top", callback=top))
    # dispatcher.add_handler(CommandHandler("faggots", callback=faggots))
    # dispatcher.add_handler(CommandHandler("debug", debug))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, callback=count))

    for job in job_queue.jobs():
        job.schedule_removal()

    job_queue.run_daily(scheduler, days=(5, ), time=datetime.time(hour=16, minute=00, second=00))
    job_queue.run_daily(top, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=20, minute=59, second=00))

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