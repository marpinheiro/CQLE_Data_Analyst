import pandas as pd
import numpy as np

class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def get_general_info(self):
        """Retorna informações macro sobre o dataset"""
        info = {
            "rows": self.df.shape[0],
            "cols": self.df.shape[1],
            "duplicates": self.df.duplicated().sum(),
            "memory": f"{self.df.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }
        return info

    def get_columns_analysis(self):
        """Analisa cada coluna individualmente"""
        analysis = []
        
        for col in self.df.columns:
            col_data = {
                "name": col,
                "type": str(self.df[col].dtype),
                "nulls": self.df[col].isnull().sum(),
                "unique": self.df[col].nunique()
            }
            
            # Se for numérico, calcula estatísticas extras
            if pd.api.types.is_numeric_dtype(self.df[col]):
                col_data["category"] = "Numérico"
                col_data["min"] = float(self.df[col].min())
                col_data["max"] = float(self.df[col].max())
                col_data["mean"] = float(self.df[col].mean())
            else:
                col_data["category"] = "Texto/Categórico"
                col_data["mode"] = str(self.df[col].mode()[0]) if not self.df[col].mode().empty else "-"
            
            analysis.append(col_data)
            
        return analysis

    def generate_text_report(self):
        """Gera um texto formatado pronto para exibir na tela"""
        if self.df is None or self.df.empty:
            return "Nenhum dado carregado."

        general = self.get_general_info()
        cols = self.get_columns_analysis()

        report = "=== RESUMO GERAL ===\n"
        report += f"📊 Total de Linhas: {general['rows']}\n"
        report += f"📊 Total de Colunas: {general['cols']}\n"
        report += f"⚠️ Linhas Duplicadas: {general['duplicates']}\n"
        report += f"💾 Uso de Memória: {general['memory']}\n\n"
        
        report += "=== ANÁLISE DETALHADA POR COLUNA ===\n"
        
        for c in cols:
            report += f"\n🔹 Coluna: {c['name'].upper()}\n"
            report += f"   Tipo: {c['category']} ({c['type']})\n"
            report += f"   Nulos (Vazios): {c['nulls']} ({(c['nulls']/general['rows'])*100:.1f}%)\n"
            report += f"   Valores Únicos: {c['unique']}\n"
            
            if c['category'] == "Numérico":
                report += f"   📈 Mín: {c['min']:.2f} | Máx: {c['max']:.2f} | Média: {c['mean']:.2f}\n"
            else:
                report += f"   🔤 Valor mais comum: {c['mode']}\n"
            
            report += "-" * 40 + "\n"

        return report