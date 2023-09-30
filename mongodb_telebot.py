import telebot
from pymongo import MongoClient

TOKEN = '5796108934:AAFH4J0IFNo5eGSiiyhqsh7oB93UHaY3iUY'
bot = telebot.TeleBot(TOKEN)

mongo_client = MongoClient("localhost:27017")
db = mongo_client["GetMyTermin"]
collection = db["users"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Please enter your email address:")

@bot.message_handler(func=lambda msg: msg.text is not None and '@' in msg.text and '.' in msg.text)
def email(message):
    try:
        email_data = {"user_id": message.from_user.id, "email": message.text}
        collection.insert_one(email_data)
        bot.reply_to(message, "Email stored successfully.")
    except Exception as e:
        bot.reply_to(message, "Error occurred while storing the email. Please try again.")
        
@bot.message_handler(commands=['xyz'])
def send_database(message):
    data = list(collection.find({}))
    for doc in data:
        del doc["_id"]  # We don't want to send this to the user
        bot.send_message(message.chat.id, str(doc))

bot.polling()
