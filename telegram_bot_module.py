from typing import Final
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN: Final = '6114910026:AAGGPogroG1BvkHA3LOTab_0EzBqqi3JQYM'
BOT_USERNAME: Final = '@GetMyTermin_bot'

# Commands
async def start_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me! I am GetMyTermin bot')


async def help_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am a GetMyTermin bot, Please specify your Termin')


async def custom_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('your Termin is booked')        


# Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return ' Hey there!'
    
    if 'how are you' in processed:
        return 'I am good!'
    
    if 'i love python' in processed:
        return 'Remember to subscribe!'
    
    return 'I do not understand what you wrote...'

async def handler_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response = str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    #Commands    
    app.add_handler(CommandHandler('start', start_commands))
    app.add_handler(CommandHandler('help', help_commands))
    app.add_handler(CommandHandler('custom', custom_commands))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handler_message))

    #Errors
    app.add_error_handler(error)

    #Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)




# import logging

# from telegram import __version__ as TG_VER

# try:
#     from telegram import __version_info__
# except ImportError:
#     __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

# if __version_info__ < (20, 0, 0, "alpha", 1):
#     raise RuntimeError(
#         f"This example is not compatible with your current PTB version {TG_VER}. To view the "
#         f"{TG_VER} version of this example, "
#         f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
#     )
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# logger = logging.getLogger(__name__)


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Sends a message with three inline buttons attached."""
#     keyboard = [
#         [
#             InlineKeyboardButton("Option 1", callback_data="1"),
#             InlineKeyboardButton("Option 2", callback_data="2"),
#         ],
#         [InlineKeyboardButton("Option 3", callback_data="3")],
#     ]

#     reply_markup = InlineKeyboardMarkup(keyboard)

#     await update.message.reply_text("Please choose:", reply_markup=reply_markup)


# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query

#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     await query.answer()

#     await query.edit_message_text(text=f"Selected option: {query.data}")


# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Displays info on how to use the bot."""
#     await update.message.reply_text("Use /start to test this bot.")


# def main() -> None:
#     """Run the bot."""
#     # Create the Application and pass it your bot's token.
#     application = Application.builder().token("TOKEN").build()

#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(CallbackQueryHandler(button))
#     application.add_handler(CommandHandler("help", help_command))

#     # Run the bot until the user presses Ctrl-C
#     application.run_polling()


# if __name__ == "__main__":
#     main()