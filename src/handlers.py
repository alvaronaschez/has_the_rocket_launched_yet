# -*- coding: utf-8 -*-
"""
This module contains the callbacks and handlers
which will going to manage the logic of the bot
"""
import logging

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InputMediaPhoto, TelegramError, Update)
from telegram.ext import (CommandHandler, CallbackQueryHandler,
                          ConversationHandler, CallbackContext)

from video_utils import FrameX, SequenceOfFrames

# Enable logging
logger = logging.getLogger(__name__)

# States of the Bot
FIRST, SECOND = range(2)
# Callback data
NO, YES = map(str, range(2))

# object that will provide us the frames
frames: SequenceOfFrames = FrameX()


def start_callback(update: Update, context: CallbackContext) -> int:
    """
    Start the bot when the command `/start` is received
    Set up the context with the initial state of all the variables
    needed to perform the binary search
    """
    # Get user that sent /start and log his name
    user = update.effective_user
    logger.info(f"User {user.first_name} started the conversation.")

    # init the binary search through the frames
    context.chat_data["left"] = left = 0
    context.chat_data["right"] = right = len(frames) - 1
    middle = (left + right) // 2

    photo = frames[middle]
    image = context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=photo)
    context.chat_data["image"] = image
    context.chat_data["step"] = step = 1

    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    keyboard = [[
        InlineKeyboardButton("Yes", callback_data=YES),
        InlineKeyboardButton("No", callback_data=NO)
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"({step}) frame {middle} -  Has the rocket launched yet?",
        reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST


def start_over_callback(update: Update, context: CallbackContext) -> int:
    """Restart the bot when the user decide to play again"""
    query = update.callback_query
    left = context.chat_data["left"]
    query.edit_message_text(
        text=f"Found! Take-off = {left} - Do you want to play again?")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Great! Let's go!!")
    return start_callback(update, context)


def bisect_callback(update: Update, context: CallbackContext) -> int:
    """
    This callback manages the behavior of the first state
    The one in which the binary search through the video is done
    """
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to
    # the user is needed. Some clients may have trouble otherwise.
    # See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    context.chat_data["step"] += 1
    step = context.chat_data["step"]
    left = context.chat_data["left"]
    right = context.chat_data["right"]
    middle = (left + right) // 2

    # we are searching the first frame in which the rocket
    # has taken off
    if query.data == YES:
        right = middle
        context.chat_data["right"] = right
    else:
        left = middle + 1
        context.chat_data["left"] = left

    middle = (left + right) // 2

    if left == right:
        # the search has ended
        try:
            context.chat_data['image'].edit_media(InputMediaPhoto(
                frames[left]))
        except TelegramError:
            # when you try to update the image sending the same image
            # a TelegramError is raised
            pass

        keyboard = [[
            InlineKeyboardButton("Yes", callback_data=YES),
            InlineKeyboardButton("No", callback_data=NO)
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=f"Found! Take-off = {left} - Do you want to play again?",
            reply_markup=reply_markup)
        return SECOND
    else:
        # continue searching
        try:
            context.chat_data['image'].edit_media(
                InputMediaPhoto(frames[middle]))
        except TelegramError:
            pass

        keyboard = [[
            InlineKeyboardButton("Yes", callback_data=YES),
            InlineKeyboardButton("No", callback_data=NO)
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=f"({step}) frame {middle} - Has the rocket launched yet?",
            reply_markup=reply_markup)
        return FIRST


def end_callback(update: Update, context: CallbackContext) -> int:
    """
    Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates"""
    logger.warning(f'Update "{update}" caused error "{context.error}"')


# Setup conversation handler with the states FIRST and SECOND
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_callback)],
    states={
        FIRST: [
            CallbackQueryHandler(bisect_callback),
        ],
        SECOND: [
            CallbackQueryHandler(start_over_callback, pattern="^" + YES + "$"),
            CallbackQueryHandler(end_callback, pattern='^' + NO + "$")
        ]
    },
    fallbacks=[CommandHandler("start", start_callback)])
