from src.backend.handlers.file_handler import FileHandler
from src.backend.handlers.sql_handler import SQLHandler
from src.backend.cache_manager import CacheManager # <--- Importar

class DataLoader:
    def __init__(self):
        self.df = None
        self.file_handler = FileHandler()
        self.sql_handler = SQLHandler()
        self.cache_manager = CacheManager() # <--- Instanciar

    def load_file(self, file_path):
        df, msg = self.file_handler.read_file(file_path)
        if df is not None:
            self.df = df
            # Salva cache silenciosamente
            self.cache_manager.save_cache(df) 
            return True, msg
        return False, msg

    def load_from_sql(self, query="SELECT * FROM users"):
        df, msg = self.sql_handler.execute_query(query)
        if df is not None:
            self.df = df
            # Salva cache silenciosamente
            self.cache_manager.save_cache(df)
            return True, msg
        return False, msg

    def load_from_cache(self):
        """Método novo para carregar direto do cache"""
        df, msg = self.cache_manager.load_cache()
        if df is not None:
            self.df = df
            return True, msg
        return False, msg

    def get_dataframe(self):
        return self.df
    
    def get_sql_tables(self):
        return self.sql_handler.get_available_tables()