import telebot
from telebot.types import *


class MyCommands:
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    def make_commands(self):
        commands = [
            {
                'name': 'start',
                'method': send_welcome
            }            
        ]
        others = [
            { 
                'wrapper': self.bot.callback_query_handler(func=lambda call: True),
                'method': test_callback
            }
        ]
        for c in commands:
            c['wrapper'](c['method'](self.bot, self.logger))

def test_callback(bot, logger):
    def wrapper(call):
        logger.info(call)
        bot.answer_callback_query(call.id, 'This is callback:'+call.data)
        bot.send_message(call.message.chat.id, 'You\' pressed a button: ' + call.data)
    return wrapper

def test_callback(bot, logger):
    def wrapper(message):
        username = message.from_user.first_name;
        bot.reply_to(message, f'Hello, {username}! Welcome to my first bot!')
        bot.send_message(message.chat.id, 'This is a message')
    return wrapper
