#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

import telebot

bot = telebot.TeleBot('1389262284:AAEy-EyDc3XKB9DXIJ-yXE7s9Or_eEDOlgs')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Привет. Это Логик! Сейчас меня немного чинят. Давай попробуем попозже? Если что - пиши моему создателю: @notProgrammerYuk0")

bot.polling()
