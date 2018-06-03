#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import system
import logging
import telebot
import constants
import subprocess
import psutil

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(constants.token)

def check_message(text, chat_id):
    if (len(text)==21) and ('-' in text):
        try:
            data = text.split('-')
            #p = system((constants.env_path + " " + constants.file_path + " %d %s %s ") % (chat_id, data[0], data[1]))
            bot.send_message(chat_id,'Ожидайте...')
            
            #p = subprocess.Popen(['start', constants.env_path, constants.file_path, str(chat_id), data[0], data[1]],shell=True)
            #system(('gnome-terminal --disable-factory -e " %s %s %d %s %s"') % (constants.env_path ,constants.file_path, chat_id, data[0], data[1]))
            #system("export DISPLAY=:0")
            #p = subprocess.Popen(['gnome-terminal --tab -e "'+constants.env_path + " " +constants.file_path + " " + str(chat_id) + " " + data[0] + " " + data[1]+'"'],shell=True)
            p = subprocess.Popen(['nohup '+constants.env_path + " " +constants.file_path + " " + str(chat_id) + " " + data[0] + " " + data[1]+" &"],shell=True)        
            bot.send_message(chat_id,'Чтобы отменить нажмите на /'+str(p.pid+1))
            '''gnome-terminal
            pid = subprocess.Popen(args=[
            "gnome-terminal", "--command=python test.py"]).pid'''
            #print (p.pid)
            #bot.reply_to(, '<b>Жауап қабылданбады, толығырақ жазыңыз! Сіздің жауабыңыз сала таңдап кетуіңізге мыңызы улкен.</b>',parse_mode = "HTML")
            return True
        except Exception as e:
            print("ERROR:",e)
            return False
    return False

@bot.message_handler(commands=['start'])
def starting(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)#
    markup.row("Запросить отчет"+u"\U0001F4C8")
    bot.send_message(message.from_user.id,'Бот для получения отчета от почты Gmail, нажмите на кнопку внизу',reply_markup=markup)

@bot.message_handler(content_types=['text'])
def message_text(message):
    text = message.text
    #print(text)
    if text[0]=='/':
        try:
            pids = [p.info['pid'] for p in psutil.process_iter(attrs=['pid', 'name']) if 'python' in p.info['name']]
            if int(text[1:]) in pids:
                system('kill -9 '+text[1:])
                bot.send_message(message.from_user.id,'Процесс остановлен!')
                return
            bot.send_message(message.from_user.id,'Возможно процесс уже остановлен...')        
        except Exception as identifier:
            print(identifier)
        return
    allowed = check_message(text, message.from_user.id)
    #print(allowed)
    if not allowed:
        if text == 'Запросить отчет'+u"\U0001F4C8":
            bot.send_message(message.from_user.id,'Отправьте период сообщении в формате: 2018/02/10-2018/04/07')
            return
        bot.reply_to(message,'Неверный запрос!')
        return
    else:
        return    

@bot.callback_query_handler(func=lambda call: call.data[:4] == 'info')
def additional_info(call):
    
    info = call.data.split()[1:]
    tmp_message = "С реферером: <b>%s</b>\n" % (info[0])
    tmp_message += "Номер и utm : <b>%s</b>\n" % (info[1])
    tmp_message += "Только с номером: <b>%s</b>\n" % (info[2])
    bot.send_message(call.from_user.id,'Из всех сообщении:\n\n' + tmp_message, parse_mode = 'HTML')
                        
bot.remove_webhook()
bot.polling(True)
