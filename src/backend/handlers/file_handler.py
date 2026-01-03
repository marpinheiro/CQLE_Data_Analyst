import pandas as pd
import os

class FileHandler:
    def read_file(self, file_path):
        """
        Lê arquivos locais (CSV, XLSX, XLS).
        Retorna: (DataFrame, Mensagem de Sucesso) ou (None, Mensagem de Erro)
        """
        ext = os.path.splitext(file_path)[1].lower()
        df = None
        
        try:
            # --- TENTATIVA 1: Extensão oficial ---
            if ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8-sig', sep=None, engine='python')
            elif ext == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            elif ext == '.xls':
                df = pd.read_excel(file_path, engine='xlrd')
            else:
                return None, f"Extensão '{ext}' não suportada."

        except Exception as e_primary:
            # --- TENTATIVA 2: Fallback para CSV ---
            print(f"Erro primário: {e_primary}. Tentando ler como texto...")
            try:
                df = pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8-sig')
            except Exception as e_secondary:
                return None, f"Erro ao ler arquivo: {str(e_primary)} | {str(e_secondary)}"

        return df, f"Arquivo carregado! ({df.shape[0]} linhas)"