import logging
from typing import Final
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN: Final = '5796108934:AAFH4J0IFNo5eGSiiyhqsh7oB93UHaY3iUY'
BOT_USERNAME: Final = '@MyDreams20bot'
ADMIN_USER_ID: Final = 5355774833  # Admin's user ID

ASKING_EMAIL = "ASKING_EMAIL"
CONFIRM_EMAIL = "CONFIRM_EMAIL"
SENDING_MESSAGE = "SENDING_MESSAGE"
CANCEL_PENDING = "CANCEL_PENDING"
CONTACTING_ADMIN = "CONTACTING_ADMIN"

user_states = {}

logging.basicConfig(filename='user_data.log', level=logging.INFO, format='%(asctime)s - %(message)s')

bot = telebot.TeleBot(TOKEN)

bot.delete_my_commands(scope=None, language_code=None)

bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Book an Appointment"),
        telebot.types.BotCommand("cancel", "Cancel the Appointment"),
        telebot.types.BotCommand("payment", "PayPal"),
        telebot.types.BotCommand("contact_us", "Tap to contact the Admin"),
    ],
    scope=telebot.types.BotCommandScopeAllPrivateChats()  # use for all private chats
)

@bot.message_handler(commands=['start'])
def start_commands(message):
    user_states[message.chat.id] = {
        "state": CONFIRM_EMAIL, 
        "email": None,
    }

    user = message.chat
    log_text = f'User {user.id}, first name: {user.first_name}, last name: {user.last_name}, username: {user.username}'
    
    # Log the user's information to 'user_data.log'
    logging.info(log_text)
    
    # Send the user's information to the admin
    bot.send_message(chat_id=ADMIN_USER_ID, text=log_text)

    bot.send_message(
        message.chat.id,
        '''Terms and Conditions:

1. After booking an appointment, you are required to pay a 30 Euro fee within 24 hours. Failure to do so will result in the cancellation of your appointment.

2. Our algorithms search for available free time slots only. While you cannot request a specific date, you can suggest your preferred date, and we will prioritize it if available.

3. You are responsible for entering accurate information and verifying it before submitting. Any issues that arise due to incorrect information entered are your sole responsibility.'''
    
    )

    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('I agree ✅', callback_data="2")
    keyboard.row(button)

    bot.send_message(message.chat.id, 'Please check the box below to indicate that you have read and agree to all the Terms and Conditions mentioned above:', reply_markup=keyboard)

@bot.message_handler(commands=['cancel'])
def cancel_commands(message):
    keyboard = InlineKeyboardMarkup()
    yes_button = InlineKeyboardButton('Yes', callback_data="confirm_cancel")
    no_button = InlineKeyboardButton('No', callback_data="deny_cancel")
    keyboard.row(yes_button, no_button)
    
    bot.send_message(
        message.chat.id,
        'Are you sure you want to cancel your appointment booking request?',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['payment'])
def payment_commands(message):

    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('PayPal', url="https://www.paypal.me/GetMyTermin")
    keyboard.row(button)
    bot.send_message(message.chat.id, text='Please use this button to pay the 30 euros fee.', reply_markup=keyboard)

@bot.message_handler(commands=['contact_us'])
def contact_us_commands(message):
    user_states[message.chat.id] = {
        "state": CONTACTING_ADMIN, 
        "message": None,
    }
    bot.send_message(message.chat.id, 'Please type your message:')

@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    if call.data == "2":
        bot.send_message(call.message.chat.id, 'Please enter your email:')
        user_states[call.message.chat.id]["state"] = ASKING_EMAIL
    elif call.data.startswith("send_msg_to_"):
        user_id = call.data.replace("send_msg_to_", "")
        user_states[ADMIN_USER_ID] = {
            "state": SENDING_MESSAGE,
            "to_user_id": user_id,
        }
        bot.answer_callback_query(call.id)
        bot.send_message(ADMIN_USER_ID, 'Please enter the message you want to send to the user:')
    elif call.data == "confirm_email" and user_states.get(call.message.chat.id, {}).get("state") == CONFIRM_EMAIL:
        email = user_states[call.message.chat.id].get("email")

        user = call.message.chat.id
        log_text = f'User {user}, email: {email}'

        # Add this line to log the user data into user_data.log file
        logging.info(f'User Data: User ID = {user}, Email = {email}')


        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton('Reply to this user ✏️', callback_data=f"send_msg_to_{user}")
        keyboard.row(button)

        bot.send_message(chat_id=ADMIN_USER_ID, text=log_text, reply_markup=keyboard)

        keyboard = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton('Go to English 🇬🇧 Form 📝', url="https://online.forms.app/getmyterminde/registration-form")
        button2 = InlineKeyboardButton('Go to Deutsch 🇩🇪 Form 📝', url="https://view.forms.app/getmyterminde/anmeldeformular")
        keyboard.row(button1)
        keyboard.row(button2)
        bot.send_message(chat_id=call.message.chat.id, text='Now, press this button to go to the appointment details form and provide the required information', reply_markup=keyboard)
        bot.answer_callback_query(callback_query_id=call.id)
    elif call.data == "edit_email" and user_states.get(call.message.chat.id, {}).get("state") == CONFIRM_EMAIL:
        bot.send_message(call.message.chat.id, 'Please enter your email again:')
        user_states[call.message.chat.id]["state"] = ASKING_EMAIL
        bot.answer_callback_query(callback_query_id=call.id)
    elif call.data == "confirm_cancel":
        user_id = call.message.chat.id
        user_states[user_id] = {
            "state": None,
            "email": None,
        }
        bot.send_message(user_id, 'Your appointment booking request has been cancelled successfully.')

        if user_id == ADMIN_USER_ID:
            bot.send_message(ADMIN_USER_ID, f'The admin has cancelled the appointment booking request.')
        else:
            bot.send_message(ADMIN_USER_ID, f'User with ID {user_id} has cancelled their appointment booking request.')

    elif call.data == "deny_cancel":
        user_id = call.message.chat.id
        bot.send_message(user_id, 'Continuing with your appointment booking request.')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if user_states.get(chat_id, {}).get("state") == ASKING_EMAIL:
        user_states[chat_id]["email"] = message.text
        user_states[chat_id]["state"] = CONFIRM_EMAIL
        keyboard = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton('Confirm ✅', callback_data="confirm_email")
        button2 = InlineKeyboardButton('Edit ✏️', callback_data="edit_email")
        keyboard.row(button1, button2)
        bot.send_message(chat_id, f'Do you confirm this email address: {message.text}', reply_markup=keyboard)
    elif user_states.get(chat_id, {}).get("state") == SENDING_MESSAGE:
        to_user_id = user_states[chat_id].get("to_user_id")
        bot.send_message(to_user_id, message.text)
        user_states[chat_id]["state"] = None
        bot.send_message(chat_id, 'Your message has been sent.')
    elif user_states.get(chat_id, {}).get("state") == CONTACTING_ADMIN:
        user_states[chat_id]["message"] = message.text
        user_states[chat_id]["state"] = None
        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton('Reply to this user ✏️', callback_data=f"send_msg_to_{chat_id}")
        keyboard.row(button)
        bot.send_message(ADMIN_USER_ID, f'User with ID {chat_id} sent this message:\n\n{message.text}', reply_markup=keyboard)
        bot.send_message(chat_id, 'Your message has been received and will be replied as soon as possible.')
    else:  # This is where we handle unrecognizable messages
        bot.send_message(chat_id, "This message is not recognizable. To communicate with the admin, please select the /contact_us option from the bot's menu.")
        
        user = message.chat
        log_text = f'Unrecognized message from User {user.id}, first name: {user.first_name}, last name: {user.last_name}, username: {user.username}, message: {message.text}'

        # Log the unrecognized message to 'user_data.log'
        logging.info(log_text)

bot.polling(none_stop=True, interval=0, timeout=20)
