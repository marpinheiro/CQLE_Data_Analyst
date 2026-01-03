# Importa as novas classes
from src.backend.handlers.file_handler import FileHandler
from src.backend.handlers.sql_handler import SQLHandler

class DataLoader:
    def __init__(self):
        self.df = None
        # Instancia os especialistas
        self.file_handler = FileHandler()
        self.sql_handler = SQLHandler()

    def load_file(self, file_path):
        """Delega para o FileHandler"""
        df, msg = self.file_handler.read_file(file_path)
        
        if df is not None:
            self.df = df
            return True, msg
        return False, msg

    def load_from_sql(self, query="SELECT * FROM users"):
        """Delega para o SQLHandler"""
        df, msg = self.sql_handler.execute_query(query)
        
        if df is not None:
            self.df = df
            return True, msg
        return False, msg

    def get_dataframe(self):
        """Retorna o dado atual (seja ele vindo de arquivo ou SQL)"""
        return self.df
    def get_sql_tables(self):
        """Retorna a lista de tabelas disponíveis"""
        return self.sql_handler.get_available_tables()