import telebot;
from telebot import types;
import logging;
import sqlite3;
import httpx
from db import *
from api import *
from config import *
from routes import MyCommands
from util import *

db_init()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_KEY);

# get_courses()
# get_course_details()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.first_name;
    bot.reply_to(message, f'Hello, {username}! Welcome to my first bot!')
    bot.send_message(message.chat.id, 'This is a message')


@bot.message_handler(commands=['help'])
def send_help(message):
    with open('./help.md', encoding='utf-8') as f:
        help_text = f.read()
    bot.send_message(message.chat.id, help_text, parse_mode='MARKDOWNV2')

@bot.message_handler(commands=['inline_buttons'])
def send_buttons(message):
    markup = types.InlineKeyboardMarkup(row_width=8)
    b1 = types.InlineKeyboardButton('Inline Button 1', callback_data='ib1')
    b2 = types.InlineKeyboardButton('Inline Button 2', callback_data='ib2')
    b3 = types.InlineKeyboardButton('Inline Button 3', callback_data='ib3')
    markup.row(b1, b2)
    markup.row(b2, b3)
    markup.row(b3)
    bot.send_message(message.chat.id, "Help message", reply_markup=markup)

# @bot.callback_query_handler(func=lambda call: True)
# def test_callback(call):
    # # logger.info(call)
    # bot.answer_callback_query(call.id, 'This is callback:'+call.data)
    # bot.send_message(call.message.chat.id, 'You\' pressed a button: ' + call.data)

# commands = MyCommands(bot, logger)
# commands.make_commands()

@bot.message_handler(commands=['rich'])
def send_box(message):
    html = """
    <b>Bold</b>
    <i>Italic</i>
    <u>Underline</u>
    <span class="tg-spoiler">This is a spoiler</span>
    <a href="https://my.uw.edu" style="color: green;">My UW</a>
    """
    bot.send_message(message.chat.id, html, parse_mode='HTML')

@bot.message_handler(commands=['set_cookie'])
def set_session(message):
    conn = create_connection()
    cursor = conn.cursor()
    user_id = message.from_user.id
    cookie = message.text.strip()[len('/set_cookie')+1:]
    temp = get_user_cookie(cursor, user_id)
    if temp:
        update_user_cookie(cursor, user_id, cookie)
    else:
        add_user_cookie(cursor, user_id, cookie)
    conn.commit()
    bot.send_message(message.chat.id, f'Cookie set: {cookie}')
    cursor.close()
    conn.close()

@bot.message_handler(commands=['get_cookie'])
def get_cookie(message):
    conn = create_connection()
    cursor = conn.cursor()
    user_id = message.from_user.id
    temp = get_user_cookie(cursor, user_id)
    if temp:
        bot.send_message(message.chat.id, f'Cookie: {temp[0][0]}')
    else:
        bot.send_message(message.chat.id, f'You haven\'t set a cookie')
    cursor.close()
    conn.close()

@bot.message_handler(commands=['get_year'])
def get_year(message):
    year = message.text.strip()[len('/get_year')+1:]
    conn = create_connection()
    cursor = conn.cursor()
    temp = get_user_cookie(cursor, message.from_user.id)
    cursor.close()
    conn.close()
    if temp:
        cookie = temp[0][0]
    else:
        bot.send_message(message.chat.id, f'You haven\'t set a cookie')
    c = init_client(cookie)
    res = get_year_course(c, year)
    if res.status_code == 200:
        data = res.json()
        if (type(data) == dict):
            bot.send_message(message.chat.id, 'Updating cookie...')
            result = make_session(c)
            if result:
                bot.send_message(message.chat.id, 'Cookie update successful!')
                res = get_year_course(c, year)
                data = res.json()
                bot.send_message(message.chat.id, f"Data length: {len(str(data))}")
                if len(str(data)) < 50:
                    bot.send_message(message.chat.id, f"{str(data)}")
                    bot.send_message(message.chat.id, f"Cookie: {res.request.headers['cookie']}")
            else:
                bot.send_message(message.chat.id, 'Cookie update failed!\nPlease set a new cookie!')
                c.close()
                return
            # bot.send_message(meesage.chat.id, 'Need to update cookie!')
            # return

        text = ''
        for q in data:
            text += f"*{q['qtrYear']}*\n"
            for c in q['academicRecord']:
                c['credit'] = escape_text(c['credit'])
                c['credit'] = escape_text(c['grade'])
                c['courseTitle'] = escape_text(c['courseTitle'])
                text += f"__{str(c['courseCode'])}__" \
                        + f" \- _{str(c['courseTitle'])}_\n"\
                        + f" \- Credit: {c['credit']}\n" \
                        + f" \- Grade:  {c['grade']}\n"
            text += '\n'
        bot.send_message(message.chat.id, text, parse_mode='MARKDOWNV2')
    else:
        bot.send_message(message.chat.id, res.json())
    c.close()

@bot.inline_handler(lambda query: True)
@with_db
@with_client
def send_search_course_result(inline_query, conn=None, cursor=None, client=None):
    user_id = inline_query.from_user.id
    cookie = get_user_cookie(cursor, user_id)
    logger.info(inline_query)
    # logger.info(client)
    # if cookie:
        # client.headers.update({'cookie': cookie[0][0]}) 
    try:
        data = search_course(client, inline_query.query.strip())
        # logger.info('got data'+ str(len(data)))
    except Exception as e:
        logger.error(e)
        return
    if type(data) == dict:
        logger.error(str(data)[:50])
        return 
    results = []
    for c in data[:20]:
        title = f"{c['code']}: {c['title']}"
        results.append(types.InlineQueryResultArticle(
            c['courseId'],
            c['code'],
            types.InputTextMessageContent(c['code']),
            description=c['title'],
            # reply_markup=markup
        ))
    bot.answer_inline_query(inline_query.id, results)
    # c.close()


@bot.message_handler(content_types=['text'])
@with_db
def send_course(message, conn=None, cursor=None):
    # cname = message.text.strip()[len('/course')+1:]
    ccode = message.text.strip()
    temp = item_exist(cursor, 'courses', ccode, id_col='code', fields='code, title, description')
    if not temp:
        return
    c_info = [escape_text(i) for i in temp[0]]
    output = f"__{str(c_info[0])}__" \
        + f" \- _{str(c_info[1])}_\n"\
        + c_info[2]
    markup = types.InlineKeyboardMarkup(row_width=8)
    b1 = types.InlineKeyboardButton('This is a button for HHC', callback_data='ib1')
    b2 = types.InlineKeyboardButton('See Sections', callback_data='see_section ' + c_info[0])
    b3 = types.InlineKeyboardButton('Inline Button 3', callback_data='ib3')
    markup.row(b1)
    markup.row(b2, b3)
    markup.row(b3)
    bot.reply_to(message, output, parse_mode='MARKDOWNV2', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'see_section')
@with_client
def send_course_sections(call, client=None, conn=None, cursor=None):
    code = call.data.split(' ')[1]
    data = get_myplan_course_detail(client, code)
    if type(data) == dict:
        logger.error(str(data)[:30])
        return
    credit = data['courseSummaryDetails']['credit']
    subjectArea = data['courseSummaryDetails']['subjectArea']
    courseNumber = data['courseSummaryDetails']['courseNumber']
    courseTitle = data['courseSummaryDetails']['courseTitle']
    secions = data['courseOfferingInstitutionList'][0]['courseOfferingTermList'][0]['activityOfferingItemList']
    output = f"{subjectArea} {courseNumber}: {courseTitle} ({credit})\n"
    for s in sections:
        enroll_text = f"{s['enrollCount']}/{s['enrollMaximum']}" 
        output = f"{s['code']} {s['activityOfferingType']} {s['registrationCode']}" \
            + f"{enroll_text} {s['enrollStatus']}\n"
    bot.answer_callback_query(call.id, 'Sending you course section data')
    bot.send_message(call.message.chat.id, output)

bot.infinity_polling()
