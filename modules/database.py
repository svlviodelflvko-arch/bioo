import sqlite3
import numpy as np

class DatabaseManager:
    def __init__(self, db_name="facelock_db.sqlite"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Stockage de l'embedding en format BLOB (respect de la minimisation des données)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                embedding BLOB NOT NULL
            )
        ''')
        self.conn.commit()

    def add_user(self, username, embedding_vector):
        # Convertir le vecteur numpy en bytes pour le stockage
        embedding_bytes = embedding_vector.tobytes()
        try:
            self.cursor.execute('INSERT INTO users (username, embedding) VALUES (?, ?)', 
                                (username, embedding_bytes))
            self.conn.commit()
            print(f"[+] Utilisateur {username} ajouté avec succès.")
        except sqlite3.IntegrityError:
            print(f"[-] L'utilisateur {username} existe déjà.")

    def get_all_users(self):
        self.cursor.execute('SELECT username, embedding FROM users')
        users = []
        for row in self.cursor.fetchall():
            username = row[0]
            # Reconvertir les bytes en vecteur numpy (float32 pour FaceNet)
            embedding = np.frombuffer(row[1], dtype=np.float32)
            users.append((username, embedding))
        return users

    def delete_user(self, username):
        self.cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        self.conn.commit()
        print(f"[+] Données biométriques de {username} supprimées (Droit à l'oubli).")