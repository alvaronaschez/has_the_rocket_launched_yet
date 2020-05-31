import logging

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InputMediaPhoto, TelegramError)
from telegram.ext import (CommandHandler, CallbackQueryHandler,
                          ConversationHandler)

from video_utils import FrameX, SequenceOfFrames

# Stages
FIRST, SECOND = range(2)
# Callback data
NO, YES = range(2)

# object that will give us the frames
frames: SequenceOfFrames = FrameX()


def start(update, context):
    """Send message on `/start`."""
    chat_id = update.effective_chat.id
    # Get user that sent /start and log his name
    user = update.effective_user
    logging.info(f"User {user.first_name} started the conversation.")
    # init the binary search through the frames
    left, right = 0, len(frames) - 1
    context.chat_data['left'] = left
    context.chat_data['right'] = right
    middle = (left + right) // 2
    photo = frames[middle]
    image = context.bot.send_photo(chat_id=chat_id, photo=photo)
    context.chat_data['image'] = image
    step = 1
    context.chat_data['step'] = step
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    keyboard = [[
        InlineKeyboardButton("Yes", callback_data=str(YES)),
        InlineKeyboardButton("No", callback_data=str(NO))
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    """
    update.message.reply_text(
        f"({step}) frame {middle} -  Has the rocket launched yet?",
        reply_markup=reply_markup)
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"({step}) frame {middle} -  Has the rocket launched yet?",
        reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST


def start_over(update, context):
    query = update.callback_query
    left = context.chat_data["left"]
    query.edit_message_text(
        text=f"Found! Take-off = {left} - Do you want to play again?")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Great! Let's go!!")
    return start(update, context)


def one(update, context):
    """Show new choice of buttons"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered,
    # even if no notification to the user is needed
    # Some clients may have trouble otherwise.
    # See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    context.chat_data['step'] += 1
    step = context.chat_data['step']
    left = context.chat_data["left"]
    right = context.chat_data["right"]
    middle = (left + right) // 2

    # we are searching the first frame in which the rocket
    # has taken off
    if int(query.data) is YES:
        right = middle
        context.chat_data["right"] = right
    else:
        left = middle + 1
        context.chat_data["left"] = left

    middle = (left + right) // 2

    if left == right:
        try:
            context.chat_data['image'].edit_media(InputMediaPhoto(
                frames[left]))
        except TelegramError:
            # when you try to update the image sending the same image
            # a TelegramError is raised
            pass

        keyboard = [[
            InlineKeyboardButton("Yes", callback_data=str(YES)),
            InlineKeyboardButton("No", callback_data=str(NO))
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=f"Found! Take-off = {left} - Do you want to play again?",
            reply_markup=reply_markup)
        return SECOND
    else:
        try:
            context.chat_data['image'].edit_media(
                InputMediaPhoto(frames[middle]))
        except TelegramError:
            pass

        keyboard = [[
            InlineKeyboardButton("Yes", callback_data=str(YES)),
            InlineKeyboardButton("No", callback_data=str(NO))
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=f"({step}) frame {middle} - Has the rocket launched yet?",
            reply_markup=reply_markup)
        return FIRST


def end(update, context):
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


# Setup conversation handler with the states FIRST and SECOND
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        FIRST: [
            CallbackQueryHandler(one),
        ],
        SECOND: [
            CallbackQueryHandler(start_over, pattern='^' + str(YES) + '$'),
            CallbackQueryHandler(end, pattern='^' + str(NO) + '$')
        ]
    },
    fallbacks=[CommandHandler('start', start)])
