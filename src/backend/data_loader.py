import pandas as pd
import os

class DataLoader:
    def __init__(self):
        self.df = None

    def load_file(self, file_path):
        """Carrega CSV ou Excel e retorna status e mensagem"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                self.df = pd.read_csv(file_path)
            elif ext in ['.xls', '.xlsx']:
                self.df = pd.read_excel(file_path)
            else:
                return False, "Formato não suportado."

            return True, f"Arquivo carregado! Linhas: {self.df.shape[0]}, Colunas: {self.df.shape[1]}"
        except Exception as e:
            return False, f"Erro ao ler arquivo: {str(e)}"

    def get_summary(self):
        """Retorna um resumo básico para teste"""
        if self.df is not None:
            return self.df.describe().to_string()
        return "Nenhum dado carregado."