import logging
from typing import Final
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN: Final = '5796108934:AAFH4J0IFNo5eGSiiyhqsh7oB93UHaY3iUY'
BOT_USERNAME: Final = '@MyDreams20bot'
ADMIN_USER_ID: Final = 5355774833  # Admin's user ID

logging.basicConfig(filename='user_data.log', level=logging.INFO, format='%(asctime)s - %(message)s')

bot = telebot.TeleBot(TOKEN)

bot.delete_my_commands(scope=None, language_code=None)

bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Book an Appointment"),
        telebot.types.BotCommand("cancel", "Cancel the Appointment"),
        telebot.types.BotCommand("help", "Guide to use the Bot")
    ],
    scope=telebot.types.BotCommandScopeAllPrivateChats()  # use for all private chats
)

user_states = {}

# States
ASKING_EMAIL = "asking email"
CONFIRM_EMAIL = "confirm email"

@bot.message_handler(commands=['start'])
def start_commands(message):
    user = message.from_user
    user_states[user.id] = {"user_data": user}  # Store user data for later logging
    
    bot.send_message(
        chat_id=message.chat.id,
        text='''Terms and Conditions:

1. After booking an appointment, you are required to pay a 75 Euro fee within 24 hours. Failure to do so will result in the cancellation of your appointment.

2. Our algorithms search for available free time slots only. While you cannot request a specific date, you can suggest your preferred date, and we will prioritize it if available.

3. You are responsible for entering accurate information and verifying it before submitting. Any issues that arise due to incorrect information entered are your sole responsibility.'''
    )

    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('I agree ✅', callback_data="2")
    keyboard.row(button)

    bot.send_message(message.chat.id, 'Please check the box below to indicate that you have read and agree to all the Terms and Conditions mentioned above:', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help_commands(message):
    bot.send_message(message.chat.id, 'I am a GetMyTermin bot. Please specify your Termin')


@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    if call.data == "2":
        # ask for email
        bot.send_message(call.message.chat.id, 'Please enter your email:')
        user_states[call.message.chat.id]["state"] = ASKING_EMAIL  # set the user state to "asking email"
    elif call.data == "confirm_email" and user_states.get(call.message.chat.id, {}).get("state") == CONFIRM_EMAIL:
        email = user_states[call.message.chat.id]["email"]
        bot.send_message(chat_id=call.message.chat.id, text=f'Confirmed email: {email}')
        bot.answer_callback_query(callback_query_id=call.id)
        
        # User data logging
        user = user_states[call.message.chat.id]["user_data"]
        logging.info(f'User {user.id}, username: {user.username}, first name: {user.first_name}, last name: {user.last_name}, email: {email}')
        log_text = f'New user: ID {user.id}, username: {user.username}, first name: {user.first_name}, last name: {user.last_name}, email: {email}'
        bot.send_message(chat_id=ADMIN_USER_ID, text=log_text)

        del user_states[call.message.chat.id]  # clear the state

        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton('Go to Form 📝', url="https://online.forms.app/getmyterminde/registration-form")
        keyboard.row(button)

        bot.send_message(chat_id=call.message.chat.id, text='Now, press this button to go to the appointment details form and provide the required information', reply_markup=keyboard)
    elif call.data == "edit_email" and user_states.get(call.message.chat.id, {}).get("state") == CONFIRM_EMAIL:
        bot.send_message(call.message.chat.id, 'Please enter your correct email:')
        user_states[call.message.chat.id]["state"] = ASKING_EMAIL  # set the user state back to "asking email"


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Check if we asked for email
    if user_states.get(message.chat.id, {}).get("state") == ASKING_EMAIL:
        # Save email and ask for confirmation
        user_states[message.chat.id]["email"] = message.text
        user_states[message.chat.id]["state"] = CONFIRM_EMAIL

        keyboard = InlineKeyboardMarkup()
        confirm_button = InlineKeyboardButton('Confirm ✅', callback_data="confirm_email")
        edit_button = InlineKeyboardButton('Edit ✏️', callback_data="edit_email")
        keyboard.row(confirm_button, edit_button)

        bot.send_message(message.chat.id, f'Is this your email: {message.text}?', reply_markup=keyboard)


@bot.polling()
def polling():
    print('Starting bot...')
    bot.polling()


if __name__ == '__main__':
    polling()
