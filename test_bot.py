import os
import tempfile
import types

import logic
import main

db_path = os.path.join(tempfile.gettempdir(), 'bot_test.db')
if os.path.exists(db_path):
    os.remove(db_path)

main.manager = logic.DB_Manager(db_path)
main.manager.create_tables()
main.manager.default_insert()

sent = []
pending = []


def send(chat_id, text, **kwargs):
    sent.append(text)


def reply(chat_id, text, **kwargs):
    sent.append(text)


def register_next_step(message, handler, **kwargs):
    pending.append((handler, kwargs))


def answer_callback(call_id, **kwargs):
    pass


main.bot.send_message = send
main.bot.reply_to = reply
main.bot.register_next_step_handler = register_next_step
main.bot.answer_callback_query = answer_callback


def msg(text, content_type='text'):
    return types.SimpleNamespace(
        text=text,
        content_type=content_type,
        from_user=types.SimpleNamespace(id=12345),
        chat=types.SimpleNamespace(id=1),
    )


def advance(text, content_type='text'):
    handler, kwargs = pending.pop(0)
    handler(msg(text, content_type), **kwargs)


main.start_command(msg('/start'))
main.addtask_command(msg('/new_project'))
advance('Сервер сайта')
advance('https://github.com/Enot222SJG/portfolio_bot')
advance('В процессе разработки')
advance('Домашний сервер для майнкрафта и сайта')
advance('Пропустить ⏭')

main.skill_handler(msg('/skills'))
advance('Сервер сайта')
advance('Python')

main.get_projects(msg('/projects'))
main.text_handler(msg('Сервер сайта'))

labels = list(main.attributes_of_projects.keys())
update_keys = {v[1]: k for k, v in main.attributes_of_projects.items()}
main.update_project(msg('/update_projects'))
advance('Сервер сайта')
advance(update_keys['status_id'])
advance('Завершен. Не поддерживается')
main.update_project(msg('/update_projects'))
advance('Сервер сайта')
advance(update_keys['url'])
advance('https://github.com/new')

main.delete_handler(msg('/delete'))
advance('Сервер сайта')

print('--- answer count:', len(sent))
for i, item in enumerate(sent, 1):
    print(i, repr(item))
print('--- db state:')
conn = logic.sqlite3.connect(db_path)
print('projects:', list(conn.execute('SELECT project_id, user_id, project_name, url, status_id, description, photo FROM projects')))
print('project_skills:', list(conn.execute('SELECT * FROM project_skills')))
conn.close()