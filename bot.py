from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown

class Bot:
    def __init__(
        self,
        token,
        webhook_url,
        webhook_port,
        on_message_recieved = None
    ):

        self.token = token
        self.webhook_url = webhook_url
        self.webhook_port = webhook_port
        self.on_message_recieved = on_message_recieved
        
        self.__updater = Updater(token)
        self.__bot = self.__updater.bot
        
        self.__setup_job_queue()
        self.__setup_dispatcher()

    def __setup_job_queue(self):
        self.__job_queue = self.__updater.job_queue

        for job in self.__job_queue.jobs():
            job.schedule_removal()

    def __setup_dispatcher(self):
        self.__dispatcher = self.__updater.dispatcher
        self.__dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: self.on_message_recieved(update.effective_chat, update.effective_user, update.message.text.strip())))

    def add_command(self, command: str, callback):
        self.__dispatcher.add_handler(
            CommandHandler(command, lambda update, context: callback(update.effective_chat, update.effective_user, update.message.text.strip()))
        )

    def add_job(self, days, time, callback):
        self.__job_queue.run_daily(callback, days=days, time=time)

    def send_message(self, chat_id, message, *args, **kwargs):
        message = escape_markdown(message, version=2)
        
        if 'mentions' in kwargs:
            print("there is mentions in kwargs")

            mentions = ""

            for id, name in kwargs['mentions']:
                mentions += f"[{name}](tg://user?id={id}) "

            message = f"{mentions}\n{message}"

        self.__bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)

    def run(self):
        # self.__updater.start_polling()

        self.__updater.start_webhook(
            listen="0.0.0.0",
            port=self.webhook_port,
            url_path=self.token,
            webhook_url=self.webhook_url + self.token
        )

        self.__updater.idle()