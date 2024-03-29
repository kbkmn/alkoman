import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone

class Database:
    def __init__(self, uri):
        self.__connection = psycopg2.connect(uri, sslmode="require")
        self.__cursor = self.__connection.cursor(cursor_factory=RealDictCursor)

    def find_or_create_user(self, user_id, name, username):
        self.__cursor.execute(f"SELECT id FROM users WHERE id = {user_id}")
        result = self.__cursor.fetchone()

        if not result:
            self.__cursor.execute("INSERT INTO users(id, name, username) VALUES (%s, %s, %s)", (user_id, name, username))
            self.__connection.commit()

    def get_user(self, id=None, username=None):
        if id:
            field = 'id'
            value = id
        else:
            field = 'username'
            value = username

        self.__cursor.execute(f"SELECT id, name, username, message_count, word_count, slur_count, word_count_today, tennis_count_today, gender, last_message FROM users WHERE {field} = '{value}'")

        return self.__cursor.fetchone()


    def get_all_users(self):
        self.__cursor.execute(f"SELECT id, name, username FROM users ORDER BY RANDOM()")
        
        return self.__cursor.fetchall()

    def get_top(self):
        self.__cursor.execute("SELECT id, name, username, word_count_today FROM users ORDER BY word_count_today DESC LIMIT 3")
        
        result = self.__cursor.fetchall()

        self.__cursor.execute("UPDATE users SET word_count_today = 0, tennis_count_today = 0")
        self.__connection.commit()

        return result

    def increment_stats(self, user_id, word_count, slur_count, tennis_count):
        self.__cursor.execute(f"UPDATE users SET message_count = (message_count + 1), word_count = (word_count + {word_count}), slur_count = (slur_count + {slur_count}), word_count_today = (word_count_today + {word_count}), tennis_count_today = (tennis_count_today + {tennis_count}), last_message = now() WHERE id = {user_id}")
        self.__connection.commit()