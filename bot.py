import os
os.system('pip install -r requirements.txt')
import yaml
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ForceReply, error, ReplyKeyboardRemove
import mysql.connector
import logging


class telegramBot:
    def __init__(self, sqlink, cursor):
        self.inline_subject_keyboard = [
            [InlineKeyboardButton("➕Aggiungi una materia➕", callback_data='add_subject')],
            [InlineKeyboardButton("➖Rimuovi una materia➖", callback_data='delete_subject')]
        ]
        self.inline_subject_keyboard_markup = InlineKeyboardMarkup(self.inline_subject_keyboard)
        self.subject_keyboard = []
        self.inline_notes_keyboard = [
            [InlineKeyboardButton("➕Aggiungi un appunto➕", callback_data='add_notes')],
            [InlineKeyboardButton("➖Rimuovi un appunto➖", callback_data='delete_notes')],
            [InlineKeyboardButton("⏎Indietro⏎", callback_data='notes_back')]
        ]
        self.inline_notes_keyboard_markup = InlineKeyboardMarkup(self.inline_notes_keyboard)
        self.notes_keyboard = []
        self.sqlink = sqlink
        self.cursor = cursor
        self.notes_list = []
        self.updater = Updater(yamlConfig()['api-token'], use_context=True)  # riceve gli aggiornamenti da telegram e li da al
        # dispatcher,'use_context=True' è molto utile perché genererà ulteriori informazioni riguardante l'evento
        self.dispatcher = self.updater.dispatcher  # fa da "postino", spedisce gli aggiornamenti a chi deve gestirli
        directory = os.listdir()
        if "Subjects" not in directory:
            os.mkdir("Subjects")
        self.bot()

    def bot(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        # il logging è obbligatorio perché la libreria telegram.ext genera dei log
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("help_appunti", self.help_appunti))
        self.dispatcher.add_handler(CallbackQueryHandler(self.button))
        self.dispatcher.add_handler(CommandHandler("lista_materie", self.subjectList))
        self.updater.start_polling()
        self.updater.idle()

    def start(self, update, context):
        self.chat_id = update.message.chat_id  # la variabile 'update' restituisce un JSON contentente tutte le informazioni
        # al momento di un interazione col bot (id utente, id chat, nome utente, etc.)
        self.user_id = update.effective_user.id
        self.first_name = update.message.from_user.first_name
        self.last_name = update.message.from_user.last_name
        if self.last_name == None:
            self.last_name = 'NULL'
        self.username = update.message.from_user.username
        self.group_name = update.message.chat.title
        if self.group_name == None:
            self.group_name = "NULL" 
        select_query = f"SELECT * from appartiene WHERE id_utente = {self.user_id} AND id_chat = {self.chat_id};"
        self.cursor.execute(select_query)
        results = self.cursor.fetchall()
        check = False
        for x in results:
            if self.user_id in x and self.chat_id in x:
                check = True
        if not check:
                insert = f"INSERT IGNORE INTO utente VALUES ({self.user_id}, '{self.first_name}', '{self.last_name}', '{self.username}');"
                self.cursor.execute(insert)
                self.sqlink.commit()
                insert = f"INSERT IGNORE INTO chat VALUES ({self.chat_id}, '{self.group_name}');"
                self.cursor.execute(insert)
                self.sqlink.commit()
                insert = f"INSERT IGNORE INTO appartiene VALUES ({self.user_id}, {self.chat_id});"
                self.cursor.execute(insert)
                self.sqlink.commit() 
        context.bot.send_message(chat_id=update.effective_chat.id, text="@appuntiDDI_bot ti permette di organizzare gli"
                                                                        " appunti e suddividerli per materia, premi o "
                                                                        "digita /help per informazioni più dettagliate")

    def help(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="ELENCO DEI COMANDI\n\n➤/lista_materie ➝ "
                                                                        "visualizza l'elenco delle materie con la "
                                                                        "possibilità di aggiungerne altre (➕Aggiungi "
                                                                        "una materia➕) o rimuoverle "
                                                                        "(➖Rimuovi una materia➖)"
                                                                        "\n\➤/help_appunti ➝ guida su come mandare gli appunti")

    def help_appunti(self, update, context):
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('help_appunti_phone.jpg', 'rb'), caption="Come mandare una foto come appunto da cellulare (Selezionare la foto, andare sui tre puntini verticali in alto a destra e premere 'Invia senza compressione')")
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('help_appunti_pc.jpg', 'rb'), caption="Come mandare una foto come appunto da PC (togliere la spunta a 'Comprimi immagini')")

    def subjectList(self, update, context):
        directory = os.listdir()
        if "Subjects" not in directory:
            os.mkdir("Subjects")
        self.chat_id = update.message.chat_id  # la variabile 'update' restituisce un JSON contentente tutte le informazioni
        # al momento di un interazione col bot (id utente, id chat, nome utente, etc.)
        self.user_id = update.effective_user.id
        self.first_name = update.message.from_user.first_name
        self.last_name = update.message.from_user.last_name
        if self.last_name == None:
            self.last_name = 'NULL'
        self.username = update.message.from_user.username
        self.group_name = update.message.chat.title
        if self.group_name == None:
            self.group_name = "NULL" 
        select_query = f"SELECT * from appartiene WHERE id_utente = {self.user_id} AND id_chat = {self.chat_id};"
        self.cursor.execute(select_query)
        results = self.cursor.fetchall()
        check = False
        for x in results:
            if self.user_id in x and self.chat_id in x:
                check = True
        if not check:
                insert = f"INSERT IGNORE INTO utente VALUES ({self.user_id}, '{self.first_name}', '{self.last_name}', '{self.username}');"
                self.cursor.execute(insert)
                self.sqlink.commit()
                insert = f"INSERT IGNORE INTO chat VALUES ({self.chat_id}, '{self.group_name}');"
                self.cursor.execute(insert)
                self.sqlink.commit()
                insert = f"INSERT IGNORE INTO appartiene VALUES ({self.user_id}, {self.chat_id});"
                self.cursor.execute(insert)
                self.sqlink.commit()
        select_query = f"SELECT nome_materia from materie where id_materia IN (SELECT id_materia from inserisce where id_chat = {self.chat_id});"
        self.cursor.execute(select_query)
        results = self.cursor.fetchall()
        check = False
        reload_keyboard = False
        if results:
            if len(self.subject_keyboard) != 0:
                reload_keyboard = True
            check = True
        if check:
            if reload_keyboard:
                while self.inline_subject_keyboard:
                    self.inline_subject_keyboard.pop()
                while self.subject_keyboard:
                    self.subject_keyboard.pop()
                self.inline_subject_keyboard = [
                    [InlineKeyboardButton("➕Aggiungi una materia➕", callback_data='add_subject')],
                    [InlineKeyboardButton("➖Rimuovi una materia➖", callback_data='delete_subject')]
                ]
                self.subject_keyboard = []
        for x in results:
            ik = [InlineKeyboardButton(f"{x[0]}", callback_data=f"{x[0]}")]
            k = [KeyboardButton(text=f"{x[0]}")]
            self.inline_subject_keyboard.insert(0, ik)
            self.subject_keyboard.insert(0, k)
        self.inline_subject_keyboard_markup = InlineKeyboardMarkup(self.inline_subject_keyboard)
        update.message.reply_text('Aggiungi una materia o selezionane una già esistente:', reply_markup=self.inline_subject_keyboard_markup)

    def button(self, update, context):
        chat_id = update.effective_chat.id  # l'update sarà nullo se passato ad un ad un altra funzione, il context no
        query = update.callback_query  # interroga il bot per vedere quale bottone è stato premuto
        query.answer()
        selected_option = f"{query.data}"
        global selected_function
        selected_function = selected_option
        select = f"SELECT percorso_appunti FROM appunti WHERE id_inserimento IN (SELECT id_inserimento FROM inserisce WHERE id_materia IN (SELECT id_materia FROM materie WHERE nome_materia='{selected_option}'));"
        try:
            self.cursor.execute(select)
            results = self.cursor.fetchall()
            for x in results:
                notes = ''
                notes_path = x[0]
                slash_counter = 0
                for x in notes_path:
                    if x == '/':
                        slash_counter += 1
                    if slash_counter == 3:
                        notes += x
                notes = notes.replace('/', '') 
                self.notes_list.append(notes)
        except Exception:
            None
        if selected_option == "add_subject":
            context.bot.send_message(chat_id=chat_id, text="Inserisci la materia", reply_markup=ForceReply(selective=False))
            self.readMessage()
        if selected_option == "delete_subject":
            if len(self.inline_subject_keyboard) == 2:
                context.bot.send_message(chat_id=chat_id, text="Non ci sono materie da rimuovere!\nAggiungine prima una!")
            else:
                self.checkIfDelete(context, chat_id)
        if str(selected_option) in self.notes_list:
            select_subject_query = f"SELECT nome_materia FROM materie WHERE id_materia IN (SELECT id_materia FROM inserisce WHERE id_chat = {chat_id} AND id_inserimento = (SELECT id_inserimento FROM appunti WHERE percorso_appunti LIKE '%{selected_option}'));"
            self.cursor.execute(select_subject_query)
            results = self.cursor.fetchone()
            subject = results[0]
            context.bot.send_document(chat_id=chat_id, document=open(f"Subjects/{chat_id}/{subject}/{selected_option}", "rb"))
        if selected_option not in self.notes_list != "add_subject" and selected_option != "delete_subject" and selected_option != "add_notes" and selected_option != "delete_notes" and selected_option != "notes_back":
            self.subject_notes = query.data
            context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
            select_query = f"SELECT percorso_appunti FROM appunti WHERE id_inserimento IN (SELECT id_inserimento FROM inserisce WHERE id_chat = {chat_id} AND id_materia IN (SELECT id_materia FROM materie WHERE nome_materia = '{self.subject_notes}'));"
            self.cursor.execute(select_query)
            results_notes = self.cursor.fetchall()
            check = False
            reload_notes_keyboard = False
            if results_notes:
                if len(self.notes_keyboard) != 0:
                    reload_notes_keyboard = True
                check = True
            if check:
                if reload_notes_keyboard:
                    while self.inline_notes_keyboard:
                        self.inline_notes_keyboard.pop()
                    while self.notes_keyboard:
                        self.notes_keyboard.pop()
                    self.inline_notes_keyboard = [
                        [InlineKeyboardButton("➕Aggiungi un appunto➕", callback_data='add_notes')],
                        [InlineKeyboardButton("➖Rimuovi un appunto➖", callback_data='delete_notes')],
                        [InlineKeyboardButton("⏎Indietro⏎", callback_data='notes_back')]
                    ]  
                    self.notes_keyboard = []
            for x in results_notes:
                path = ''
                slash_counter = 0
                for y in x[0]:
                    if y == '/':
                        slash_counter += 1
                    if slash_counter == 3:
                        path += y
                path = path.replace('/', '')
                ik = [InlineKeyboardButton(f"{path}", callback_data=f"{path}")]
                k = [KeyboardButton(text=f"{path}")]
                self.inline_notes_keyboard.insert(0, ik)
                self.notes_keyboard.insert(0, k)  
            self.inline_notes_keyboard_markup = InlineKeyboardMarkup(self.inline_notes_keyboard)              
            context.bot.send_message(chat_id=chat_id, text=f"Aggiungi un appunto per {self.subject_notes} o selezionane una già esistente:", 
                                    reply_markup=self.inline_notes_keyboard_markup)
        if selected_option == "add_notes":
            context.bot.send_message(chat_id=chat_id, text='Manda il tuo file...', reply_markup=ForceReply(selective=False))
            self.notesHandler()
        if selected_option == "delete_notes":
            if len(self.inline_notes_keyboard) == 3:
                context.bot.send_message(chat_id=chat_id, text="❎Non ci sono appunti da rimuovere!❎\nAggiungine prima alcuni!")
            else:
                self.checkIfDeleteNotes(context, chat_id)
        if selected_option == "notes_back":
            context.bot.send_message(chat_id=chat_id, text="Tornando indierto...")
            context.bot.send_message(chat_id=chat_id, text='Aggiungi una materia o selezionane una già esistente:', reply_markup=self.inline_subject_keyboard_markup)


    def checkIfDelete(self, context, chat_id):
        reply_keyboard_markup = ReplyKeyboardMarkup(self.subject_keyboard, resize_keyboard=True, one_time_keyboard=True)
        context.bot.send_message(chat_id=chat_id, text="Seleziona la materia da rimuovere\n\n⚠ATTENZIONE⚠\nSe rimuovi un appunto esso verrà rimosso DEFINITIVAMENTE",
                                 reply_markup=reply_keyboard_markup)
        self.readMessage()

    def checkIfDeleteNotes(self, context, chat_id):
        reply_notes_keyboard_markup = ReplyKeyboardMarkup(self.notes_keyboard, resize_keyboard=True, one_time_keyboard=True)
        context.bot.send_message(chat_id=chat_id, text="Seleziona l'appunto da rimuovere\n\n⚠ATTENZIONE⚠\nSe rimuovi una materia, tutti gli appunti ad essa associata verranno rimossi DEFINITIVAMENTE",
                                 reply_markup=reply_notes_keyboard_markup)
        self.readMessage()    

    def readMessage(self):
        try:
            self.dispatcher.add_handler(MessageHandler(Filters.text & ~ Filters.command, self.addAndDelete))
        except ValueError:
            self.readMessage()

    def addAndDelete(self, update, context):
        chat_id = update.effective_chat.id
        if selected_function == 'add_subject':
            subject = update.message.text
            select_query = f"SELECT nome_materia FROM materie WHERE nome_materia = '{subject}' AND id_materia IN (SELECT id_materia FROM inserisce WHERE id_chat = {update.effective_chat.id});"
            self.cursor.execute(select_query)
            results = self.cursor.fetchall()
            if not results:
                select_materie = f"SELECT * FROM materie WHERE nome_materia = '{subject}';"
                self.cursor.execute(select_materie)
                results_materie = self.cursor.fetchall()
                if not results_materie:
                    insert = f"INSERT INTO materie (nome_materia) VALUES ('{subject}');"
                    self.cursor.execute(insert)
                    self.sqlink.commit()
                select = f"SELECT id_materia FROM materie WHERE nome_materia = '{subject}';"
                self.cursor.execute(select)
                result_id = self.cursor.fetchone()
                result_id = result_id[0]
                inserisce = f"INSERT INTO inserisce (id_materia, id_utente, id_chat) VALUES ({result_id}, {update.effective_user.id}, {update.effective_chat.id});"
                self.cursor.execute(inserisce)
                self.sqlink.commit()
                context.bot.send_message(chat_id=update.effective_chat.id,
                                        text="🖋Materia aggiunta con successo!🖋\n\nControlla premendo o digitando /lista_materie")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="❎La materia è già inserita!❎")
        elif selected_function == 'delete_subject':
            subject = update.message.text
            delete = f"DELETE FROM inserisce WHERE id_materia = (SELECT id_materia FROM materie WHERE nome_materia = '{subject}');"
            self.cursor.execute(delete)
            self.sqlink.commit()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="🗑️Materia rimossa con successo!🗑️\n\nControlla premendo o digitando /lista_materie",
                                     reply_markup=ReplyKeyboardRemove())
            os.system(f"rm -r Subjects/{chat_id}/{subject}")
        if selected_function == "delete_notes":
            notes = update.message.text
            select_query = f"SELECT percorso_appunti FROM appunti WHERE percorso_appunti LIKE '%{notes}';"
            self.cursor.execute(select_query)
            results = self.cursor.fetchone()
            path = results[0]
            delete = f"DELETE FROM appunti WHERE percorso_appunti = '{path}';"
            self.cursor.execute(delete)
            self.sqlink.commit()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"{notes} rimosso con successo!🗑️\n\nControlla premendo o digitando /lista_materie",
                                     reply_markup=ReplyKeyboardRemove())
            os.remove(path)
    
    def notesHandler(self):
        try:
            self.dispatcher.add_handler(MessageHandler((Filters.document | Filters.photo) &  ~ (Filters.command | Filters.text), self.addNotes))
        except ValueError:
            self.notesHandler()

    def addNotes(self, update, context):
        if selected_function == "add_notes":
            try:
                chat_id = update.effective_chat.id
                document = update.message.document
                file = context.bot.getFile(document)
                name = document.file_name
            except error.TelegramError:
                photo = update.message.photo
                file = context.bot.get_file(photo)
                name = photo.file_unique_id
            select_query = f"SELECT id_inserimento FROM inserisce WHERE id_chat = {chat_id} AND id_materia = (SELECT id_materia FROM materie WHERE nome_materia = '{self.subject_notes}');"
            self.cursor.execute(select_query)
            results = self.cursor.fetchone()
            id_inserimento = results[0]
            if file.file_size > 20:
                try:
                    create_directory = f"Subjects/{chat_id}"
                    os.mkdir(create_directory)
                except FileExistsError:
                    print("Cartella già esistente, creazione della sottocartella...")
                try:
                    create_directory = f"Subjects/{chat_id}/{self.subject_notes}"
                    os.mkdir(create_directory)
                    print("Sottocartella creata")
                except FileExistsError:
                    print("Sottocartella già esistente")
                path = f"Subjects/{chat_id}/{self.subject_notes}/{name}"
                file.download(path)
                insert = f"INSERT INTO appunti (percorso_appunti, id_inserimento) VALUES ('{str(path)}', {int(id_inserimento)});"
                self.cursor.execute(insert)
                self.sqlink.commit()
                context.bot.send_message(chat_id=update.effective_chat.id, text="✍Appunto aggiunto con successo!✍")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text='❎Il file non può superare 20MB!❎')

def yamlConfig():
    with open('config.yaml', 'r') as ymlconfig:
        config = yaml.load(ymlconfig, Loader=yaml.FullLoader)
    return config


def main():
    yaml_config = yamlConfig()
    sqlink = mysql.connector.connect(
        host=yaml_config['host'],
        port=yaml_config['port'],
        user=yaml_config['user'],
        password=yaml_config['password'],
        database=yaml_config['database']
    )
    cursor = sqlink.cursor(buffered=True)
    telegramBot(sqlink, cursor)


main()
