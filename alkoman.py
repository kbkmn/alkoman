import os
import datetime

from settings import *
from bot import Bot
from database import Database
from extras import pluralize, check_for_kadyrov, check_for_words

class Alkoman:
    def __init__(self):
        self.bot = Bot(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_WEBHOOK_URL,
            int(os.environ.get("PORT", TELEGRAM_WEBHOOK_PORT)),
            on_message_recieved=self.message_recieved
        )
        self.database = Database(POSTGRESQL_DB_URI)

        # self.bot.add_job((0, 1, 2, 3, 4, 5, 6), datetime.time(hour=20, minute=59, second=00), self.top)
        # self.bot.add_job((5, ), datetime.time(hour=16, minute=00, second=00), self.weekend)

        self.bot.add_command("stat", self.stat)
        self.bot.add_command("help", self.help)

        self.bot.run()

    def message_recieved(self, chat, user, message):
        if check_for_kadyrov(message):
            self.bot.send_message(chat.id, "Извините дон")
        
        words = message.split()
        word_count = len(list(filter(lambda value: len(value) >= 3, words)))
        slur_count = check_for_words(SLURS, message)
        tennis_count = check_for_words(["теннис"], message)

        self.database.find_or_create_user(user.id, user.first_name)
        self.database.increment_stats(user.id, word_count, slur_count, tennis_count)

    def top(self):
        chat_id = -1001036605543
        valera_user_id = 213533559

        valera = self.database.get_user(valera_user_id)
        users = self.database.get_top()

        if not users:
            self.bot.send_message(chat_id, "Иди на хуй!")
        else:
            message = "Главные пиздаболы:\n"
            for i, item in enumerate(users):
                username = item['username']
                word_count_today = int(item['word_count_today'])

                message += f"{i + 1}. {username} – {'%s %s' % (word_count_today, pluralize(word_count_today, ['слово', 'слова', 'слов']))}\n"

            if valera:
                valera_username = valera['username']
                valera_tennis_count = int(valera['tennis_count_today'])

                message += f"\n{valera_username} згадав про теніс {valera_tennis_count} {pluralize(valera_tennis_count, ['раз', 'рази', 'раз'])}"

            self.bot.send_message(chat_id, message)

    def weekend(self):
        chat_id = -1001036605543
        users = self.database.get_all_users()

        if not users:
            self.bot.send_message(chat_id, "Хуй вам, а не опрос")
        else:
            message = "Конец дня наступил и конец рабочий недели вместе с ним. Рассказывайте, что у вас интересного случилось давайте, чего видели/слышали, есть ли движухи какие. В общем делитесь клёвым и неклёвым тоже\n"
            for i, item in enumerate(users):
                message += f"[{item['username']}](tg://user?id={item['id']}) "
            
            self.bot.send_message(chat_id, message)

    def stat(self, chat, user, message):
        user = self.database.get_user(user.id)
        valera_user_id = 213533559

        if not user:
            self.bot.send_message(chat.id, "Начинай пездеть, кузнечик!")
        else:
            username = user['username']
            message_count = int(user['message_count'])
            word_count = int(user['word_count'])
            slur_count = int(user['slur_count'])
            male = user['gender']

            if user.id == valera_user_id:
                message = f"{username}, ти надіслав {message_count} {pluralize(message_count, ['повідомлення', 'повідомлення', 'повідомлень'])} – {word_count} {pluralize(message_count, ['слово', 'слова', 'слiв'])} ({slur_count} {pluralize(slur_count, ['слово', 'слова', 'слiв'])} матюки) 🇺🇦"
            else:
                if male:
                    message = f"{username}, ты напездел {message_count} {pluralize(message_count, ['сообщение', 'сообщения', 'сообщений'])} – {word_count} {pluralize(word_count, ['слово', 'слова', 'слов'])} ({slur_count} {pluralize(slur_count, ['слово', 'слова', 'слов'])} матершины)"
                else:
                    message = f"{username}, ты напездела {message_count} {pluralize(message_count, ['сообщение', 'сообщения', 'сообщений'])} – {word_count} {pluralize(word_count, ['слово', 'слова', 'слов'])} ({slur_count} {pluralize(slur_count, ['слово', 'слова', 'слов'])} матершины)"

            self.bot.send_message(chat.id, message)

    def help(self, chat, user, message):
        user = self.database.get_user(user.id)

        if user:
            username = user['username']
            
            self.bot.send_message(
                chat.id,
                f"{username}, иди на хуй! ( ) \n . , \n [ ]"
            )

if __name__ == "__main__":
    Alkoman()