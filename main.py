import mysql.connector
from config import db_config
from telegrambot import start_bot
import urllib.request
import xml.dom.minidom as minidom


db_names = 'realtor'
creat_tables_offer = """CREATE TABLE IF NOT EXISTS offer (id_offer int AUTO_INCREMENT, internal int not null, 
            types varchar(50) not null, category varchar(50) not null, price int not null, PRIMARY KEY (id_offer));"""


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


def creat_db_base(connection, db):
    cursor = connection.cursor()
    creat_base_db = "CREATE DATABASE IF NOT EXISTS " + db
    cursor.execute(creat_base_db)
    connection.commit()
    cursor.close()
    connection.close()


def creat_db_tables(connection, creat_tables):
    cursor = connection.cursor()
    cursor.execute(creat_tables)
    connection.commit()
    cursor.close()
    connection.close()


def get_data(xml_url):
    try:
        web_file = urllib.request.urlopen(xml_url)
        return web_file.read()
    except:
        pass


def get_elements(xml_content, elenents_tag_name, tag_name):
    dom = minidom.parseString(xml_content)
    dom.normalize()

    elements = dom.getElementsByTagName(elenents_tag_name)
    elements_dict = []
    for node in elements:
        for child in node.childNodes:
            if child.nodeType == 1:
                if child.tagName == tag_name:
                    if child.firstChild.nodeType == 3:
                        elements_dict.append(child.firstChild.data)
    return elements_dict


def list_add_elements(list_elements=(), list_dict_elements=()):
    for add_elements in range(len(list_dict_elements)):
        if list_elements[add_elements].isalpha():
            list_dict_elements[add_elements] = list(list_dict_elements[add_elements])
            list_dict_elements[add_elements].append(list_elements[add_elements])
            list_dict_elements[add_elements] = tuple(list_dict_elements[add_elements])
        elif list_elements[add_elements].isdigit():
            list_dict_elements[add_elements] = list(list_dict_elements[add_elements])
            list_dict_elements[add_elements].append(int(list_elements[add_elements]))
            list_dict_elements[add_elements] = tuple(list_dict_elements[add_elements])
        else:
            list_dict_elements[add_elements] = list(list_dict_elements[add_elements])
            list_dict_elements[add_elements].append(list_elements[add_elements])
            list_dict_elements[add_elements] = tuple(list_dict_elements[add_elements])
    return list_dict_elements


def get_currencies_dictionary(xml_content):
    dom = minidom.parseString(xml_content)
    dom.normalize()

    main_elements = "offer"
    price_elements = "price"
    elements = dom.getElementsByTagName(main_elements)
    type_tag_name = "type"
    category_tag_name = "category"
    price_tag_name = "value"
    currency_dict = []

    for node in elements:
        main_dict = list()
        main_dict.append(int(node.getAttribute("internal-id")))
        currency_dict.append(tuple(main_dict))

    currency_dict = list_add_elements(get_elements(xml_content, main_elements, type_tag_name), currency_dict)
    currency_dict = list_add_elements(get_elements(xml_content, main_elements, category_tag_name), currency_dict)
    currency_dict = list_add_elements(get_elements(xml_content, price_elements, price_tag_name), currency_dict)
    insert_tables_db(create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"],
                                                db_config["mysql"]["pass"], db_names), currency_dict)


def insert_tables_db(connection, insert_list):
    cursor = connection.cursor()
    insert_list = list(audit_db_parxml(insert_list))
    if len(insert_list) > 0:
        for insert_tables_list in insert_list:
            cursor.execute("""INSERT INTO offer (internal, types, category, price) VALUES (%s, %s, %s, %s);""",
                           insert_tables_list)
            connection.commit()
    else:
        pass
    cursor.close()
    connection.close()


def audit_db_parxml(list_parsxml):
    connection = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"],
                                            db_config["mysql"]["pass"], db_names)
    list_parsxml = set(list_parsxml)
    cursor = connection.cursor()
    cursor.execute("""SELECT internal, types, category, price from offer;""")
    data_tables = cursor.fetchall()
    cursor.close()
    connection.close()
    data_tables = set(data_tables)
    return list_parsxml - data_tables


def print_db(connection):
    str_db = ['аренда']
    cursor = connection.cursor()
    list_1 = ("""SELECT types from offer""")
    list_2 = ("""SELECT types, category FROM offer WHERE types = %s;""", str_db)
    cursor.execute("""SELECT types, category FROM offer WHERE types = %s;""", [str_db[0]])
    data_tables = cursor.fetchall()
    cursor.close()
    connection.close()
    print(len(data_tables))


if __name__ == '__main__':
    url = 'https://feed-p.topnlab.ru/download/base/?data=objects&chosen=1&format=yandex&key=WluHFbXNa6uYi5Wa4XY%3D'
    creat_db_base(create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"],
                                             db_config["mysql"]["pass"]), db_names)
    creat_db_tables(create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"],
                                               db_config["mysql"]["pass"], db_names), creat_tables_offer)
    get_currencies_dictionary(get_data(url))
#    print_db(create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"],
#                                        db_config["mysql"]["pass"], db_names))
    start_bot()
