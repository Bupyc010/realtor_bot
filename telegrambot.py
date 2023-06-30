import time
import telebot
import mysql.connector
from config import db_config
from telebot import types


bot = telebot.TeleBot('none')
meseg_users = []
time_minutes = 1
senb_list = ['', '', 0, 0]
len_list_categ = ['', '']


def create_connection_mysql_db(db_host, user_name, user_password, db_name=None):
    connection_db = None
    try:
        connection_db = mysql.connector.connect(
            host=db_host,
            port=3306,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print('Подключение к MySQL успешно выполнено')
    except Exception as ex:
        print(ex)
    return connection_db


def list_offer(list_user, message):
    try:
        connection = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"],
                                                db_config["mysql"]["pass"], 'realtor')
        cursor = connection.cursor()
        cursor.execute("""SELECT internal, types, category, price from offer WHERE types = %s and 
        category = %s and price BETWEEN %s AND %s;""", list_user)
        data_tables = cursor.fetchall()
        cursor.close()
        connection.close()
        return data_tables
    except Exception as ex:
        bot.send_message(message.chat.id, 'Не все свединия внесены')


def len_category_db(str_selection, listing=[]):
    connection = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"],
                                            db_config["mysql"]["pass"], 'realtor')
    cursor = connection.cursor()
    cursor.execute(str_selection, listing)
    data_tables = cursor.fetchall()
    cursor.close()
    connection.close()
    return data_tables


def list_category_db(str_selection):
    connection = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"],
                                            db_config["mysql"]["pass"], 'realtor')
    str_db = ''
    cursor = connection.cursor()
    cursor.execute(str_selection)
    data_tables = cursor.fetchall()
    cursor.close()
    connection.close()
    data_tables = set(data_tables)
    for list_str in data_tables:
        str_db += list_str[0] + ', '
    str_db = str_db[:-2]
    return str_db


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Добро пожаловать {message.from_user.first_name} '
                                      f'{message.from_user.last_name}!\n'
                                      f'Для ознакомление работы с чато введите команду /help')


@bot.message_handler(commands=['ID'])
def id_chat(message):
    bot.send_message(message.chat.id, f'Чат ID: {message.chat.id}')


@bot.message_handler(commands=['help'])
def bot_help(message):
    bot.send_message(message.chat.id, 'Основные команды для работы с чат ботом:\n'
                                      '/help - Выводит основные команды \n'
                                      '/offer - отправка запроса для получения предложения')


#@bot.message_handler(commands=['time']) '/time - меняет отправку сообщений бота пользователю о найденых результатох\n'
def send_time(message):
    bot.send_message(message.chat.id, f'Отправка сообщений каждую {time_minutes} минуту. '
                                      f'Для изменение время отправки введите число.')
    bot.register_next_step_handler(message, change_time)


def change_time(message):
    time_minutes = int(message.text.strip())
    bot.send_message(message.chat.id, f'Время отправки сообщения сейчас каждые {time_minutes} менуты')


@bot.message_handler(commands=['offer'])
def realtor(message):
    meseg_users.clear()
#    list_types = ("""SELECT types from offer""")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Тип предложения"))
    markup.add(types.KeyboardButton("Выбор категории"))
    markup.add(types.KeyboardButton("Цена"))
    bot.send_message(message.chat.id, 'Выберете категорию для начало выборки предложений', reply_markup=markup)
#    bot.send_message(message.chat.id, f"Введите тип предложения из списка.{list_category_db(list_types)}")
#    bot.register_next_step_handler(message, user_type)


@bot.message_handler(content_types=['text'])
def send_list(message):
    if message.text == 'Тип предложения':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Аренда"), types.KeyboardButton("Продажа"))
        markup.add(types.KeyboardButton("Вернуться в главное меню"))
        bot.send_message(message.chat.id, 'Выберите один оз вариантов', reply_markup=markup)
    elif message.text == 'Выбор категории':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Участок"), types.KeyboardButton("Коттедж"), types.KeyboardButton("Таунхаус"))
        markup.add(types.KeyboardButton("Коммерческая"), types.KeyboardButton("Квартира"), types.KeyboardButton("Дом"))
        markup.add(types.KeyboardButton("Вернуться в главное меню"))
        bot.send_message(message.chat.id, 'Выберите один оз вариантов', reply_markup=markup)
    elif message.text == 'Цена':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("min Цена"), types.KeyboardButton("max Цена"))
        markup.add(types.KeyboardButton("Вернуться в главное меню"))
        bot.send_message(message.chat.id, 'Выберите один оз вариантов', reply_markup=markup)
    elif message.text == 'Продажа' or message.text == 'Аренда':
            senb_list[0] = message.text.strip().lower()
            len_list_categ[0] = message.text.strip().lower()
            list_category = ("""SELECT types, category from offer WHERE types = %s or category = %s;""")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Выбор категории"))
            markup.add(types.KeyboardButton("Цена"))
            markup.add(types.KeyboardButton("Вернуться в главное меню"))
            bot.send_message(message.chat.id, f'Данные внесены для запроса: {senb_list[0]}. '
                                              f'Количество найденных запросов {len(len_category_db(list_category, len_list_categ))}.'
                                              f' Выберете дальнейшие действия.', reply_markup=markup)
    elif message.text == 'Участок' or message.text == 'Коттедж' or message.text == 'Таунхаус' \
            or message.text == 'Коммерческая' or message.text == 'Квартира' or message.text == 'Дом':
            senb_list[1] = message.text.strip().lower()
            len_list_categ[1] = message.text.strip().lower()
            list_category = ("""SELECT types, category from offer WHERE types = %s or category = %s;""")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Тип предложения"))
            markup.add(types.KeyboardButton("Цена"))
            markup.add(types.KeyboardButton("Вернуться в главное меню"))
            bot.send_message(message.chat.id, f'Данные внесены для запроса: {senb_list[1]}. '
                                              f'Количество найденных запросов {len(len_category_db(list_category, len_list_categ))}.'
                                              f' Выберете дальнейшие действия.', reply_markup=markup)
    elif message.text == "min Цена":
        bot.send_message(message.chat.id, 'Напишите min цену:')
        bot.register_next_step_handler(message, min_price)
    elif message.text == 'max Цена':
        bot.send_message(message.chat.id, 'Напишите max цену:')
        bot.register_next_step_handler(message, max_price)
    elif message.text == 'Вернуться в главное меню':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Тип предложения"))
        markup.add(types.KeyboardButton("Выбор категории"))
        markup.add(types.KeyboardButton("Цена"))
        markup.add(types.KeyboardButton("Результат"))
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню', reply_markup=markup)
    elif message.text == 'Результат':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Тип предложения"))
        markup.add(types.KeyboardButton("Выбор категории"))
        markup.add(types.KeyboardButton("Цена"))
        markup.add(types.KeyboardButton("Вернуться в главное меню"))
        bot.send_message(message.chat.id, 'Выберете один из вариантов получения результата', reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        if len(list_offer(senb_list, message)) > 0:
            markup.add(types.InlineKeyboardButton("Список предложений", callback_data='send'))
            markup.add(types.InlineKeyboardButton("Отправка сообщений", callback_data='send_mesag'))
            bot.send_message(message.chat.id, f"Количество предложений: {len(list_offer(senb_list, message))}", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"Количество предложений: {len(list_offer(senb_list, message))}")
#    bot.register_next_step_handler(message, user_type)


def min_price(message):
    if message.text.strip().isdigit():
        senb_list[2] = int(message.text.strip())
        bot.send_message(message.chat.id, f'Данные внесены для запроса о min цыне: {senb_list[2]}. Выберете дальнейшие действия.')
    else:
        bot.send_message(message.chat.id, 'Введено не число. Повторите ваши действия с выбора Цены')


def max_price(message):
    if message.text.strip().isdigit():
        if int(message.text.strip()) > senb_list[2]:
            senb_list[3] = int(message.text.strip())
            bot.send_message(message.chat.id, f'Данные внесены для запроса о max цыне: {senb_list[3]}. Выберете дальнейшие действия.')
        else:
            bot.send_message(message.chat.id, 'Введено значение меньше min цыны. Повторите ваши действия с выбора Цены')
    else:
        bot.send_message(message.chat.id, 'Введено не число. Повторите ваши действия с выбора Цены')


@bot.callback_query_handler(func=lambda send: True)
def send_list(send):
    list_message = list_offer(senb_list, send)
    info = ''
    if send.data == 'send':
        for list_send in list_message:
            info += f'ID предложения: {list_send[0]}, тип: {list_send[1]}, категория: {list_send[2]}, цена: {list_send[3]}\n'
        bot.send_message(send.message.chat.id, info)
    elif send.data == 'send_mesag':
        for list_send in list_message:
            info = f'ID предложения: {list_send[0]}, тип: {list_send[1]}, категория: {list_send[2]}, цена: {list_send[3]}'
            bot.send_message(send.message.chat.id, info)
            time.sleep(time_minutes*60)
        bot.send_message(send.message.chat.id, "Выборка предложений закончена")


def start_bot():
    bot.polling(none_stop=True)
