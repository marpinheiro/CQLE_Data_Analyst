import pandas as pd
import pyodbc
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from src.backend.config_manager import ConfigManager

class SQLHandler:
    def __init__(self):
        self.config_manager = ConfigManager()

    def _get_best_driver(self):
        """Detecta o driver ODBC instalado"""
        drivers = pyodbc.drivers()
        preference = [
            "ODBC Driver 18 for SQL Server", 
            "ODBC Driver 17 for SQL Server", 
            "ODBC Driver 13 for SQL Server",
            "SQL Server Native Client 11.0", 
            "SQL Server"
        ]
        for d in preference:
            if d in drivers: return d
        return "SQL Server"

    def get_connection_config(self):
        """Retorna configuração bruta e o driver"""
        conf = self.config_manager.load_db_config()
        if not conf: return None, None
        return conf, self._get_best_driver()

    def get_available_tables(self):
        """
        Retorna lista de tabelas. 
        Usa pyodbc puro aqui pois é metadado leve e específico.
        """
        conf, driver = self.get_connection_config()
        if not conf: return None, "Configure o banco no menu Admin."

        # String de conexão bruta para metadados
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={conf['server']};"
            f"DATABASE={conf['database']};"
            f"UID={conf['user']};"
            f"PWD={conf['password']};"
            "TrustServerCertificate=yes;"
        )

        query_meta = """
        SELECT TABLE_SCHEMA + '.' + TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE IN ('BASE TABLE', 'VIEW')
        ORDER BY TABLE_NAME
        """

        try:
            # Aqui usamos pyodbc direto pois não é DataFrame do pandas
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute(query_meta)
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables, "Sucesso"
        except Exception as e:
            return None, f"Erro ao listar: {str(e)}"

    def execute_query(self, query):
        """
        Executa query usando SQLAlchemy para evitar o erro do Pandas.
        """
        conf, driver = self.get_connection_config()
        if not conf: return None, "Sem configuração."

        try:
            # 1. Monta a string de conexão segura para o SQLAlchemy
            # Usamos quote_plus para permitir senhas com caracteres especiais
            params = quote_plus(
                f"DRIVER={{{driver}}};"
                f"SERVER={conf['server']};"
                f"DATABASE={conf['database']};"
                f"UID={conf['user']};"
                f"PWD={conf['password']};"
                "TrustServerCertificate=yes;"
            )
            
            # URL de conexão padrão SQLAlchemy para MSSQL+PyODBC
            connection_url = f"mssql+pyodbc:///?odbc_connect={params}"
            
            # 2. Cria a Engine
            engine = create_engine(connection_url)
            
            # 3. Conecta e lê (Usando 'with' para garantir fechamento)
            with engine.connect() as connection:
                # pandas requer query em formato text() do sqlalchemy
                df = pd.read_sql(text(query), connection)
                
            return df, f"Dados SQL carregados! ({df.shape[0]} linhas)"

        except Exception as e:
            return None, f"Erro SQL: {str(e)}"