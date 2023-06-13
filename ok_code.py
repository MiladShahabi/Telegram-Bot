import time
import logging
from typing import Final
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN: Final = '6114910026:AAGGPogroG1BvkHA3LOTab_0EzBqqi3JQYM'
BOT_USERNAME: Final = '@GetMyTermin_bot'
ADMIN_USER_ID: Final = 5355774833  # Admin's user ID

logging.basicConfig(filename='user_data.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

async def start_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logging.info(f'User {user.id}, username: {user.username}, first name: {user.first_name}, last name: {user.last_name}')
    log_text = f'New user: ID {user.id}, username: {user.username}, first name: {user.first_name}, last name: {user.last_name}'
    await context.bot.send_message(chat_id=ADMIN_USER_ID, text=log_text)

    await update.message.reply_text(
                                    '''Terms and Conditions:

1. After booking an appointment, you are required to pay a 75 Euro fee within 24 hours. Failure to do so will result in the cancellation of your appointment.

2. Our algorithms search for available free time slots only. While you cannot request a specific date, you can suggest your preferred date, and we will prioritize it if available.

3. You are responsible for entering accurate information and verifying it before submitting. Any issues that arise due to incorrect information entered are your sole responsibility.'''
                                    )
    keyboard = [[InlineKeyboardButton('I agree ✅', callback_data="2")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Please check the box below to indicate that you have read and agree to all the Terms and Conditions mentioned above:', reply_markup=reply_markup)

async def help_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am a GetMyTermin bot, Please specify your Termin')

# async def custom_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text('your Termin is booked') 

# def handle_response(text: str) -> str:
#     processed: str = text.lower()

#     if 'hello' in processed:
#         return ' Hey there!'
    
#     if 'how are you' in processed:
#         return 'I am good!'
    
#     if 'i love python' in processed:
#         return 'Remember to subscribe!'
    
#     return 'I do not understand what you wrote...'

# async def handler_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     message_type: str = update.message.chat.type
#     text: str = update.message.text

#     print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

#     if message_type == 'group':
#         if BOT_USERNAME in text:
#             new_text: str = text.replace(BOT_USERNAME, '').strip()
#             response: str = handle_response(new_text)
#         else:
#             return
#     else:
#         response = str = handle_response(text)

#     print('Bot:', response)
#     await update.message.reply_text(response)

async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data = query.data

    if query_data == "2":
        keyboard = [[InlineKeyboardButton('Go to Form 📝', url="https://online.forms.app/getmyterminde/registration-form")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text('Now, press this button to go to the appointment details form and provide the required information', reply_markup=reply_markup)
        await query.answer()

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_commands))
    app.add_handler(CommandHandler('help', help_commands))
    #app.add_handler(CommandHandler('custom', custom_commands))
    #app.add_handler(MessageHandler(filters.TEXT, handler_message))
    app.add_handler(CallbackQueryHandler(handle_button_press))

    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)
