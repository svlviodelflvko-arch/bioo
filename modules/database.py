import sqlite3
import numpy as np

class DatabaseManager:
    def __init__(self, db_name="facelock_db.sqlite"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.migrate_db() # Met à jour les anciennes bases de données

    def create_tables(self):
        # Table des utilisateurs
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                embedding BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # NOUVELLE: Table de l'historique de connexion (Logs)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def migrate_db(self):
        # Ajoute la colonne created_at si elle n'existait pas avant
        try:
            self.cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass # La colonne existe déjà

    def add_user(self, username, embedding_vector):
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
            embedding = np.frombuffer(row[1], dtype=np.float32)
            users.append((username, embedding))
        return users

    def delete_user(self, username):
        self.cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        # RGPD : On supprime aussi l'historique lié à cet utilisateur
        self.cursor.execute('DELETE FROM access_logs WHERE username = ?', (username,))
        self.conn.commit()
        print(f"[+] Données de {username} supprimées (Droit à l'oubli).")

    # ==========================================
    # NOUVELLES MÉTHODES POUR LE DASHBOARD ADMIN
    # ==========================================

    def log_access(self, username, status):
        """Enregistre une tentative de connexion (Succès ou Échec)"""
        self.cursor.execute('INSERT INTO access_logs (username, status) VALUES (?, ?)', (username, status))
        self.conn.commit()

    def get_admin_users_list(self):
        """Récupère la liste des utilisateurs sans télécharger les vecteurs biométriques"""
        self.cursor.execute('SELECT id, username, created_at FROM users')
        return self.cursor.fetchall()

    def get_access_logs(self):
        """Récupère les 100 derniers événements de connexion"""
        self.cursor.execute('SELECT id, username, status, timestamp FROM access_logs ORDER BY timestamp DESC LIMIT 100')
        return self.cursor.fetchall()