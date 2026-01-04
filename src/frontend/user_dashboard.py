import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import numpy as np
import threading

# Importações do Backend
from src.backend.data_loader import DataLoader
from src.backend.analyzer import DataAnalyzer
from src.backend.exporter import DataExporter

class UserDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CQLE Data Analyst - Painel Profissional")
        self.geometry("1200x800")
        
        if os.path.exists("CQLE.ico"):
            self.iconbitmap("CQLE.ico")

        # --- INICIALIZAÇÃO DO BACKEND ---
        self.loader = DataLoader()
        self.analyzer = None 
        self.exporter = DataExporter()
        self.current_df = None

        # Configura estilo da Tabela (Grid)
        self.setup_table_style()

        # Criação da Interface
        self.create_layout()

    def setup_table_style(self):
        """Configura as cores da tabela (Treeview) para o modo Dark"""
        style = ttk.Style()
        style.theme_use("default")

        bg_color = "#2b2b2b"
        text_color = "white"
        header_bg = "#1f6aa5"
        selected_bg = "#1fa565"

        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=text_color, 
                        fieldbackground=bg_color,
                        rowheight=25,
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        background=header_bg, 
                        foreground="white", 
                        relief="flat",
                        font=("Arial", 10, "bold"))
        
        style.map("Treeview", background=[('selected', selected_bg)])
        style.map("Treeview.Heading", background=[('active', header_bg)])

    def create_layout(self):
        # --- MENU LATERAL (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Botão de Cache (Destaque)
        self.btn_cache = ctk.CTkButton(self.sidebar, text="⚡ Carregar Última Sessão", 
                                       fg_color="#D35B58", hover_color="#C72C41",
                                       command=self.load_cache_data)
        self.btn_cache.pack(pady=(30, 10), padx=20)

        ctk.CTkLabel(self.sidebar, text="FONTE DE DADOS", font=("Arial", 14, "bold")).pack(pady=(10, 10))

        self.btn_csv = ctk.CTkButton(self.sidebar, text="Abrir Arquivo Local", command=self.upload_local_file)
        self.btn_csv.pack(pady=5, padx=20)

        self.btn_sql = ctk.CTkButton(self.sidebar, text="Conectar SQL Server", fg_color="darkblue", command=self.connect_sql)
        self.btn_sql.pack(pady=5, padx=20)
        
        ctk.CTkLabel(self.sidebar, text="AÇÕES", font=("Arial", 14, "bold")).pack(pady=(20, 10))

        self.btn_export = ctk.CTkButton(self.sidebar, text="Exportar Dados", fg_color="green", command=self.export_data)
        self.btn_export.pack(pady=5, padx=20)

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Sair / Logout", fg_color="transparent", border_width=1, command=self.logout)
        self.btn_logout.pack(side="bottom", pady=20, padx=20)

        # --- ÁREA PRINCIPAL (ABAS) ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.tab_resumo = self.tabview.add(" 📋 Resumo ")
        self.tab_dados = self.tabview.add(" 💾 Grid de Dados ")
        self.tab_graficos = self.tabview.add(" 📊 Estúdio Gráfico ")

        # --- ABA 1: RESUMO ---
        self.txt_report = ctk.CTkTextbox(self.tab_resumo, font=("Consolas", 14))
        self.txt_report.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_report.insert("0.0", "Carregue um arquivo ou conecte ao SQL para começar...")

        # --- ABA 2: GRID (TABELA) ---
        self.table_frame = ctk.CTkFrame(self.tab_dados)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.scroll_y = ttk.Scrollbar(self.table_frame, orient="vertical")
        self.scroll_x = ttk.Scrollbar(self.table_frame, orient="horizontal")

        self.tree = ttk.Treeview(self.table_frame, yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        
        self.scroll_y.config(command=self.tree.yview)
        self.scroll_x.config(command=self.tree.xview)

        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # --- ABA 3: GRÁFICOS ---
        self.graph_frame = ctk.CTkFrame(self.tab_graficos)
        self.graph_frame.pack(fill="both", expand=True)

        # Painel de Controle (Esquerda)
        self.controls_frame = ctk.CTkFrame(self.graph_frame, width=250)
        self.controls_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.controls_frame, text="Configuração", font=("Arial", 16, "bold")).pack(pady=10)
        
        ctk.CTkLabel(self.controls_frame, text="Eixo X (Coluna):").pack(anchor="w", padx=10)
        self.combo_columns = ctk.CTkOptionMenu(self.controls_frame, values=[""], command=self.on_column_change)
        self.combo_columns.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(self.controls_frame, text="Tipo de Gráfico:").pack(anchor="w", padx=10)
        self.combo_chart_type = ctk.CTkOptionMenu(self.controls_frame, values=["Histograma", "Boxplot", "Barras", "Pizza", "Linha"], command=self.update_chart)
        self.combo_chart_type.pack(fill="x", padx=10, pady=(0, 20))

        ctk.CTkLabel(self.controls_frame, text="Filtros (Top N):").pack(anchor="w", padx=10)
        self.slider_top_n = ctk.CTkSlider(self.controls_frame, from_=5, to=50, number_of_steps=9, command=self.update_chart_slider)
        self.slider_top_n.set(10)
        self.slider_top_n.pack(fill="x", padx=10, pady=(0, 5))
        self.lbl_slider = ctk.CTkLabel(self.controls_frame, text="Top 10")
        self.lbl_slider.pack()

        ctk.CTkButton(self.controls_frame, text="Atualizar Gráfico", fg_color="green", command=self.update_chart).pack(pady=30, padx=10)

        # Área do Canvas (Direita)
        self.canvas_frame = ctk.CTkFrame(self.graph_frame)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.lbl_placeholder = ctk.CTkLabel(self.canvas_frame, text="Selecione uma coluna para visualizar.")
        self.lbl_placeholder.pack(expand=True)

    # =========================================================================
    # LÓGICA CENTRAL (CORE)
    # =========================================================================

    def update_interface(self):
        """Atualiza todas as abas com os dados carregados"""
        df = self.loader.get_dataframe()
        if df is None: return
        self.current_df = df

        # 1. Resumo Textual
        self.analyzer = DataAnalyzer(df)
        report = self.analyzer.generate_text_report()
        self.txt_report.delete("0.0", "end")
        self.txt_report.insert("0.0", report)

        # 2. Grid de Dados
        self.update_table_view(df)

        # 3. Controles Gráficos
        cols = list(df.columns)
        self.combo_columns.configure(values=cols)
        self.combo_columns.set(cols[0]) 
        self.on_column_change(cols[0])

    def update_table_view(self, df):
        """Preenche o Treeview (limitado a 5000 linhas para performance visual)"""
        # Limpa
        self.tree.delete(*self.tree.get_children())
        
        # Colunas
        cols = list(df.columns)
        self.tree["columns"] = cols
        self.tree["show"] = "headings"
        
        for col in cols:
            self.tree.heading(col, text=col)
            width = max(100, len(str(col)) * 10)
            self.tree.column(col, width=width, minwidth=50, anchor="w")

        # Dados
        rows_to_show = df.head(5000).to_numpy().tolist()
        for row in rows_to_show:
            clean_row = [str(x) if str(x) != 'nan' else "" for x in row]
            self.tree.insert("", "end", values=clean_row)

    # =========================================================================
    # CACHE / CARGA RÁPIDA
    # =========================================================================
    def load_cache_data(self):
        success, msg = self.loader.load_from_cache()
        if success:
            self.update_interface()
            messagebox.showinfo("Cache", "Sessão anterior restaurada com sucesso!")
        else:
            messagebox.showwarning("Aviso", msg)

    # =========================================================================
    # CONEXÃO SQL (COM THREADING)
    # =========================================================================
    def connect_sql(self):
        self.configure(cursor="watch")
        self.update()
        
        tables, msg = self.loader.get_sql_tables()
        self.configure(cursor="")

        if tables is None:
            messagebox.showerror("Erro SQL", msg)
            return
        if len(tables) == 0:
            messagebox.showwarning("Aviso", "Nenhuma tabela encontrada.")
            return
            
        self.open_table_selector(tables)

    def open_table_selector(self, tables):
        selector = ctk.CTkToplevel(self)
        selector.title("Selecionar Tabela")
        selector.geometry("400x500")
        selector.grab_set()
        
        ctk.CTkLabel(selector, text="Tabelas Disponíveis", font=("Arial", 16, "bold")).pack(pady=15)
        scroll = ctk.CTkScrollableFrame(selector, width=350, height=350)
        scroll.pack(pady=10, padx=10, fill="both", expand=True)

        def start_loading_thread(table_name):
            selector.destroy()
            
            # Janela de Loading
            self.loading_window = ctk.CTkToplevel(self)
            self.loading_window.title("Baixando dados...")
            self.loading_window.geometry("300x150")
            self.loading_window.grab_set()
            
            # Centraliza
            self.loading_window.geometry(f"+{self.winfo_x()+400}+{self.winfo_y()+200}")
            
            ctk.CTkLabel(self.loading_window, text=f"Lendo tabela: {table_name}...", font=("Arial", 14)).pack(pady=20)
            progress = ctk.CTkProgressBar(self.loading_window, width=200)
            progress.pack(pady=10)
            progress.configure(mode="indeterminate")
            progress.start()
            
            # Thread
            thread = threading.Thread(target=run_heavy_query, args=(table_name,))
            thread.start()

        def run_heavy_query(table_name):
            query = f"SELECT * FROM {table_name}"
            success, msg = self.loader.load_from_sql(query)
            self.after(0, lambda: finish_loading(success, msg))

        def finish_loading(success, msg):
            if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
                self.loading_window.destroy()
            
            if success:
                self.update_interface()
                messagebox.showinfo("Sucesso", "Dados carregados e Cache atualizado!")
            else:
                messagebox.showerror("Erro", msg)

        for tb in tables:
            ctk.CTkButton(scroll, text=tb, fg_color="transparent", border_width=1, 
                          text_color=("black", "white"), anchor="w",
                          command=lambda t=tb: start_loading_thread(t)).pack(fill="x", pady=2, padx=5)

    # =========================================================================
    # ARQUIVOS LOCAIS
    # =========================================================================
    def upload_local_file(self):
        path = filedialog.askopenfilename(filetypes=[("Dados", "*.csv;*.xlsx;*.xls")])
        if path:
            success, msg = self.loader.load_file(path)
            if success: self.update_interface()
            else: messagebox.showerror("Erro", msg)

    # =========================================================================
    # EXPORTAÇÃO (COM THREADING)
    # =========================================================================
    def export_data(self):
        if self.current_df is None:
            messagebox.showwarning("Aviso", "Sem dados para exportar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel (.xlsx)", "*.xlsx"), ("CSV (.csv)", "*.csv")],
            title="Exportar Dados"
        )
        if not file_path: return

        # Janela Loading
        self.loading_window = ctk.CTkToplevel(self)
        self.loading_window.title("Exportando...")
        self.loading_window.geometry("300x150")
        self.loading_window.grab_set()
        
        msg_text = "Gerando Excel..." if ".xlsx" in file_path else "Gerando CSV..."
        ctk.CTkLabel(self.loading_window, text=msg_text, font=("Arial", 14)).pack(pady=20)
        progress = ctk.CTkProgressBar(self.loading_window, width=200)
        progress.pack(pady=10)
        progress.configure(mode="indeterminate")
        progress.start()

        thread = threading.Thread(target=self.run_export_thread, args=(file_path,))
        thread.start()

    def run_export_thread(self, file_path):
        success, msg = self.exporter.export_data(self.current_df, file_path)
        self.after(0, lambda: self.finish_export(success, msg))

    def finish_export(self, success, msg):
        if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
            self.loading_window.destroy()
        if success: messagebox.showinfo("Exportação", msg)
        else: messagebox.showerror("Erro", msg)

    # =========================================================================
    # LÓGICA GRÁFICA
    # =========================================================================
    def on_column_change(self, choice):
        if self.current_df is None: return
        dtype = self.current_df[choice].dtype
        
        # Sugestão automática
        if pd.api.types.is_numeric_dtype(dtype):
            if "ano" in choice.lower() or "data" in choice.lower(): self.combo_chart_type.set("Linha")
            else: self.combo_chart_type.set("Histograma")
        else:
            if self.current_df[choice].nunique() < 5: self.combo_chart_type.set("Pizza")
            else: self.combo_chart_type.set("Barras")
        self.update_chart()

    def update_chart_slider(self, value):
        self.lbl_slider.configure(text=f"Top {int(value)}")

    def update_chart(self, _=None):
        if self.current_df is None: return
        
        for widget in self.canvas_frame.winfo_children(): widget.destroy()

        col_name = self.combo_columns.get()
        chart_type = self.combo_chart_type.get()
        top_n = int(self.slider_top_n.get())

        fig = plt.Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
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
            series = self.current_df[col_name].dropna()
            
            if chart_type == "Histograma":
                ax.hist(series, bins=30, color='#1f6aa5', edgecolor='white')
            elif chart_type == "Boxplot":
                ax.boxplot(series, vert=False, patch_artist=True, boxprops=dict(facecolor='#1f6aa5'), medianprops=dict(color='yellow'))
            elif chart_type == "Barras":
                series.value_counts().nlargest(top_n).sort_values().plot(kind='barh', ax=ax, color='#1fa565')
            elif chart_type == "Pizza":
                c = series.value_counts().nlargest(top_n)
                ax.pie(c, labels=c.index, autopct='%1.1f%%', textprops={'color':"white"})
            elif chart_type == "Linha":
                if pd.api.types.is_numeric_dtype(series): ax.plot(series.values, color='#ffa500')
                else: 
                    c = series.value_counts().sort_index()
                    ax.plot(c.index.astype(str), c.values, color='#ffa500')
            
            ax.set_title(f"{chart_type}: {col_name}")

            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            toolbar = NavigationToolbar2Tk(canvas, self.canvas_frame, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(side="bottom", fill="x")

        except Exception as e:
            ctk.CTkLabel(self.canvas_frame, text=f"Erro ao plotar: {str(e)}", text_color="red").pack(expand=True)

    def logout(self):
        self.destroy()
        from src.frontend.login import LoginScreen
        app = LoginScreen()
        app.mainloop()