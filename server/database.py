# server/database.py
import sqlite3
import threading

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._local = threading.local()
        self._write_lock = threading.Lock()

        self._init_leds_db()
        self._init_scenes_db()

    @property
    def conn(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.execute("PRAGMA foreign_keys = ON")
        return self._local.conn

    @property
    def cursor(self):
        if not hasattr(self._local, 'cursor'):
            self._local.cursor = self.conn.cursor()
        return self._local.cursor

    def _init_leds_db(self):
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

    def _init_scenes_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scene_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id INTEGER NOT NULL REFERENCES scenes(id) ON DELETE CASCADE,
                strip_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                layer TEXT NOT NULL,        -- COLOR / INTENSITY / WHITE
                module_name TEXT NOT NULL,  -- 'blink', 'rainbow', etc.
                params TEXT NOT NULL        -- JSON string of parameters for the module
            );
        ''')
        self.conn.commit()


    def add_strip(self, name: str, num_leds: int):
        self.cursor.execute('INSERT INTO strips (name, num_leds) VALUES (?, ?)', (name, num_leds,))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_strip(self, id: int, name: str, num_leds: int):
        self.cursor.execute('UPDATE strips SET name = (?), num_leds = (?) WHERE id = (?)', (name, num_leds, id,))
        self.conn.commit()

    def delete_strip(self, id: int):
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



    def add_scene(self, name: str, module_name: str, config: str):
        self.cursor.execute('INSERT INTO scenes (name) VALUES (?)', (name,))
        scene_id = self.cursor.lastrowid
        self.cursor.execute('INSERT INTO scene_modules (scene_id, module_name, params) VALUES (?, ?, ?)', (scene_id, module_name, config,))
        self.conn.commit()
        return scene_id
    
    def update_scene(self, id: int, name: str, module_name: str, config: str):
        self.cursor.execute('UPDATE scenes SET name = (?) WHERE id = (?)', (name, id,))
        self.cursor.execute('UPDATE scene_modules SET module_name = (?), params = (?) WHERE scene_id = (?)', (module_name, config, id,))
        self.conn.commit()

    def delete_scene(self, id: int):
        self.cursor.execute('DELETE FROM scene_modules WHERE scene_id = (?)', (id,))
        self.cursor.execute('DELETE FROM scenes WHERE id = (?)', (id,))
        self.conn.commit()

    def get_scenes(self, id: int|None=None):
        if id is not None:
            self.cursor.execute('SELECT * FROM scenes WHERE id = ?', (id,))
        else:
            self.cursor.execute('SELECT * FROM scenes')
        return self.cursor.fetchall()



    def close(self):
        if self.conn:
            self.conn.close()