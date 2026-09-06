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
                            photo TEXT,
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
        result = self.__select_data(sql, (status_name,))
        return result[0][0] if result else None

    def get_projects(self, user_id):
        sql = """SELECT project_id, user_id, project_name, description, url, status_id, photo
                 FROM projects WHERE user_id = ?"""
        return self.__select_data(sql, (user_id,))

    def get_project_info(self, user_id, project_name):
        sql = """SELECT project_name, description, url, status_name, photo
                 FROM projects
                 LEFT JOIN status USING(status_id)
                 WHERE user_id = ? AND project_name = ?"""
        return self.__select_data(sql, (user_id, project_name))

    def get_project_skills(self, project_name):
        sql = """SELECT skill_name
                 FROM skills
                 LEFT JOIN project_skills USING(skill_id)
                 LEFT JOIN projects USING(project_id)
                 WHERE project_name = ?"""
        return self.__select_data(sql, (project_name,))

    def insert_project(self, data):
        sql = 'INSERT INTO projects (user_id, project_name, url, status_id, description, photo) values (?, ?, ?, ?, ?, ?)'
        self.__executemany(sql, data)

    def insert_project_skills(self, project_id, skills):
        sql = 'INSERT INTO project_skills (project_id, skill_id) values (?, ?)'
        data = [(project_id, skill_id) for skill_id in skills]
        self.__executemany(sql, data)

    def update_projects(self, attribute, data):
        sql = f"UPDATE projects SET {attribute} = ? WHERE project_name = ? AND user_id = ?"
        self.__executemany(sql, [data])

    def get_skills(self):
        sql = 'SELECT skill_id, skill_name FROM skills'
        return self.__select_data(sql)

    def insert_skill(self, user_id, project_name, skill_name):
        sql = """INSERT INTO project_skills (project_id, skill_id)
                 SELECT p.project_id, s.skill_id
                 FROM projects p, skills s
                 WHERE p.user_id = ? AND p.project_name = ? AND s.skill_name = ?"""
        self.__executemany(sql, [(user_id, project_name, skill_name)])

    def add_skill(self, new_skill):
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

    def get_skill_id(self, skill_name):
        sql = 'SELECT skill_id FROM skills WHERE skill_name = ?'
        result = self.__select_data(sql, (skill_name,))
        return result[0][0] if result else None

    def get_project_id(self, project_name, user_id):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        result = self.__select_data(sql, (project_name, user_id))
        return result[0][0] if result else None

    def delete_project(self, user_id, project_id):
        sql = 'DELETE FROM project_skills WHERE project_id = ?'
        self.__executemany(sql, [(project_id,)])
        sql = 'DELETE FROM projects WHERE user_id = ? AND project_id = ?'
        data = [(user_id, project_id)]
        self.__executemany(sql, data)

    def __repr__(self):
        return 'Класс для управления БД'


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()