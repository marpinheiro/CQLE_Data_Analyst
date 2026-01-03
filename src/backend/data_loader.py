import pandas as pd
import os
import pyodbc
from src.backend.config_manager import ConfigManager

class DataLoader:
    def __init__(self):
        self.df = None
        self.config = ConfigManager()

    def load_file(self, file_path):
        """
        Carrega arquivos com estratégia de Fallback (Plano B).
        Se falhar como Excel, tenta como CSV automaticamente.
        """
        # Pega a extensão
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # --- TENTATIVA 1: Confiar na extensão do arquivo ---
            if ext == '.csv':
                # sep=None faz o pandas tentar descobrir se é virgula ou ponto-e-virgula
                self.df = pd.read_csv(file_path, encoding='utf-8-sig', sep=None, engine='python')
            
            elif ext == '.xlsx':
                self.df = pd.read_excel(file_path, engine='openpyxl')
            
            elif ext == '.xls':
                self.df = pd.read_excel(file_path, engine='xlrd')
            
            else:
                return False, f"Extensão '{ext}' não é suportada oficialmente."

        except Exception as e_primary:
            # --- TENTATIVA 2 (PLANO B): O arquivo pode ser um CSV "disfarçado" ---
            # O erro da sua imagem mostra que ele tentou ler XLS mas achou texto (b'id,batte')
            print(f"Tentativa primária falhou: {e_primary}. Tentando modo compatibilidade...")
            
            try:
                # Tenta ler como CSV ignorando a extensão original
                self.df = pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8-sig')
            
            except Exception as e_secondary:
                # Se falhar nos dois métodos, aí sim devolvemos o erro real
                return False, f"Falha crítica ao ler arquivo.\n\nErro Original: {str(e_primary)}\n\nErro Tentativa CSV: {str(e_secondary)}"

        # Sucesso
        return True, f"Arquivo carregado! ({self.df.shape[0]} linhas, {self.df.shape[1]} colunas)"

    def load_from_sql(self, query="SELECT * FROM users"):
        """Lê do SQL Server"""
        conf = self.config.load_db_config()
        if not conf:
            return False, "Configuração de banco não encontrada. Fale com o Admin."

        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={conf['server']};"
            f"DATABASE={conf['database']};"
            f"UID={conf['user']};"
            f"PWD={conf['password']}"
        )

        try:
            conn = pyodbc.connect(conn_str)
            self.df = pd.read_sql(query, conn)
            conn.close()
            return True, f"Dados carregados do SQL! Linhas: {self.df.shape[0]}"
        except Exception as e:
            return False, f"Erro SQL: {str(e)}"

    def get_dataframe(self):
        return self.df