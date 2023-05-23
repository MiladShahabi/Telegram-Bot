from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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