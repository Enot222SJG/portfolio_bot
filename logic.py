import sqlite3
from config import DATABASE

skills = [(_,) for _ in ['Python', 'SQL', 'API']]
statuses = [(_,) for _ in ['На этапе проектирования', 'В процессе разработки',
                           'Разработан. Готов к использованию.', 'Обновлен',
                           'Завершен. Не поддерживается']]


class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def default_insert(self):
        sql = 'INSERT INTO skills (skill_name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)

    def add_status(self, new_status):
        sql = 'INSERT INTO status (status_name) values(?)'
        data = [(new_status,)]
        self.__executemany(sql, data)

    def update_status(self, status_id, new_status):
        sql = 'UPDATE status SET status_name = ? WHERE status_id = ?'
        data = [(new_status, status_id)]
        self.__executemany(sql, data)

    def delete_status(self, status_id):
        sql = 'DELETE FROM status WHERE status_id = ?'
        data = [(status_id,)]
        self.__executemany(sql, data)

    def get_statuses(self):
        sql = 'SELECT status_name FROM status'
        return self.__select_data(sql)

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        return self.__select_data(sql, (status_name,))

    def get_projects(self):
        sql = """SELECT project_name, status_name, description, url, GROUP_CONCAT(skill_name)
                 FROM projects
                 LEFT JOIN status USING(status_id)
                 LEFT JOIN project_skills USING(project_id)
                 LEFT JOIN skills USING(skill_id)
                 GROUP BY project_id"""
        return self.__select_data(sql)

    def insert_project(self, user_id, project_name, description, url, status_id):
        sql = 'INSERT INTO projects (user_id, project_name, description, url, status_id) values (?, ?, ?, ?, ?)'
        data = [(user_id, project_name, description, url, status_id)]
        self.__executemany(sql, data)

    def get_project_info(self, project_id):
        sql = """SELECT project_name, description, url, status_name
                 FROM projects
                 LEFT JOIN status USING(status_id)
                 WHERE project_id = ?"""
        return self.__select_data(sql, (project_id,))

    def get_project_skills(self, project_id):
        sql = """SELECT skill_name
                 FROM skills
                 LEFT JOIN project_skills USING(skill_id)
                 WHERE project_id = ?"""
        return self.__select_data(sql, (project_id,))

    def insert_project_skills(self, project_id, skills):
        sql = 'INSERT INTO project_skills (project_id, skill_id) values (?, ?)'
        data = [(project_id, skill_id) for skill_id in skills]
        self.__executemany(sql, data)

    def update_projects(self, project_id, new_status_id):
        sql = 'UPDATE projects SET status_id = ? WHERE project_id = ?'
        data = [(new_status_id, project_id)]
        self.__executemany(sql, data)

    def get_skills(self):
        sql = 'SELECT skill_name FROM skills'
        return self.__select_data(sql)

    def insert_skill(self, new_skill):
        sql = 'INSERT INTO skills (skill_name) values(?)'
        data = [(new_skill,)]
        self.__executemany(sql, data)

    def delete_skill(self, skill_id):
        sql = 'DELETE FROM skills WHERE skill_id = ?'
        data = [(skill_id,)]
        self.__executemany(sql, data)

    def update_skill(self, skill_id, new_skill):
        sql = 'UPDATE skills SET skill_name = ? WHERE skill_id = ?'
        data = [(new_skill, skill_id)]
        self.__executemany(sql, data)

    def get_project_id(self, project_name):
        sql = 'SELECT project_id FROM projects WHERE project_name = ?'
        return self.__select_data(sql, (project_name,))

    def __repr__(self):
        return 'Класс для управления БД'


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()
    print(manager.get_statuses())
    print(manager.get_skills())
    status_id = manager.get_status_id('В процессе разработки')[0][0]
    manager.insert_project(0, 'Сервер для майна и хостинга сайта',
                           'Создание домашнего сервера на Ubuntu, на котором хостится Minecraft и сайты.',
                           '', status_id)
    project_id = manager.get_project_id('Сервер для майна и хостинга сайта')[0][0]
    manager.insert_project_skills(project_id, [1, 2, 3])
    print(manager.get_projects())
    print(manager.get_project_info(project_id))
    print(manager.get_project_skills(project_id))
    manager.update_projects(project_id, 4)
    print(manager.get_project_info(project_id))