import sqlite3
import os
from datetime import datetime


class DBManager:
    def __init__(self, db_path='data/scanmangas.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS Manga(
                id INTEGER PRIMARY KEY,
                title TEXT UNIQUE,
                synopsis TEXT,
                url TEXT
            );

            CREATE TABLE IF NOT EXISTS Chapitre(
                id INTEGER PRIMARY KEY,
                manga_id INTEGER,
                numero REAL,
                date_publication TEXT,
                url TEXT,
                FOREIGN KEY(manga_id) REFERENCES Manga(id)
            );

            CREATE TABLE IF NOT EXISTS Categorie(
                id INTEGER PRIMARY KEY,
                nom TEXT UNIQUE
            );

            CREATE TABLE IF NOT EXISTS Manga_Categorie(
                manga_id INTEGER,
                categorie_id INTEGER,
                PRIMARY KEY(manga_id, categorie_id)
            );
        ''')

    def insert_manga(self, title, synopsis, url, categories):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO Manga(title, synopsis, url)
            VALUES (?, ?, ?)
        ''', (title, synopsis, url))

        manga_id = cursor.lastrowid or self.get_manga_id(title)

        for cat in categories:
            cursor.execute('''
                INSERT OR IGNORE INTO Categorie(nom) VALUES (?)
            ''', (cat,))
            cat_id = cursor.execute('SELECT id FROM Categorie WHERE nom=?', (cat,)).fetchone()[0]
            cursor.execute('''
                INSERT OR IGNORE INTO Manga_Categorie VALUES (?, ?)
            ''', (manga_id, cat_id))

        self.conn.commit()
        return manga_id

    def get_manga_id(self, title):
        return self.conn.execute(
            'SELECT id FROM Manga WHERE title=?', (title,)
        ).fetchone()[0]

    def update_chapters(self, manga_id, chapters):
        existing = self.conn.execute(
            'SELECT numero FROM Chapitre WHERE manga_id=?', (manga_id,)
        ).fetchall()

        existing_nums = {row[0] for row in existing}

        for num, date, url in chapters:
            if num not in existing_nums:
                self.conn.execute('''
                    INSERT INTO Chapitre(manga_id, numero, date_publication, url)
                    VALUES (?, ?, ?, ?)
                ''', (manga_id, num, date, url))

        self.conn.commit()

    def backup_db(self):
        backup_path = f"data/backup_{datetime.now().strftime('%Y%m%d%H%M')}.db"
        self.conn.backup(sqlite3.connect(backup_path))