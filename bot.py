#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined as callback query handler.
Then, those functions are passed to the Dispatcher and registered
at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple
CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
import logging
import os
import sys

from telegram.ext import Updater
from handlers import conv_handler, error

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

# logger = logging.getLogger(__name__)

# Getting bot token
TOKEN = os.getenv("TOKEN")

# Getting mode, so we could define run function for local and Heroku setup
MODE = os.getenv("MODE")

if MODE == "dev":

    def run(updater):
        # Start the Bot
        updater.start_polling()
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
elif MODE == "prod":

    def run(updater):
        PORT = int(os.environ.get('PORT', '8443'))
        # add handlers
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.set_webhook(f"https://<appname>.herokuapp.com/{TOKEN}")
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT.
        updater.idle()
else:
    logging.error("No MODE specified!")
    sys.exit(1)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add ConversationHandler to dispatcher that will be used for handling
    # updates
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    run(updater)


if __name__ == '__main__':
    main()
