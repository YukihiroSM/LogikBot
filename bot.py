from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ext
import logging
import sqlite3

DB = 'BOT_DATABASE.db'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
TOKEN = "1389262284:AAEy-EyDc3XKB9DXIJ-yXE7s9Or_eEDOlgs"
updater = ext.Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

GR_ID, USERNAME, LOGIKS = range(3)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Привет, это Логик! На данный момент я мне... кхм... Подкручивают гайки. Скоро меня закончат ремонтировать и мы поработаем снова. ')

start_handler = ext.CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.dispatcher.add_handler(ext.CallbackQueryHandler(button))
updater.start_polling()
