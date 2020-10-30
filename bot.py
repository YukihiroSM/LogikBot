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
@ext.run_async
def add_teacher_to_db(username, id):
    DB = 'BOT_DATABASE.db'
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    sql1 = "SELECT * FROM teachers WHERE cid={}".format(id)
    cursor.execute(sql1)
    resulting = cursor.fetchall()
    if len(resulting) == 0:
        sql = '''INSERT INTO teachers (cid, groups, chat_name)
        VALUES (?, ?, ?)'''
        logging.info("Created new Teacher: Name: {0}, ID: {1}".format(username, id))
        cursor.execute(sql, (id, "", username))
        conn.commit()
        conn.close()
        return True
    else:
        logging.info("Teacher Connected: Name: {0}, ID: {1}".format(username, id))
        return False


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Привет, это Логик! Сейчас я тебя просканирую и продлжим!')
    if add_teacher_to_db(update.effective_user.first_name, update.effective_chat.id):
        context.bot.send_message(chat_id=update.effective_chat.id, 
        text='Окей, мы теперь познакомились, {}!)'.format(update.effective_user.first_name))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
        text='О, я тебя помню, {}! Давай приступать к работе!)'.format(update.effective_user.first_name))
    keyboard = [
        [
            InlineKeyboardButton("Просмотр групп", callback_data='111'),
            InlineKeyboardButton("Добавить ученика", callback_data='222'),
        ],
        [InlineKeyboardButton("Помощь", callback_data="333"),],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Погнали к выбору!", reply_markup=reply_markup)


def teacher_admin(update, context):
    update.message.reply_text('''
    Окей. Сейчас нужно ввести ID группы:
    ''')
    return GR_ID


def gr_id(update, context):
    user= update.message.from_user
    update.message.reply_text("Отлично! Сейчас проверю, есть ли такая группа. Если нет - я её создам. ")
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    sql = '''create table if not exists {0} (
        "id" INTEGER UNIQUE, 
        "username" TEXT,
        "amount" TEXT, 
        "teacher_id" TEXT,
        PRIMARY KEY("id" AUTOINCREMENT))'''.format('"' + update.message.text + '"') #Checking if group exist
    cursor.execute(sql)
    sql = ''' SELECT groups FROM teachers WHERE cid={}'''.format(update.effective_chat.id) #Getting all group id's of teacher
    cursor.execute(sql)
    current_groups = cursor.fetchall()
    ids = current_groups[0][0].split('A')
    current_groups = current_groups[0][0]

    if update.message.text.split(' ')[0] not in ids or len(ids) == 0:
        current_groups += update.message.text + "A"
        sql = '''UPDATE teachers SET groups=? WHERE cid=?'''
        cursor.execute(sql, (current_groups, update.effective_chat.id))
    
    sql = ''' UPDATE teachers SET gr_id_req=? WHERE cid=?'''
    cursor.execute(sql, (update.message.text, update.effective_chat.id))
    conn.commit()
    conn.close()
    update.message.reply_text("Теперь введите имя ученика: ")
    return USERNAME


def username(update, context):
    user = update.message.from_user
    update.message.reply_text("Проверяю, нет ли ученика с таким именем...🔄")
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    sql = ''' SELECT gr_id_req FROM teachers WHERE cid={}'''.format(update.effective_chat.id)
    cursor.execute(sql)
    gr_id = cursor.fetchall()[0][0]
    sql = "SELECT username FROM {}".format('"' + gr_id + '"')

    cursor.execute(sql)
    usernames = cursor.fetchall()
    for i in range(len(usernames)):
        usernames[i] = usernames[i][0]
    print(usernames)
    if update.message.text in usernames:
        update.message.reply_text("Такой ученик уже есть в данной группе! Нужно придумать другое имя! Начните сначала -)")
        conn.commit()
        conn.close()
        keyboard = [
        [
            InlineKeyboardButton("Просмотр групп", callback_data='111'),
            InlineKeyboardButton("Добавить ученика", callback_data='222'),
        ],
        [InlineKeyboardButton("Помощь", callback_data="333"),],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Погнали к выбору!", reply_markup=reply_markup)
        return ext.ConversationHandler.END

    update.message.reply_text("Ок, такого ученика нет! Создаем!\n Чтобы прекратить - используйте команду /cancel")
    update.message.reply_text("Введите начальное количество логиков цифрами: ")
    sql = ''' UPDATE teachers SET username_req=? WHERE cid=?'''
    cursor.execute(sql, (update.message.text, update.effective_chat.id))
    conn.commit()
    conn.close()
    return LOGIKS
    

def logiks(update, context):
    user = update.message.from_user
    update.message.reply_text("Такс, провожу финальные подсчёты!")

    if not update.message.text.isdigit():
        update.message.reply_text("Вы ввели не число. Нужно начать сначала!")
        return ext.ConversationHandler.END
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    sql = ''' UPDATE teachers SET logiks_req=? WHERE cid=?'''
    cursor.execute(sql, (update.message.text, update.effective_chat.id))
    sql = ''' SELECT gr_id_req FROM teachers WHERE cid={}'''.format(update.effective_chat.id)
    cursor.execute(sql)
    gr_id = '"' + cursor.fetchall()[0][0] + '"'

    sql = ''' SELECT username_req FROM teachers WHERE cid={}'''.format(update.effective_chat.id)
    cursor.execute(sql)
    username = '"' + cursor.fetchall()[0][0] + '"' 

    sql = ''' SELECT logiks_req FROM teachers WHERE cid={}'''.format(update.effective_chat.id)
    cursor.execute(sql)
    amount ='"' +  cursor.fetchall()[0][0] + '"'
    sql = "INSERT INTO {0}(username, amount, teacher_id) VALUES ({1}, {2}, {3})".format(gr_id, username, amount, update.effective_chat.id)
    cursor.execute(sql)
    conn.commit()
    conn.close()
    update.message.reply_text("Процесс добавления ученика окончен!")
    update.message.reply_text("Ученик добавлен успешно!")
    keyboard = [
        [
            InlineKeyboardButton("Просмотр групп", callback_data='111'),
            InlineKeyboardButton("Добавить ученика", callback_data='222'),
        ],
        [InlineKeyboardButton("Помощь", callback_data="333"),],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Погнали к выбору!", reply_markup=reply_markup)
    return ext.ConversationHandler.END


def group_view(update, context):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    sql = ''' SELECT groups FROM teachers WHERE cid={}'''.format(update.effective_chat.id)
    cursor.execute(sql)
    groups = cursor.fetchone()[0].split('A')
    conn.commit()
    conn.close()
    groups = groups[:len(groups)-1]
    if len(groups) == 0:
        keyboard = [
        [
            InlineKeyboardButton("Просмотр групп", callback_data='111'),
            InlineKeyboardButton("Добавить ученика", callback_data='222'),
        ],
        [InlineKeyboardButton("Помощь", callback_data="333"),],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="У Вас ещё нет групп!")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Погнали к выбору!", reply_markup=reply_markup)
        return
    keyboard = []
    for group in groups:
        keyboard.append([InlineKeyboardButton(group, callback_data=group+'g')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Теперь нажми на одну из них, чтобы просмотреть!", reply_markup=reply_markup)
    

def group_conv():
    conv_handler = ext.ConversationHandler(
        entry_points=[ext.CommandHandler('view', group_view)],
        states={},
        fallbacks=[ext.CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)    


def cancel(update, context):
    update.message.reply_text("Процесс окончен!")
    return ext.ConversationHandler.END


def people_conv():
    conv_handler = ext.ConversationHandler(
        entry_points=[ext.CommandHandler('teacher_admin', teacher_admin)],
        states={
            GR_ID: [ext.MessageHandler(ext.Filters.text & ~ext.Filters.command, gr_id)],
            USERNAME: [ext.MessageHandler(ext.Filters.text & ~ext.Filters.command, username)],
            LOGIKS: [ext.MessageHandler(ext.Filters.text & ~ext.Filters.command, logiks)],
        },
        fallbacks=[ext.CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)


def show_group(id, update, context):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    sql = ''' SELECT * FROM {}'''.format('"' + id +'"')
    cursor.execute(sql)
    group = cursor.fetchall()
    text = ""
    sql = ''' UPDATE teachers SET gr_id_req=? WHERE cid=?'''
    cursor.execute(sql, (id, update.effective_chat.id))
    conn.commit()
    for people in group:
        text += str(group.index(people)+1)+ '. ' + people[1] + " -> " + people[2] + '\n'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    keyboard=[[InlineKeyboardButton("Изменить логики", callback_data='ch_l'+id)],
                [InlineKeyboardButton("Закрыть", callback_data='закрыть')],]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Нажми кнопку ниже, чтобы изменить логики, или закрыть, чтобы отменить.', reply_markup=reply_markup)


def change_logiks():
    conv_handler = ext.ConversationHandler(
        entry_points=[ext.CommandHandler('change', logik_change)],
        states={
            LOGIKS: [ext.MessageHandler(ext.Filters.text & ~ext.Filters.command, enter_logiks)],
        },
        fallbacks=[ext.CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)


def logik_change(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Отлично! Теперь через пробел введите логики для всех ребят.")
    return LOGIKS


def enter_logiks(update, context):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    sql = ''' SELECT gr_id_req FROM teachers WHERE cid={}'''.format(update.effective_chat.id)
    cursor.execute(sql)
    gr_id= cursor.fetchall()[0][0]
    conn.close()
    context.bot.send_message(chat_id=update.effective_chat.id, text="Сейчас всё проверим.")
    data = update.message.text.split()
    conn = sqlite3.connect(DB)
    cursor= conn.cursor()
    sql = "SELECT username FROM {}".format('"' + gr_id + '"')
    cursor.execute(sql)
    usernames = cursor.fetchall()
    if len(usernames) != len(data):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Количество введённых цифр не равно количеству детей. Давайте сначала!")
        keyboard = [
        [
            InlineKeyboardButton("Просмотр групп", callback_data='111'),
            InlineKeyboardButton("Добавить ученика", callback_data='222'),
        ],
            [InlineKeyboardButton("Помощь", callback_data="333"),],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Погнали к выбору!", reply_markup=reply_markup)
        conn.close()
        return ext.ConversationHandler.END
    else:
        sql = "SELECT amount FROM {}".format('"' + gr_id + '"')
        cursor.execute(sql)
        data_log = cursor.fetchall()
        
        for i in range(len(usernames)):
            
            sql = 'UPDATE {0} SET amount={1} WHERE username={2}'.format('"' + gr_id + '"','"' + str(int(data_log[i][0]) + int(data[i])) + '"', '"' + usernames[i][0] + '"' )
            cursor.execute(sql)
        conn.commit()
        conn.close()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Логики изменены!")
        keyboard = [
        [
            InlineKeyboardButton("Просмотр групп", callback_data='111'),
            InlineKeyboardButton("Добавить ученика", callback_data='222'),
        ],
            [InlineKeyboardButton("Помощь", callback_data="333"),],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Погнали к выбору!", reply_markup=reply_markup)
        conn.close()
        return ext.ConversationHandler.END
    

def button(update, context):
    querry = update.callback_query
    querry.answer()
    if querry.data == '1' or querry.data == '2':
        querry.edit_message_text(text="You selected {}".format(querry.data))
    elif querry.data == '222':
        querry.edit_message_text(text="Начинаю процес создания ученика! Для этого нажмите на команду: \n /teacher_admin")
        logging.info("{0} : {1} Is now creating people!".format(update.effective_user.first_name, update.effective_chat.id))        
        people_conv()
    elif querry.data == '111':
        querry.edit_message_text(text="Ох, сейчас покопаюсь... \n Нужна помощь! Нажми на команду /view")
        group_conv()
    elif querry.data == '3' or querry.data == '4':
        querry.edit_message_text(text="You selected2 {}".format(querry.data))       
    elif querry.data == 'закрыть':
        keyboard = [
        [
            InlineKeyboardButton("Просмотр групп", callback_data='111'),
            InlineKeyboardButton("Добавить ученика", callback_data='222'),
        ],
        [InlineKeyboardButton("Помощь", callback_data="333"),],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Погнали к выбору!", reply_markup=reply_markup)
    elif querry.data[:4] == 'ch_l':
        querry.edit_message_text(text="Ок, меняем логики в группе номер: {}. \n Нажмите на команду: /change".format(querry.data[4:len(querry.data)]))
        change_logiks()
    else:
        querry.edit_message_text(text="Ок, открываю группу номер: {}".format(querry.data[:len(querry.data)-1]))
        show_group(querry.data[:len(querry.data)-1], update, context)



start_handler = ext.CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.dispatcher.add_handler(ext.CallbackQueryHandler(button))
updater.start_polling()