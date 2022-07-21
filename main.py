import logging
import os
from typing import List

from telegram.ext import Updater, Dispatcher, Handler
from telegram.ext.handler import UT
from telegram.ext.utils.types import CCT

import bot

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def add_handlers(dispatcher: Dispatcher, handlers: List[Handler[UT, CCT]]):
    for handler in handlers:
        dispatcher.add_handler(handler)


def main():
    token = os.environ["BOT_TOKEN"]
    updater = Updater(token=token)
    dispatcher: Dispatcher = updater.dispatcher

    # Handlers
    add_handlers(dispatcher, bot.handlers)

    # Error
    dispatcher.add_error_handler(bot.handle_error)

    # Polling
    updater.start_polling()

    # Run
    logger.info(f"Bot started at https://t.me/{updater.bot.username}")
    updater.idle()


if __name__ == "__main__":
    main()
