import telegram

# Replace 'YOUR_API_TOKEN' with the API token you received from the BotFather
bot = telegram.Bot(token='6114910026:AAGGPogroG1BvkHA3LOTab_0EzBqqi3JQYM')

# Replace 'USER_ID' with the actual user ID you want to send the message to
user_id = '161111997'

# Replace 'YOUR_MESSAGE' with the text message you want to send
message = 'YOUR_MESSAGE'

bot.send_message(chat_id=user_id, text=message)





    keyboard = [
        [
            InlineKeyboardButton("Go to Form", url='https://online.forms.app/getmyterminde/registration-form'),
            InlineKeyboardButton("Help", callback_data="2"),
        ],
        [InlineKeyboardButton("Pay with PayPal", url='https://www.paypal.me/GetMyTermin')],
    ]