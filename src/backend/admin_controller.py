import sqlite3
import hashlib
from datetime import datetime

class AdminController:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name

    def _encrypt(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_all_users(self):
        """Busca todos usuários exceto os excluídos (Status 6) para listar na tela"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # Trazemos status 6 também para histórico, ou filtramos. Vamos trazer tudo exceto o próprio admin logado se quiser.
        cursor.execute("SELECT id, username, full_name, role, status, created_at, updated_at FROM users WHERE status != 6")
        data = cursor.fetchall()
        conn.close()
        return data

    def create_user(self, username, full_name, role):
        """
        Cria usuário.
        Senha padrão: Mud@r123
        Status: 1 (Inserido agora)
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            default_pass = self._encrypt("Mud@r123")
            now = self._get_time()
            # Status 1: Inserido agora
            cursor.execute("""
                INSERT INTO users (username, full_name, password, role, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (username, full_name, default_pass, role, now, now))
            conn.commit()
            return True, "Usuário criado com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Nome de usuário já existe."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def edit_user(self, user_id, full_name, role):
        """
        Edita dados cadastrais.
        Status: 5 (Alterado)
        Mantém created_at, altera updated_at
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        now = self._get_time()
        
        try:
            # Status 5: Alterado dados
            cursor.execute("""
                UPDATE users 
                SET full_name = ?, role = ?, status = 5, updated_at = ?
                WHERE id = ?
            """, (full_name, role, now, user_id))
            conn.commit()
            return True, "Dados atualizados."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def reset_password(self, user_id):
        """
        Reseta senha para Mud@r123.
        Status: 3 (Resetado/Forçar troca)
        Altera updated_at
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        now = self._get_time()
        default_pass = self._encrypt("Mud@r123")

        try:
            cursor.execute("""
                UPDATE users 
                SET password = ?, status = 3, updated_at = ?
                WHERE id = ?
            """, (default_pass, now, user_id))
            conn.commit()
            return True, "Senha resetada para 'Mud@r123'."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_user(self, user_id):
        """
        Exclusão Lógica.
        Status: 6 (Excluído)
        Altera updated_at
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        now = self._get_time()

        try:
            cursor.execute("""
                UPDATE users 
                SET status = 6, updated_at = ?
                WHERE id = ?
            """, (now, user_id))
            conn.commit()
            return True, "Usuário excluído."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()