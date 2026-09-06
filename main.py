import os

from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove()

cancel_button = "Отмена 🚫"
skip_button = "Пропустить ⏭"


def cansel(message):
    bot.send_message(message.chat.id, "Чтобы посмотреть команды, используй - /info", reply_markup=hideBoard)


def no_projects(message):
    bot.send_message(message.chat.id, 'У тебя пока нет проектов!\nМожешь добавить их с помощью команды /new_project')


def gen_inline_markup(rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(row, callback_data=row))
    return markup


def gen_markup(rows):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup


attributes_of_projects = {'⭐ Имя проекта': ["Введите новое имя проекта", "project_name"],
                          "📝 Описание": ["Введите новое описание проекта", "description"],
                          "🔗 Ссылка": ["Введите новую ссылку на проект", "url"],
                          "📊 Статус": ["Выберите новый статус проекта", "status_id"],
                          "🖼 Фото": ["Отправь новое фото проекта", "photo"]}


def save_photo(message):
    photo = message.photo[-1]
    file_id = photo.file_id
    os.makedirs('imgs', exist_ok=True)
    saved_name = f"{file_id}.jpg"
    with open(os.path.join('imgs', saved_name), 'wb') as f:
        f.write(bot.download_file(bot.get_file(file_id).file_path))
    return saved_name


def info_project(message, user_id, project_name):
    info = manager.get_project_info(user_id, project_name)[0]
    skills = manager.get_project_skills(project_name)
    if not skills:
        skills = 'Навыки пока не добавлены'
    bot.send_message(message.chat.id, f"""📌 Project name: {info[0]}
📝 Description: {info[1]}
🔗 Link: {info[2]}
📊 Status: {info[3]}
📸 Photo: {info[4] or 'нет'}
🛠 Skills: {skills}
""")


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "👋 Привет! Я бот-менеджер проектов!\nПомогу тебе сохранить твои проекты и информацию о них! 🚀\n")
    info(message)


@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,
"""
📚 Вот команды, которые тебе помогут:

📌 /new_project - добавить новый проект
📂 /projects - посмотреть список проектов
🛠 /skills - добавить навыки к проекту
✏️ /update_projects - изменить проект
🗑 /delete - удалить проект

Также ты можешь просто ввести имя проекта и я покажу о нём всё! 😉""", reply_markup=hideBoard)


@bot.message_handler(commands=['new_project'])
def addtask_command(message):
    bot.send_message(message.chat.id, "📌 Введите название проекта:")
    bot.register_next_step_handler(message, name_project)


def name_project(message):
    data = [message.from_user.id, message.text]
    bot.send_message(message.chat.id, "🔗 Введите ссылку на проект:")
    bot.register_next_step_handler(message, link_project, data=data)


def link_project(message, data):
    data.append(message.text)
    statuses = [x[0] for x in manager.get_statuses()]
    bot.send_message(message.chat.id, "📊 Введите текущий статус проекта:", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)


def callback_project(message, data, statuses):
    if message.text == cancel_button:
        cansel(message)
        return
    if message.text not in statuses:
        bot.send_message(message.chat.id, "Ты выбрал статус не из списка, попробуй ещё раз!)",
                         reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)
        return
    data.append(manager.get_status_id(message.text))
    bot.send_message(message.chat.id, "📝 Введите описание проекта или нажми 'Пропустить ⏭'")
    bot.register_next_step_handler(message, description_project, data=data)


def description_project(message, data):
    data.append('' if message.text in (skip_button, cancel_button) else message.text)
    bot.send_message(message.chat.id, "📸 Отправьте фото проекта или нажми 'Пропустить ⏭'")
    bot.register_next_step_handler(message, photo_project, data=data)


def photo_project(message, data):
    if message.content_type == 'photo':
        data.append(save_photo(message))
    elif message.text in (skip_button, cancel_button):
        data.append('')
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправь фото или нажми 'Пропустить ⏭'")
        bot.register_next_step_handler(message, photo_project, data=data)
        return
    manager.insert_project([tuple(data)])
    bot.send_message(message.chat.id, "Проект сохранён! 🎉 Добавить навыки можно командой /skills")


@bot.message_handler(commands=['skills'])
def skill_handler(message):
    projects = manager.get_projects(message.from_user.id)
    if not projects:
        no_projects(message)
        return
    projects = [x[2] for x in projects]
    bot.send_message(message.chat.id, '🛠 Выбери проект, для которого нужно указать навык',
                     reply_markup=gen_markup(projects))
    bot.register_next_step_handler(message, skill_project, projects=projects)


def skill_project(message, projects):
    if message.text == cancel_button:
        cansel(message)
        return
    if message.text not in projects:
        bot.send_message(message.chat.id, 'У тебя нет такого проекта, попробуй ещё раз!',
                         reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
        return
    skills = [x[1] for x in manager.get_skills()]
    bot.send_message(message.chat.id, 'Выбери навык', reply_markup=gen_markup(skills))
    bot.register_next_step_handler(message, set_skill, project_name=message.text, skills=skills)


def set_skill(message, project_name, skills):
    if message.text == cancel_button:
        cansel(message)
        return
    if message.text not in skills:
        bot.send_message(message.chat.id, 'Видимо, ты выбрал навык не из списка, попробуй ещё раз!',
                         reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)
        return
    manager.insert_skill(message.from_user.id, project_name, message.text)
    bot.send_message(message.chat.id, f'Навык {message.text} добавлен проекту {project_name} ✅\n'
                                      f'Можно добавить ещё с помощью /skills')


@bot.message_handler(commands=['projects'])
def get_projects(message):
    projects = manager.get_projects(message.from_user.id)
    if not projects:
        no_projects(message)
        return
    text = "\n".join([f"📌 {x[2]} \n🔗 {x[4]}\n" for x in projects])
    bot.send_message(message.chat.id, text, reply_markup=gen_inline_markup([x[2] for x in projects]))


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    info_project(call.message, call.from_user.id, call.data)
    bot.answer_callback_query(call.id)


@bot.message_handler(commands=['delete'])
def delete_handler(message):
    projects = manager.get_projects(message.from_user.id)
    if not projects:
        no_projects(message)
        return
    text = "\n".join([f"📌 {x[2]} \n🔗 {x[4]}\n" for x in projects])
    projects = [x[2] for x in projects]
    bot.send_message(message.chat.id, text, reply_markup=gen_markup(projects))
    bot.register_next_step_handler(message, delete_project, projects=projects)


def delete_project(message, projects):
    if message.text == cancel_button:
        cansel(message)
        return
    if message.text not in projects:
        bot.send_message(message.chat.id, 'У тебя нет такого проекта, попробуй выбрать ещё раз!',
                         reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
        return
    user_id = message.from_user.id
    manager.delete_project(user_id, manager.get_project_id(message.text, user_id))
    bot.send_message(message.chat.id, f'Проект {message.text} удалён! 🗑')


@bot.message_handler(commands=['update_projects'])
def update_project(message):
    projects = manager.get_projects(message.from_user.id)
    if not projects:
        no_projects(message)
        return
    projects = [x[2] for x in projects]
    bot.send_message(message.chat.id, "✏️ Выбери проект, который хочешь изменить",
                     reply_markup=gen_markup(projects))
    bot.register_next_step_handler(message, update_project_step_2, projects=projects)


def update_project_step_2(message, projects):
    if message.text in (cancel_button, *projects):
        if message.text == cancel_button:
            cansel(message)
        else:
            bot.send_message(message.chat.id, "Выбери, что требуется изменить в проекте",
                             reply_markup=gen_markup(attributes_of_projects.keys()))
            bot.register_next_step_handler(message, update_project_step_3, project_name=message.text)
        return
    bot.send_message(message.chat.id, "Что-то пошло не так! Выбери проект ещё раз:",
                     reply_markup=gen_markup(projects))
    bot.register_next_step_handler(message, update_project_step_2, projects=projects)


def update_project_step_3(message, project_name):
    label = message.text
    if label == cancel_button:
        cansel(message)
        return
    if label not in attributes_of_projects:
        bot.send_message(message.chat.id, "Кажется, ты ошибся, попробуй ещё раз!",
                         reply_markup=gen_markup(attributes_of_projects.keys()))
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)
        return
    attribute = attributes_of_projects[label][1]
    markup = gen_markup([x[0] for x in manager.get_statuses()]) if 'Статус' in label else None
    bot.send_message(message.chat.id, attributes_of_projects[label][0], reply_markup=markup)
    bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attribute)


def update_project_step_4(message, project_name, attribute):
    user_id = message.from_user.id
    if attribute == 'photo':
        if message.content_type == 'photo':
            value = save_photo(message)
        elif message.text == cancel_button:
            cansel(message)
            return
        else:
            bot.send_message(message.chat.id, "Отправь фото проекта!")
            bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attribute)
            return
    else:
        if message.text == cancel_button:
            cansel(message)
            return
        value = message.text
        if attribute == 'status_id':
            statuses = [x[0] for x in manager.get_statuses()]
            if value in statuses:
                value = manager.get_status_id(value)
            else:
                bot.send_message(message.chat.id, "Был выбран неверный статус, попробуй ещё раз!",
                                 reply_markup=gen_markup(statuses))
                bot.register_next_step_handler(message, update_project_step_4, project_name=project_name,
                                               attribute=attribute)
                return
    manager.update_projects(attribute, (value, project_name, user_id))
    bot.send_message(message.chat.id, "Готово! Обновления внесены! ✅")


@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    if message.text in projects:
        info_project(message, user_id, message.text)
        return
    bot.reply_to(message, "Тебе нужна помощь?")
    info(message)


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()