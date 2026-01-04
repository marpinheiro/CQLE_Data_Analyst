import pandas as pd
import os

class CacheManager:
    def __init__(self):
        self.cache_dir = "cache_data"
        self._ensure_dir()
        self.cache_file = os.path.join(self.cache_dir, "last_session.parquet")

    def _ensure_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def save_cache(self, df):
        """Salva o DataFrame em disco de forma otimizada (Parquet)"""
        try:
            if df is not None:
                df.to_parquet(self.cache_file, index=False)
                return True, "Cache salvo automaticamente."
            return False, "Sem dados para salvar."
        except Exception as e:
            return False, f"Erro ao salvar cache: {str(e)}"

    def load_cache(self):
        """Lê o arquivo Parquet (Instantâneo)"""
        if not os.path.exists(self.cache_file):
            return None, "Nenhum cache encontrado. Conecte ao SQL primeiro."
        
        try:
            df = pd.read_parquet(self.cache_file)
            return df, f"Cache carregado! ({df.shape[0]} linhas)"
        except Exception as e:
            return None, f"Erro ao ler cache: {str(e)}"
            
    def has_cache(self):
        return os.path.exists(self.cache_file)