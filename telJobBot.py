
import time,copy,json
from abc import ABC
import telebot,logging
from telebot import types
from telebot.custom_filters import SimpleCustomFilter, AdvancedCustomFilter,IsReplyFilter
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pymongo
import re
import jdatetime,datetime
#import urllib.parse

#username = urllib.parse.quote_plus('admin')
#password = urllib.parse.quote_plus('M!l@d724')
#myclient = pymongo.MongoClient('mongodb://%s:%s@localhost:27017/?authMechanism=DEFAULT' % (username, password))

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["telebot"]

logger = telebot.logger

logger.setLevel(logging.DEBUG) # Outputs debug messages to console.
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
fileHandler = logging.FileHandler("{0}/{1}.log".format("./", "telebot"))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

TOKEN = '6114910026:AAGGPogroG1BvkHA3LOTab_0EzBqqi3JQYM'

def db_user_writer(msg,access):
    mycol = mydb["users"]
    print(msg)
    dic={"user_id": msg.from_user.id, "first_name": msg.from_user.first_name,"access":access}
    if 'last_name' in msg.from_user.__dict__:
        dic['last_name']=msg.from_user.last_name
    if 'username' in msg.from_user.__dict__:
        dic['username']=msg.from_user.username
    mycol.replace_one({"user_id":dic["user_id"]},dic,True)

    return 0

def db_user_query(dic={}):
    mycol = mydb["users"]
    return list(mycol.find(dic))

def db_logger(dic):
    mycol=mydb["log"]
    mycol.insert_one(dic)
    return 0

adv_data={}
adv_id={}
reply_msg="پیغامی وجود ندارد"
message_id={}
adv_admin={}
reason_id={}
admin_group_id="-702682161"
admin_group_id="-238163702"
admin_channel_id="-1001135056135"
call_id_check=[]

help='''
✅ لطفا موارد خواسته شده را به ترتیب و با دقت تکمیل نمایید.

✅ دقت کنید که موارد خواسته شده در قالب یک پیام و به صورت پاسخ به پیغام ربات ارسال شود.

✅ در صورت نیاز به ثبت چند مورد می توانید موارد را با کاما از یکدیگر تفکیک کنید.

✅ در صورت نیاز پیغام ارسال شده خود را ویرایش کنید.

✅ آگهی ارسال شده پس از تایید توسط ادمین در کانال قرار داده می شود.
'''

titles={
    "job_title":{"fa": "موقعیت شغلی","en":"job title","msg":"موقعیت شغلی مورد نظر را وارد کنید (در صورت وجود چند مورد با کاما تفکیک کنید) :"},
    "date":{"fa":  "تاریخ","en":"date","msg":"تاریخ آگهی را وارد کنید :"},
    "location":{ "fa":"محل کار","en":"location","msg":"محل کار را وارد کنید (در صورت وجود چند مورد با کاما تفکیک کنید) :"},
    "description": {"fa":"توضیحات","en":"description","msg":"توضیحات را در یک پیام وارد کنید :"},
    "company": {"fa":"شرکت","en":"company","msg":"شرکت را وارد کنید (در صورت وجود چند مورد با کاما تفکیک کنید) :"},
    "contact_info":{"fa": "اطلاعات تماس","en":"contact info","msg":'اطلاعات تماس را در قالب یک پیام وارد کنید :'}
}

def adv_data_remains(adv_data):
    remained = [key for key in list(adv_data) if adv_data[key] is None]
    return remained

def adv_entity(titles=titles):
    return {key:None for key in list(titles)}

def adv_msg(uid,adv_data=adv_data,titles=titles,return_title=False,return_step=False):
    if uid in list(adv_data):
        if len(adv_data_remains(adv_data[uid]))==0:
            adv_data[uid]['step']='submit'
        if return_step:
            return adv_data[uid]['step']
        if return_title:
            return adv_data_remains(adv_data[uid])[0]
        if adv_data[uid]['step']=='fill':
            return titles[adv_data_remains(adv_data[uid])[0]]["msg"]
        else:
            return adv_data[uid]['step']
    return "not_started"

def adv_formater(input_str,type):
    if type=='hashtag':
        input_str=input_str.replace("#", "")
        input_str=re.sub(' +', ' ', input_str)
        if '،' in input_str:
            return " ".join(["#" + item.strip().replace(" ", "_") for item in input_str.split('،') if item !=" " and item !="" ])
        else:
            return " ".join(["#" + item.strip().replace(" ", "_") for item in input_str.split(',') if item !=" " and item !="" ])

def msg_gen(adv_text):
    print(adv_text)

    result=f"""
موقعیت شغلی:  {adv_text["job_title"]}

تاریخ: {adv_text["date"]}

محل کار: {adv_text["location"]}

توضیحات:

{adv_text["description"]}

شرکت: {adv_text["company"]}

اطلاعات تماس: {adv_text["contact_info"]}


@IranTelecomJobs

    """
    return result

legal='\n\nکاربر گرامی، کانال هیچ گونه مسئولیتی در مورد صحت آگهی و اعتبار و صلاحیت کارفرما ندارد، شما مختارید بنا به صلاحدید خود نسبت به تحقیق در مورد کارفرما و تماس و یا عقد قرارداد اقدام کنید.'

imageSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)  # create the image selection keyboard
imageSelect.add('Mickey', 'Minnie')
startSelect=types.ReplyKeyboardMarkup(one_time_keyboard=True)
startSelect.add('start')
hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard
markup = types.ForceReply(selective=False)

# error handling if user isn't known yet
# (obsolete once known users are saved to file, because all users
#   had to use the /start command and are therefore known to the bot)

# def get_user_step(uid):
#     if uid in userStep:
#         return userStep[uid]
#     else:
#         knownUsers.append(uid)
#         userStep[uid] = 0
#         print("New user detected, who hasn't used \"/start\" yet")
#         return 0

def knownUsers():
    query=db_user_query()
    user_ids=[record['user_id'] for record in query if (record['access']=='known' or record['access']=='admin')]
    return user_ids

def adminUsers():
    query=db_user_query()
    user_ids=[record['user_id'] for record in query if (record['access']=='admin')]
    return user_ids

def userData(uid):
    user_info=db_user_query({"user_id":uid})[0]
    del user_info['_id'],user_info['access']
    result=""
    for key in user_info:
        result=result+"\n"+f"{key} : {user_info[key]}"
    return result

def date_fill(local='fa'):
    if local=='fa':
        return jdatetime.datetime.now().strftime("%d/%m/%Y")
    elif local=='en':
        return datetime.datetime.now().strftime("%Y/%m/%d")

# only used for console output now
def listener(messages):

    """
    When new messages arrive TeleBot will call this function.

    """

    for m in messages:
        print(str(m))
        print(str(m.chat.first_name) +" UID["+str(m.from_user.id) +"] CID[" + str(m.chat.id) + "]: " + m.text)

bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener
bot.delete_my_commands(scope=None, language_code=None)
bot.set_my_commands(

    commands=[
        telebot.types.BotCommand("start_adv", "شروع آگهی"),
        telebot.types.BotCommand("cancel_adv", "لغو آگهی جاری"),
        telebot.types.BotCommand("help", "راهنمای استفاده از ربات")
    ],

    # scope=telebot.types.BotCommandScopeChat(12345678)  # use for personal command for users
    scope=telebot.types.BotCommandScopeAllPrivateChats()  # use for all private chats
)

# check command
cmd = bot.get_my_commands(scope=None, language_code=None)
print([c.to_json() for c in cmd])

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data="/start_adv"), InlineKeyboardButton("No", callback_data="cb_no"))
    return markup

def start_adv_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("شروع", callback_data="cb_start_adv"))
    return markup

def submit_adv_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton("تایید", callback_data="cb_submit_adv"),InlineKeyboardButton("ویرایش", callback_data="cb_edit_adv"),InlineKeyboardButton("لغو", callback_data="cb_cancel_adv"))
    return markup

def admin_adv_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("تایید", callback_data="cb_accept_adv"),InlineKeyboardButton("رد", callback_data="cb_reject_adv"))
    return markup

def check_reply(message,reply_to_text):
    print(reply_to_text)
    if isinstance(message, types.CallbackQuery):
        if message.message.reply_to_message is not None :
            return message.message.reply_to_message.from_user.id==5419926132 and  reply_to_text in message.message.reply_to_message.text
    if message.reply_to_message is not None:
        return message.reply_to_message.from_user.id==5419926132 and  reply_to_text in message.reply_to_message.text

# handle the "/start" command

@bot.message_handler(commands=['start'],chat_types=['private'])
def command_start(m):
    cid = m.chat.id
    uid=m.from_user.id
    if uid not in knownUsers():
        bot.send_message(cid, "سلام، به ربات IranTelecomJobs خوش اومدین.")
        db_user_writer(m, 'known')
    # if uid not in adminUsers():  # if user hasn't used the "/start" command yet:
    #     bot.send_message(cid, "اسم شما در لیست ثبت کنندگان آگهی نیست!")
    #     bot.send_message(cid, "در صورت نیاز از ادمین بخواین شما رو به لیست ثبت کنندگان آگهی اضافه کنه")
    bot.send_message(cid,"ثبت آگهی",reply_markup=start_adv_markup())

@bot.message_handler(commands=['start_adv'],chat_types=['private'])
def command_start(m):
    cid = m.chat.id
    uid=m.from_user.id
    bot.send_message(cid,"ثبت آگهی",reply_markup=start_adv_markup())

@bot.message_handler(commands=['help'],chat_types=['private'])
def command_start(m):
    cid = m.chat.id
    uid=m.from_user.id
    bot.send_message(cid, help)





@bot.message_handler(commands=['cancel_adv'],chat_types=['private'])
def command_start(m):
    cid = m.chat.id
    uid=m.from_user.id
    if uid in list(adv_data):
        if adv_data[uid]['step']=='admin':
            bot.send_message(cid, "متاسفانه درخواست شما در سبد ادمین می باشد و قابل لغو نیست، شما می توانید جهت لغو به ادمین پیغام دهید.")
        else:
            del adv_data[uid]
            del adv_id[uid]
            bot.send_message(cid, "آگهی لغو شد.")
    else:
        bot.send_message(cid, "آگهی فعالی وجود ندارد.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cid=call.message.chat.id
    uid=call.from_user.id
    mid=call.message.message_id
    call_id_str=str(cid)+","+str(mid)
    if call_id_str in call_id_check:
        bot.answer_callback_query(call.id, "شما قبلا انتخاب خود را کرده اید")
        return None
    else:
        call_id_check.append(call_id_str)
    if call.data == "cb_start_adv":
        bot.answer_callback_query(call.id, "شروع ثبت آگهی")
        db_user_writer(call, 'known')
        # if uid in adminUsers():  # if user hasn't used the "/start" command yet:
        if uid in list(adv_data):
            if adv_data[uid]['step']!="admin":
                bot.send_message(cid,help)
                adv_data[uid]=adv_entity()
                adv_data[uid]['step']='fill'
                adv_id[uid]={}
                bot.send_message(cid,adv_msg(uid), reply_markup=markup)
            else:
                bot.send_message(cid, "شما قبلا آگهی ثبت کرده اید، منتظر پاسخ باشید")
        else:
            bot.send_message(cid, help)
            adv_data[uid] = adv_entity()
            adv_data[uid]['step'] = 'fill'
            adv_id[uid] = {}
            bot.send_message(cid, adv_msg(uid), reply_markup=markup)
    elif call.data == 'cb_accept_adv':
        bot.answer_callback_query(call.id, "آگهی تایید شد.")
        bot.send_message(adv_admin[call.message.message_id],"آگهی شما تایید شد و در کانال قابل مشاهده است.")
        bot.send_message(admin_channel_id,msg_gen(adv_data[adv_admin[call.message.message_id]])+legal)
        del adv_data[adv_admin[call.message.message_id]]
    elif call.data == 'cb_reject_adv':
        bot.answer_callback_query(call.id, "آگهی رد شد.")
        bot.send_message(adv_admin[call.message.message_id], "آگهی شما تایید نشد، دلیل تایید نشدن برای شما ارسال میشود.")
        reason_id[bot.send_message(cid,"لطفا دلیل را جهت ارسال به آگهی دهنده ذکر بفرمایید:",reply_markup=markup).message_id]=adv_admin[call.message.message_id]
    elif uid in list(adv_data):
        if call.data=='cb_submit_adv':
            admin_msg=bot.send_message(admin_group_id, msg_gen(adv_data[uid])+"\n"+"آگهی دهنده :"+"\n"+ userData(uid), reply_markup=admin_adv_markup())
            adv_admin[admin_msg.message_id]=uid
            bot.answer_callback_query(call.id, "آگهی جهت بررسی به ادمین ارسال شد، پس از بررسی نتیجه برای شما ارسال میگردد.")
            bot.send_message(cid, "آگهی جهت بررسی به ادمین ارسال شد، پس از بررسی نتیجه برای شما ارسال میگردد.")
        elif call.data=='cb_edit_adv':
            bot.answer_callback_query(call.id, "شما میتوانید جواب های خود به ربات را ویرایش کرده و سپس دوباره دکمه تایید را بزنید.")
            bot.send_message(cid, "شما میتوانید جواب های خود به ربات را ویرایش کرده و سپس دوباره دکمه تایید را بزنید.")
        elif call.data=='cb_cancel_adv':
            del adv_data[uid]
            del adv_id[uid]
            bot.answer_callback_query(call.id, "آکهی لغو شد.")
            bot.send_message(cid, "آگهی لغو شد.")
        else:
            bot.answer_callback_query(call.id, "موردی یافت نشد.")
    else:
        bot.answer_callback_query(call.id, "موردی یافت نشد.")

@bot.message_handler(func=lambda m :  check_reply(m,adv_msg(m.from_user.id)),chat_types=['private'])
def reply_msg(m):
    cid = m.chat.id
    uid=m.from_user.id
    adv_data[uid]['date'] = date_fill()
    subject=adv_msg(uid,return_title=True)
    print(subject)
    print(adv_data[uid])
    if subject=='job_title' or subject == 'location' or subject=='company':
        adv_data[uid][subject] = adv_formater(m.text,"hashtag")
    else:
        adv_data[uid][subject] = m.text

    adv_id[uid][m.id]= subject
    bot.send_message(cid,f" {titles[subject]['fa']} :  {adv_data[uid][subject] } ✅"  )
    print(subject)
    next_step=adv_msg(uid, return_step=True)
    if next_step =='fill':
        bot.send_message(cid,adv_msg(uid), reply_markup=markup)
    elif next_step=='submit':
        bot.send_message(cid,msg_gen(adv_data[uid]))
        bot.send_message(cid, "آیا آگهی مورد تایید است؟", reply_markup=submit_adv_markup())

@bot.message_handler(func=lambda m :  check_reply(m,"لطفا دلیل را جهت ارسال به آگهی دهنده ذکر بفرمایید:"),chat_types=['group'])
def reply_msg_admin(m):
    cid = m.chat.id
    uid=m.from_user.id
    bot.send_message(reason_id[m.reply_to_message.id],f"پیام ادمین : \n" + m.text)

@bot.message_handler(chat_types=['private'])
def default_msg(m):
    cid = m.chat.id
    uid=m.from_user.id
    if uid in list(adv_data):
        next_step = adv_msg(uid, return_step=True)
        if next_step =='submit':
            bot.send_message(cid, msg_gen(adv_data[uid]))
            bot.send_message(cid, "آیا آگهی مورد تایید است؟", reply_markup=submit_adv_markup())
        elif next_step=='fill':
            bot.send_message(cid, adv_msg(uid), reply_markup=markup)
    else:
        bot.send_message(cid, "شما آگهی فعالی ندارید، میخواهید آگهی جدیدی شروع کنید؟", reply_markup=start_adv_markup())

@bot.edited_message_handler()
def edit_msg(m):
    cid=m.chat.id
    uid=m.from_user.id
    if uid in list(adv_id) and adv_data[uid]['step']!='admin':
        if m.message_id in list(adv_id[uid]):
            subject=adv_id[uid][m.message_id]
            if subject == 'job_title' or subject == 'location' or subject == 'company':
                adv_data[uid][subject] = adv_formater(m.text, "hashtag")
            else:
                adv_data[uid][subject] = m.text
            msg=f'''
            شما {titles[subject]['fa']} را به شکل زیر ویرایش کردید.
            
            {titles[subject]['fa']} :  {adv_data[uid][subject] } ✅

            '''
            bot.send_message(cid, msg)
            next_step = adv_msg(uid, return_step=True)
            if next_step == 'submit':
                bot.send_message(cid, msg_gen(adv_data[uid]))
                bot.send_message(cid, "آیا آگهی مورد تایید است؟", reply_markup=submit_adv_markup())
            elif next_step=='fill':
                bot.send_message(cid, adv_msg(uid), reply_markup=markup)

bot.infinity_polling()

