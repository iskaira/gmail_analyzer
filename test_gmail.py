from __future__ import print_function
import sys
import os
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from time import gmtime, strftime
import telebot
import constants
import timeit

bot = telebot.TeleBot(constants.token)

def normalize_phone(text):
    phone='None'
    data = text.split()
    temp_index = -1
    if 'Телефон' in text:
        temp_index = (data.index('Телефон'))
    elif 'номер:' in text:
        temp_index = (data.index('номер:'))
    else:
        return 'None'
    temp_number = data[temp_index + 1]
    if temp_number[:2] in ['70','74','77','(7','87']:
        phone = temp_number
    elif temp_number[:2] in ['+7'] and len(temp_number)==2 and data[temp_index+2][0]!='(':
        phone = ''.join(data[temp_index + 1:temp_index+6])
    elif temp_number[:2] in ['+7'] and len(temp_number)==2 and data[temp_index+2][0]=='(':
        phone = ''.join(data[temp_index + 1:temp_index+4])
    elif temp_number[:2] in ['+7'] and len(temp_number)>2 and temp_number[2:4]=='(7':
        phone = ''.join(data[temp_index + 1:temp_index+5])
    else:
        phone = data[temp_index+1]    
        return False
    return phone


    
def normalize_data(text):
    global with_referer_identified
    global with_referer_unknown
    global without_referer
    global temp_info
    global musor
    global advertisements_referer
    text = text.replace("Телефон:","Телефон")
    text = text.replace("yutub:","youtube")
    phone = normalize_phone(text)
    if phone:
        if "REFERER" in text or "Рекламная система:" in text :
            not_found = True
            for i in advertisements_referer:        
                if i in text:
                    with_referer_identified+=1
                    not_found = False
                    temp_text = i+","+phone
                    temp_info.append(temp_text)
                    #print(i)
                    break
            if not_found:
                with_referer_unknown+=1
                temp_text = "Без-рефералки,"+phone
                temp_info.append(temp_text)
                #print(text)
            
        else:
            temp_text = "Без-рефералки,"+phone
            temp_info.append(temp_text)
            without_referer+=1
    else:
        musor+=1



def GetMessage(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        text = message['snippet']
        normalize_data(text)
    except Exception as e:
        print ('An error occurred: %s' % e)


#def main(chat_id):
def main(chat_id, after, before):
    try:
        #chat_id = 295091909   
        messageID=0
        SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
        store = file.Storage(constants.creditentials)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(constants.client_secret, SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http()))

        user_id='me'
        #after = '2018/02/10'
        #before = '2018/04/07'

        query = 'after:%s before:%s'%(after,before)
        print(query)

        message = bot.send_message(chat_id, "Считаю данные... <b>Ожидайте!</b>", parse_mode = 'HTML')
        
        try:
            response = service.users().messages().list(userId=user_id, q = query ).execute()
            messages = []                                 
            if 'messages' in response:
                messages.extend(response['messages'])
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
                messages.extend(response['messages'])
        except Exception as e:
            print ('An error occurred: %s' % e)
        
        num_of_messages = len(messages)
        if num_of_messages == 0:
            bot.send_message(chat_id, "Нет сообщении для обработки(\n\n<b>Проверьте правильно ли указали период.</b>", parse_mode = 'HTML')
            import sys
            sys.exit()
        bot.edit_message_text("Количество сообщении: <b>" + str(num_of_messages) +'</b>', chat_id, message_id = message.message_id, parse_mode = 'HTML')
        bot.send_message(chat_id, "Идет обработка... ", parse_mode = 'HTML')
        
        status = [int(i/(10.0)*num_of_messages) for i in range(1,11)]
        
        #print (status)
        
        message = bot.send_message(chat_id, "Ожидайте... <b>0%</b>", parse_mode = 'HTML')
    
        for msg in messages:
            messageID+=1
            #print("Message_ID:",messageID)
            GetMessage(service, user_id, msg['id'])
            if messageID in status:
                percent = str(int((messageID*1.0)/num_of_messages*100))
                bot.edit_message_text("Ожидайте... <b>" + percent+'%</b>', chat_id, message_id = message.message_id, parse_mode = 'HTML')
            
        tmp_message = ''
        tmp_message += "Общее количество сделок за период: <b>%d</b>\n" % (num_of_messages)
        tmp_message += "Уникальные заявки: <b>%d</b>\n" % (len(set(temp_info)))
        tmp_message += "Мусор: <b>%d</b>\n" % (musor)
        tmp_callback_data = "info %d %d %d" % (with_referer_identified, len(temp_info), without_referer)

        additional_info = telebot.types.InlineKeyboardMarkup()
        row = [telebot.types.InlineKeyboardButton("Подробнее...", callback_data = tmp_callback_data)]
        additional_info.row(*row)
        #if phone_number == '+77759839537':
        new_array = set(temp_info)
        results=[0,0,0,0,0,0,0,0,0,0,0]
        
        for i in new_array:
            i = i.split(',')[0]
            results[advertisements_referer.index(i)] += 1
        
        for i in range(len(results)):
            tmp_message += '<b>' + advertisements_referer[i] + ": "+str(results[i]) + '</b>\n'
        
        print(tmp_message)
        bot.send_message(chat_id, tmp_message, parse_mode='HTML', reply_markup = additional_info)        
    except Exception as e:
        print(e)

if __name__ == "__main__":
    advertisements_referer = ['youtube','vk.com','instagram','sms','yandex','telegram','facebook','google','whatsapp','biznes-bastau','Без-рефералки']
    temp_info = []
    musor = 0
    without_referer = 0
    with_referer_identified = 0
    with_referer_unknown = 0
    start = timeit.default_timer()
    #main()
    
    main(sys.argv[1],sys.argv[2],sys.argv[3])
    #main(sys.argv[1])
    #print(msg)
    stop = timeit.default_timer()
    bot.send_message(sys.argv[1],"Время выполнения: " + "%.2f" % (stop - start)+" сек." )
    