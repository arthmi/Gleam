# server/database.py
import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS strips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                num_leds INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                strip_id INTEGER REFERENCES strips(id) ON DELETE CASCADE,
                led_start INTEGER NOT NULL,
                led_end INTEGER NOT NULL               
            )
        ''')
        self.conn.commit()


    def add_strip(self, name: str, num_leds: int):
        self.cursor.execute('INSERT INTO strips (name, num_leds) VALUES (?, ?)', (name, num_leds,))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_strip(self, id: int, name: str, num_leds: int):
        self.cursor.execute('UPDATE strips SET name = (?), num_leds = (?) WHERE id = (?)', (name, num_leds, id,))
        self.conn.commit()

    def delete_strip(self, sid: int):
        self.cursor.execute('DELETE FROM strips WHERE id = (?)', (id,))
        self.conn.commit()

    def get_strips(self, id=None):
        if id:
            self.cursor.execute('SELECT * FROM strips WHERE id = ?', (id,))
        else:
            self.cursor.execute('SELECT * FROM strips')
        return self.cursor.fetchall()


    def add_group(self, name: str, strip_id: int, start: int, end: int):
        self.cursor.execute('INSERT INTO groups (name, strip_id, led_start, led_end) VALUES (?, ?, ?, ?)', (name, strip_id, start, end,))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_group(self, id: int, name: str, start: int, end: int):
        self.cursor.execute('UPDATE groups SET name = (?), start = (?), end = (?) WHERE id = (?)', (name, start, end, id,))
        self.conn.commit()

    def delete_group(self, id: int):
        self.cursor.execute('DELETE FROM groups WHERE id = (?)', (id,))
        self.conn.commit()

    def get_groups(self, id=None):
        if id is not None:
            self.cursor.execute('SELECT * FROM groups WHERE id = ?', (id,))
        else:
            self.cursor.execute('SELECT * FROM groups')
        return self.cursor.fetchall()


    def close(self):
        if self.conn:
            self.conn.close()