from config import DATABASE
from logic import DB_Manager

manager = DB_Manager(DATABASE)
con = manager.connection
cur = manager.cursor

with con:
    cur.execute("INSERT OR IGNORE INTO status(status_name) VALUES(?)", ("Доработка",))
    cur.execute("SELECT status_id FROM status WHERE status_name = ?", ("Доработка",))
    status_id = cur.fetchone()[0]

    skills = ["Python", "Java", "Bash", "SQL", "API", "Telegram", "Flask", "HTML", "CSS"]
    skill_ids = []
    for skill in skills:
        cur.execute("INSERT OR IGNORE INTO skills(skill_name) VALUES(?)", (skill,))
        cur.execute("SELECT skill_id FROM skills WHERE skill_name = ?", (skill,))
        skill_ids.append(cur.fetchone()[0])

    cur.execute(
        "INSERT INTO projects(user_id, project_name, description, url, status_id) VALUES(?, ?, ?, ?, ?)",
        (
            0,
            "Сервер для майна и хостинга сайта",
            "Создание домашнего сервера на Ubuntu, на котором хостится Minecraft, сайт (www.femboysmp.ru) и его поддомены.",
            None,
            status_id,
        ),
    )
    project_id = cur.lastrowid

    for skill_id in skill_ids:
        cur.execute("INSERT INTO project_skills(project_id, skill_id) VALUES(?, ?)", (project_id, skill_id))

manager.close()
