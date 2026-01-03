import sqlite3
import hashlib
from datetime import datetime

class AuthManager:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.init_db()

    def _encrypt_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Recriando tabela se necessário para garantir novas colunas
        # OBS: Em produção, usaríamos scripts de migração. Aqui, validamos se existe.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                status INTEGER NOT NULL,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Cria Admin Padrão se não existir
        cursor.execute("SELECT count(*) FROM users")
        if cursor.fetchone()[0] == 0:
            now = self.get_timestamp()
            admin_pass = self._encrypt_password("admin123")
            # Status 2 = Ativo (pois é o admin inicial)
            cursor.execute("""
                INSERT INTO users (username, full_name, password, role, status, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("admin", "Administrador Sistema", admin_pass, "admin", 2, now, now))
            print("--- ADMIN PADRÃO CRIADO ---")
            
        conn.commit()
        conn.close()

    def login(self, username, password):
        """Verifica login. Retorna (role, status) se sucesso, ou None."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        encrypted_pass = self._encrypt_password(password)
        
        # Bloqueia login se status for 6 (Excluído)
        cursor.execute("""
            SELECT role, status FROM users 
            WHERE username = ? AND password = ? AND status != 6
        """, (username, encrypted_pass))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result # Retorna tupla (role, status)
        return None
    def force_password_change(self, username, new_password):
        """
        Altera a senha e define o status para 2 (Ativo).
        Usado quando o usuário é obrigado a trocar a senha (Status 1 ou 3).
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        encrypted_pass = self._encrypt_password(new_password)
        now = self.get_timestamp()
        
        try:
            # Status 2 = Ativo Normal
            # Mantém data de criação, atualiza data de alteração (updated_at)
            cursor.execute("""
                UPDATE users 
                SET password = ?, status = 2, updated_at = ?
                WHERE username = ?
            """, (encrypted_pass, now, username))
            
            conn.commit()
            return True, "Senha alterada com sucesso!"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()