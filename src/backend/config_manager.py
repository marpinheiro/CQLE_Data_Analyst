import json
import os
import pyodbc

class ConfigManager:
    def __init__(self):
        self.config_dir = "config"
        self.config_file = os.path.join(self.config_dir, "database.json")
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def test_connection(self, server, database, user, password):
        """
        Tenta conectar ao SQL Server.
        Retorna (True, 'Ok') ou (False, 'Erro detalhado').
        """
        # String de conexão padrão para SQL Server
        # Nota: '{SQL Server}' é o driver padrão antigo do Windows. 
        # Se tiver o 'ODBC Driver 17 for SQL Server' instalado, é melhor, mas este é mais compatível.
        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password}"
        )

        try:
            # Tenta conectar com timeout de 5 segundos para não travar a tela
            conn = pyodbc.connect(conn_str, timeout=5)
            conn.close()
            return True, "Conexão realizada com sucesso!"
        except Exception as e:
            # Retorna o erro limpo (sem o código técnico completo se possível)
            return False, f"Falha na conexão: {str(e)}"

    def save_db_config(self, server, database, user, password):
        """Salva as credenciais no arquivo JSON"""
        data = {
            "server": server,
            "database": database,
            "user": user,
            "password": password
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(data, f, indent=4)
            return True, "Configuração salva com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar arquivo: {str(e)}"

    def load_db_config(self):
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except:
            return {}