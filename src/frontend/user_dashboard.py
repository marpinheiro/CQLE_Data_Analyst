import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import numpy as np

from src.backend.data_loader import DataLoader
from src.backend.analyzer import DataAnalyzer

class UserDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CQLE Data Analyst - Painel Interativo")
        self.geometry("1200x800")
        
        if os.path.exists("CQLE.ico"):
            self.iconbitmap("CQLE.ico")

        # Classes de lógica
        self.loader = DataLoader()
        self.analyzer = None 
        self.current_df = None

        # Layout
        self.create_layout()

    def create_layout(self):
        # --- MENU LATERAL ESQUERDO (GLOBAL) ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="FONTE DE DADOS", font=("Arial", 14, "bold")).pack(pady=(30, 10))

        self.btn_csv = ctk.CTkButton(self.sidebar, text="Abrir Arquivo", command=self.upload_local_file)
        self.btn_csv.pack(pady=10, padx=20)

        self.btn_sql = ctk.CTkButton(self.sidebar, text="Conectar SQL", fg_color="darkblue", command=self.connect_sql)
        self.btn_sql.pack(pady=10, padx=20)
        
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Sair", fg_color="transparent", border_width=1, command=self.logout)
        self.btn_logout.pack(side="bottom", pady=20, padx=20)

        # --- ÁREA PRINCIPAL COM ABAS ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.tab_resumo = self.tabview.add(" 📋 Resumo ")
        self.tab_dados = self.tabview.add(" 💾 Dados ")
        self.tab_graficos = self.tabview.add(" 📊 Estúdio Gráfico ") # Nome novo!

        # --- CONTEÚDO: RESUMO ---
        self.txt_report = ctk.CTkTextbox(self.tab_resumo, font=("Consolas", 14))
        self.txt_report.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_report.insert("0.0", "Carregue um arquivo para começar...")

        # --- CONTEÚDO: DADOS ---
        self.txt_preview = ctk.CTkTextbox(self.tab_dados, wrap="none")
        self.txt_preview.pack(fill="both", expand=True, padx=10, pady=10)

        # --- CONTEÚDO: ESTÚDIO GRÁFICO (NOVO LAYOUT) ---
        # Dividir a aba em: Controle (Esquerda) e Visualização (Direita)
        
        self.graph_frame = ctk.CTkFrame(self.tab_graficos)
        self.graph_frame.pack(fill="both", expand=True)

        # 1. Coluna de Controles
        self.controls_frame = ctk.CTkFrame(self.graph_frame, width=250)
        self.controls_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.controls_frame, text="Configuração do Gráfico", font=("Arial", 16, "bold")).pack(pady=10)

        ctk.CTkLabel(self.controls_frame, text="1. Escolha a Coluna X:").pack(anchor="w", padx=10)
        self.combo_columns = ctk.CTkOptionMenu(self.controls_frame, values=["(Vazio)"], command=self.on_column_change)
        self.combo_columns.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(self.controls_frame, text="2. Tipo de Gráfico:").pack(anchor="w", padx=10)
        self.combo_chart_type = ctk.CTkOptionMenu(self.controls_frame, 
                                                  values=["Histograma", "Boxplot", "Barras", "Pizza", "Linha"],
                                                  command=self.update_chart)
        self.combo_chart_type.pack(fill="x", padx=10, pady=(0, 20))

        # Filtro Opcional (apenas visual por enquanto)
        ctk.CTkLabel(self.controls_frame, text="3. Filtros (Top N):").pack(anchor="w", padx=10)
        self.slider_top_n = ctk.CTkSlider(self.controls_frame, from_=5, to=50, number_of_steps=9, command=self.update_chart_slider)
        self.slider_top_n.set(10)
        self.slider_top_n.pack(fill="x", padx=10, pady=(0, 5))
        self.lbl_slider = ctk.CTkLabel(self.controls_frame, text="Top 10 itens")
        self.lbl_slider.pack()

        # Botão forçar atualização
        ctk.CTkButton(self.controls_frame, text="Atualizar Visualização", fg_color="green", command=self.update_chart).pack(pady=30, padx=10)


        # 2. Área do Gráfico (Canvas)
        self.canvas_frame = ctk.CTkFrame(self.graph_frame)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Placeholder
        self.lbl_placeholder = ctk.CTkLabel(self.canvas_frame, text="Selecione uma coluna para gerar o gráfico.")
        self.lbl_placeholder.pack(expand=True)

    # --- LÓGICA DO DASHBOARD ---

    def update_interface(self):
        """Atualiza dados globais após carregar arquivo"""
        df = self.loader.get_dataframe()
        if df is None: return
        
        self.current_df = df

        # 1. Análise Textual
        self.analyzer = DataAnalyzer(df)
        report = self.analyzer.generate_text_report()
        self.txt_report.delete("0.0", "end")
        self.txt_report.insert("0.0", report)

        # 2. Preview
        preview = df.head(50).to_string()
        self.txt_preview.delete("0.0", "end")
        self.txt_preview.insert("0.0", preview)

        # 3. Atualizar Lista de Colunas no Estúdio Gráfico
        cols = list(df.columns)
        self.combo_columns.configure(values=cols)
        self.combo_columns.set(cols[0]) # Seleciona a primeira por padrão
        
        # Gera o primeiro gráfico automaticamente
        self.on_column_change(cols[0])

        messagebox.showinfo("Sucesso", "Dados carregados! Vá para a aba 'Estúdio Gráfico' para explorar.")

    # --- LÓGICA DO ESTÚDIO GRÁFICO ---

    def on_column_change(self, choice):
        """Chamado quando o usuário troca a coluna no dropdown"""
        # Tenta adivinhar o melhor gráfico
        if self.current_df is None: return

        dtype = self.current_df[choice].dtype
        
        # Lógica inteligente de sugestão
        if pd.api.types.is_numeric_dtype(dtype):
            if "ano" in choice.lower() or "data" in choice.lower():
                self.combo_chart_type.set("Linha")
            else:
                self.combo_chart_type.set("Histograma")
        else:
            if self.current_df[choice].nunique() < 5:
                self.combo_chart_type.set("Pizza")
            else:
                self.combo_chart_type.set("Barras")
        
        self.update_chart()

    def update_chart_slider(self, value):
        self.lbl_slider.configure(text=f"Top {int(value)} itens")
        # Não atualiza o gráfico em tempo real para não pesar, espera soltar ou clicar
        # (Mas podemos chamar update_chart se for leve)
    
    def update_chart(self, _=None):
        """Desenha o gráfico baseado nas configurações atuais"""
        if self.current_df is None: return

        # Limpa área antiga
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        col_name = self.combo_columns.get()
        chart_type = self.combo_chart_type.get()
        top_n = int(self.slider_top_n.get())

        # Prepara Figura
        fig = plt.Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Tema Dark
        plt.style.use('bmh')
        bg_color = "#2b2b2b"
        text_color = "white"
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)

        try:
            # Lógica de Plotagem
            series = self.current_df[col_name].dropna()
            
            if chart_type == "Histograma":
                if not pd.api.types.is_numeric_dtype(series):
                    raise ValueError("Histograma requer dados numéricos.")
                ax.hist(series, bins=30, color='#1f6aa5', edgecolor='white')
                ax.set_title(f"Distribuição de {col_name}")

            elif chart_type == "Boxplot":
                if not pd.api.types.is_numeric_dtype(series):
                    raise ValueError("Boxplot requer dados numéricos.")
                ax.boxplot(series, vert=False, patch_artist=True, 
                           boxprops=dict(facecolor='#1f6aa5', color='white'),
                           medianprops=dict(color='yellow'),
                           tick_labels=[col_name])
                ax.set_title(f"Outliers em {col_name}")

            elif chart_type == "Barras":
                # Contagem de valores
                counts = series.value_counts().nlargest(top_n)
                # Inverte para o maior ficar em cima no barh, ou usa bar normal
                counts.sort_values().plot(kind='barh', ax=ax, color='#1fa565')
                ax.set_title(f"Top {top_n} - {col_name}")
                ax.set_xlabel("Contagem")

            elif chart_type == "Pizza":
                counts = series.value_counts().nlargest(top_n)
                ax.pie(counts, labels=counts.index, autopct='%1.1f%%', 
                       textprops={'color':"white"})
                ax.set_title(f"Proporção - {col_name}")

            elif chart_type == "Linha":
                # Ideal para séries temporais. Se for numérico simples, plota index vs valor
                if pd.api.types.is_numeric_dtype(series):
                    ax.plot(series.values, color='#ffa500')
                else:
                    # Se for texto, conta ocorrências? Não, linha não faz sentido.
                    # Vamos tentar plotar contagem por ordem
                    counts = series.value_counts().sort_index()
                    ax.plot(counts.index.astype(str), counts.values, color='#ffa500')
                ax.set_title(f"Tendência - {col_name}")

            # Renderiza no Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Barra de Ferramentas (Zoom, Salvar, Pan) - Opcional mas profissional
            toolbar = NavigationToolbar2Tk(canvas, self.canvas_frame, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(side="bottom", fill="x")

        except Exception as e:
            err_label = ctk.CTkLabel(self.canvas_frame, text=f"Não foi possível gerar este gráfico:\n{str(e)}", 
                                     text_color="red", font=("Arial", 14))
            err_label.pack(expand=True)

    # --- FUNÇÕES DE CARREGAMENTO (Mantidas) ---

    def upload_local_file(self):
        path = filedialog.askopenfilename(filetypes=[("Dados", "*.csv;*.xlsx;*.xls")])
        if path:
            success, msg = self.loader.load_file(path)
            if success:
                self.update_interface()
            else:
                messagebox.showerror("Erro", msg)

    def connect_sql(self):
        query = simpledialog.askstring("SQL", "Digite a Query (ex: SELECT * FROM Tabela):")
        if query:
            success, msg = self.loader.load_from_sql(query)
            if success:
                self.update_interface()
            else:
                messagebox.showerror("Erro", msg)

    def logout(self):
        self.destroy()
        from src.frontend.login import LoginScreen
        app = LoginScreen()
        app.mainloop()