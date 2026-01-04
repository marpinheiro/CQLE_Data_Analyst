import pandas as pd
import os

class DataExporter:
    def export_data(self, df, file_path):
        """
        Direciona para Excel ou CSV dependendo da extensão escolhida.
        """
        if file_path.lower().endswith('.csv'):
            return self._to_csv(df, file_path)
        else:
            return self._to_excel(df, file_path)

    def _to_excel(self, df, file_path):
        try:
            if df is None or df.empty: return False, "Sem dados."
            if not file_path.endswith(".xlsx"): file_path += ".xlsx"

            # O Excel leva tempo para processar 30k linhas
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Dados")
                df.describe().to_excel(writer, sheet_name="Estatísticas")

            return True, f"Excel salvo com sucesso!\n{file_path}"
        except Exception as e:
            return False, f"Erro Excel: {str(e)}"

    def _to_csv(self, df, file_path):
        try:
            # CSV é instantâneo
            if not file_path.endswith(".csv"): file_path += ".csv"
            
            # sep=';' e decimal=',' é o padrão brasileiro (Excel abre direto)
            df.to_csv(file_path, index=False, sep=';', decimal=',', encoding='utf-8-sig')
            
            return True, f"CSV gerado instantaneamente!\n{file_path}"
        except Exception as e:
            return False, f"Erro CSV: {str(e)}"