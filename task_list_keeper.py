import telebot
import shelve
import os

TG_TOKEN = os.getenv("TEST_LIST_KEEPER_TOKEN")
bot = telebot.TeleBot(TG_TOKEN)



@bot.message_handler(commands=['start'])
def identification(message):
    ID = str(message.chat.id)

    with shelve.open('to_do_list') as to_do:
        if not ID in to_do.keys():
            to_do[ID] = []
            bot.send_message(chat_id=ID, text='_Вы добавлены в список пользователей._', parse_mode='Markdown')
            bot.send_message(chat_id=ID,
                             text=("""Мои команды:
/new_item <текст задачи> - добавление новой задачи
Отправленная вами фотография будет прикреплена к последней созданной задаче
/all - вывод списка задач
/delete - удаление задачи"""))


@bot.message_handler(commands=['new_item'])
def new_item(message):
    ID = str(message.chat.id)

    item = message.text.split()
    with shelve.open('to_do_list') as to_do:
        to_do[ID] = to_do[ID] + [' '.join(item[1:])]

        bot.delete_message(chat_id=ID, message_id=message.message_id)
        bot.send_message(chat_id=ID, text='_Задача сохранена._', parse_mode='Markdown')


@bot.message_handler(commands=['all'])
def all(message):
    ID = str(message.chat.id)

    with shelve.open('to_do_list') as to_do:
        all_items = ''
        for item_number in range(len(to_do[ID])):
            all_items += f'*{item_number + 1}*: `{to_do[ID][item_number]}`\n'

            photo_path = os.getcwd() + os.sep + ID + os.sep + str(item_number) + '.jpg'
            if os.path.exists(photo_path):
                bot.send_message(chat_id=ID, text=all_items, parse_mode='Markdown')
                with open(photo_path, 'rb') as photo:
                    bot.send_photo(chat_id=ID, photo=photo)
                all_items = ''

        bot.delete_message(chat_id=ID, message_id=message.message_id)
        bot.send_message(chat_id=ID, text=all_items, parse_mode='Markdown')


@bot.message_handler(commands=['delete'])
def delete(message):
    ID = str(message.chat.id)

    with shelve.open('to_do_list') as to_do:
        keyboard = telebot.types.InlineKeyboardMarkup()
        for item_number in range(len(to_do[ID])):
            keyboard.add(telebot.types.InlineKeyboardButton(text=f'{item_number + 1}: {to_do[ID][item_number]}',
                                                            callback_data=str(item_number)))

        bot.delete_message(chat_id=ID, message_id=message.message_id)
        bot.send_message(chat_id=ID, text='Выберите задачу, которую вы хотите удалить: ', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def del_item(call):
    ID = str(call.message.chat.id)

    with shelve.open('to_do_list') as to_do:
        to_do[ID] = to_do[ID][:int(call.data)] + to_do[ID][int(call.data) + 1:]

        photo_path = os.getcwd() + os.sep + ID + os.sep + call.data + '.jpg'
        if os.path.exists(photo_path):
            os.remove(photo_path)

        bot.delete_message(chat_id=ID, message_id=call.message.message_id)
        bot.send_message(chat_id=ID, text='_Задача удалена._', parse_mode='Markdown')


@bot.message_handler(content_types=['photo'])
def add_photo(message):
    ID = str(message.chat.id)

    id_photo = message.photo[-1].file_id
    path_photo = bot.get_file(id_photo).file_path
    photo = bot.download_file(path_photo)

    user_dir = os.getcwd() + os.sep + ID
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)

    with shelve.open('to_do_list') as to_do:
        with open(user_dir + os.sep + str(len(to_do[ID]) - 1) + '.jpg', 'wb') as photo_file:
            photo_file.write(photo)


if __name__ == '__main__':
    bot.polling()
