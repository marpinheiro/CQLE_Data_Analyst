import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import numpy as np
import threading

from src.backend.data_loader import DataLoader
from src.backend.analyzer import DataAnalyzer
from src.backend.exporter import DataExporter

class UserDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CQLE Data Analyst -  v1.0")
        self.geometry("1200x800")
        
        # Aplica ícone na janela principal
        self.set_icon(self)

        # Backend
        self.loader = DataLoader()
        self.analyzer = None 
        self.exporter = DataExporter()
        self.current_df = None

        self.setup_table_style()
        self.create_layout()

    # --- HELPERS VISUAIS ---
    def set_icon(self, window):
        """Aplica o ícone CQLE.ico de forma segura"""
        if os.path.exists("CQLE.ico"):
            # O after(200) é um truque para garantir que o Windows registre o ícone em popups
            window.after(200, lambda: window.iconbitmap("CQLE.ico"))

    def center_toplevel(self, window, width, height):
        """Centraliza janelas pop-up em relação à tela"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        window.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def setup_table_style(self):
        style = ttk.Style()
        style.theme_use("default")
        
        # Paleta de Cores Profissional
        bg_color = "#212121" # Cinza bem escuro
        text_color = "#E0E0E0" # Branco gelo
        header_bg = "#1565C0" # Azul Material Design
        row_alt = "#2c2c2c" # Cinza levemente mais claro para linhas alternadas (se quiser implementar)

        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=text_color, 
                        fieldbackground=bg_color,
                        rowheight=28, # Linhas mais altas para respirar
                        borderwidth=0,
                        font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading", 
                        background=header_bg, 
                        foreground="white", 
                        relief="flat",
                        font=("Segoe UI", 11, "bold"))
        
        style.map("Treeview", background=[('selected', '#00796B')]) # Verde petróleo ao selecionar

    def create_layout(self):
        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Cabeçalho Sidebar
        ctk.CTkLabel(self.sidebar, text="CQLE ANALYST", font=("Roboto", 20, "bold")).pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="v1.0", font=("Arial", 10), text_color="gray").pack(pady=(0, 20))

        # Botão Cache
        self.btn_cache = ctk.CTkButton(self.sidebar, text="⚡ Sessão Anterior", height=40,
                                       fg_color="#C62828", hover_color="#B71C1C", font=("Roboto", 12, "bold"),
                                       command=self.load_cache_data)
        self.btn_cache.pack(pady=(10, 20), padx=20, fill="x")

        ctk.CTkLabel(self.sidebar, text="CONECTORES", font=("Roboto", 12, "bold"), text_color="gray").pack(pady=5, anchor="w", padx=20)

        self.btn_csv = ctk.CTkButton(self.sidebar, text="Abrir Arquivo Local", height=35, anchor="w", command=self.upload_local_file)
        self.btn_csv.pack(pady=5, padx=20, fill="x")

        self.btn_sql = ctk.CTkButton(self.sidebar, text="SQL Server", height=35, anchor="w", fg_color="#1565C0", hover_color="#0D47A1", command=self.connect_sql)
        self.btn_sql.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.sidebar, text="FERRAMENTAS", font=("Roboto", 12, "bold"), text_color="gray").pack(pady=(20, 5), anchor="w", padx=20)

        self.btn_export = ctk.CTkButton(self.sidebar, text="Exportar Dados", height=35, anchor="w", fg_color="#2E7D32", hover_color="#1B5E20", command=self.export_data)
        self.btn_export.pack(pady=5, padx=20, fill="x")

        # Rodapé Sidebar
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Sair do Sistema", fg_color="transparent", border_width=1, text_color="#E0E0E0", command=self.logout)
        self.btn_logout.pack(side="bottom", pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(self.sidebar, text="Dev: Marciano Silva", font=("Arial", 9), text_color="gray").pack(side="bottom", pady=5)

        # --- ABAS PRINCIPAIS ---
        self.tabview = ctk.CTkTabview(self, anchor="nw")
        self.tabview.pack(side="right", fill="both", expand=True, padx=20, pady=10)

        self.tab_resumo = self.tabview.add("   Resumo Executivo   ")
        self.tab_dados = self.tabview.add("   Visualizar Dados   ")
        self.tab_graficos = self.tabview.add("   Análise Gráfica   ")

        # Conteúdo Resumo
        self.txt_report = ctk.CTkTextbox(self.tab_resumo, font=("Consolas", 14), activate_scrollbars=True)
        self.txt_report.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_report.insert("0.0", "\n\n   👋 Olá!\n\n   Selecione uma fonte de dados no menu lateral para começar.")

        # Conteúdo Grid
        self.table_frame = ctk.CTkFrame(self.tab_dados, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.scroll_y = ttk.Scrollbar(self.table_frame, orient="vertical")
        self.scroll_x = ttk.Scrollbar(self.table_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(self.table_frame, yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        
        self.scroll_y.config(command=self.tree.yview)
        self.scroll_x.config(command=self.tree.xview)
        
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Conteúdo Gráficos
        self.graph_frame = ctk.CTkFrame(self.tab_graficos, fg_color="transparent")
        self.graph_frame.pack(fill="both", expand=True)

        # Painel Controles Gráficos (Card Style)
        self.controls_frame = ctk.CTkFrame(self.graph_frame, width=250, corner_radius=15)
        self.controls_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.controls_frame, text="Configuração", font=("Roboto", 16, "bold")).pack(pady=(20,10))
        
        ctk.CTkLabel(self.controls_frame, text="Coluna X:").pack(anchor="w", padx=20)
        self.combo_columns = ctk.CTkOptionMenu(self.controls_frame, values=[""], command=self.on_column_change)
        self.combo_columns.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(self.controls_frame, text="Tipo de Gráfico:").pack(anchor="w", padx=20)
        self.combo_chart_type = ctk.CTkOptionMenu(self.controls_frame, values=["Histograma", "Boxplot", "Barras", "Pizza", "Linha"], command=self.update_chart)
        self.combo_chart_type.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(self.controls_frame, text="Filtros (Top N):").pack(anchor="w", padx=20)
        self.slider_top_n = ctk.CTkSlider(self.controls_frame, from_=5, to=50, number_of_steps=9, command=self.update_chart_slider)
        self.slider_top_n.set(10)
        self.slider_top_n.pack(fill="x", padx=20, pady=(0, 5))
        self.lbl_slider = ctk.CTkLabel(self.controls_frame, text="Top 10")
        self.lbl_slider.pack()

        ctk.CTkButton(self.controls_frame, text="🔄 Atualizar Gráfico", height=40, font=("Roboto", 13, "bold"), fg_color="green", command=self.update_chart).pack(pady=30, padx=20)

        # Canvas
        self.canvas_frame = ctk.CTkFrame(self.graph_frame, fg_color="#2b2b2b")
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.lbl_placeholder = ctk.CTkLabel(self.canvas_frame, text="Selecione uma coluna para visualizar.", font=("Roboto", 14))
        self.lbl_placeholder.pack(expand=True)

    # --- LÓGICA CORE ---
    def update_interface(self):
        df = self.loader.get_dataframe()
        if df is None: return
        self.current_df = df

        self.analyzer = DataAnalyzer(df)
        report = self.analyzer.generate_text_report()
        self.txt_report.delete("0.0", "end")
        self.txt_report.insert("0.0", report)
        self.update_table_view(df)
        
        cols = list(df.columns)
        self.combo_columns.configure(values=cols)
        self.combo_columns.set(cols[0]) 
        self.on_column_change(cols[0])

    def update_table_view(self, df):
        self.tree.delete(*self.tree.get_children())
        cols = list(df.columns)
        self.tree["columns"] = cols
        self.tree["show"] = "headings"
        for col in cols:
            self.tree.heading(col, text=col)
            width = max(100, len(str(col)) * 10)
            self.tree.column(col, width=width, minwidth=50, anchor="w")
        rows_to_show = df.head(5000).to_numpy().tolist()
        for row in rows_to_show:
            clean_row = [str(x) if str(x) != 'nan' else "" for x in row]
            self.tree.insert("", "end", values=clean_row)

    # --- LÓGICA DE LOADING COM ÍCONE E CENTRALIZAÇÃO ---
    def load_cache_data(self):
        success, msg = self.loader.load_from_cache()
        if success:
            self.update_interface()
            messagebox.showinfo("Sucesso", "Dados restaurados!")
        else:
            messagebox.showwarning("Aviso", msg)

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
        self.center_toplevel(selector, 400, 500) # Centraliza
        self.set_icon(selector) # Põe ícone
        selector.grab_set()
        
        ctk.CTkLabel(selector, text="Tabelas Disponíveis", font=("Roboto", 16, "bold")).pack(pady=15)
        scroll = ctk.CTkScrollableFrame(selector, width=350, height=350)
        scroll.pack(pady=10, padx=10, fill="both", expand=True)

        def start_loading_thread(table_name):
            selector.destroy()
            
            # JANELA DE LOADING MELHORADA
            self.loading_window = ctk.CTkToplevel(self)
            self.loading_window.title("Aguarde")
            self.center_toplevel(self.loading_window, 300, 180) # Centraliza
            self.set_icon(self.loading_window) # Põe ícone
            self.loading_window.grab_set()
            
            ctk.CTkLabel(self.loading_window, text=f"Baixando: {table_name}", font=("Roboto", 14, "bold")).pack(pady=(25, 5))
            ctk.CTkLabel(self.loading_window, text="Isso pode levar alguns instantes...", font=("Arial", 11), text_color="gray").pack(pady=0)
            
            progress = ctk.CTkProgressBar(self.loading_window, width=220, mode="indeterminate")
            progress.pack(pady=20)
            progress.start()
            
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
                messagebox.showinfo("Sucesso", "Dados carregados!")
            else:
                messagebox.showerror("Erro", msg)

        for tb in tables:
            ctk.CTkButton(scroll, text=tb, fg_color="transparent", border_width=1, text_color=("black", "white"), anchor="w",
                          command=lambda t=tb: start_loading_thread(t)).pack(fill="x", pady=2, padx=5)

    def upload_local_file(self):
        path = filedialog.askopenfilename(filetypes=[("Dados", "*.csv;*.xlsx;*.xls")])
        if path:
            success, msg = self.loader.load_file(path)
            if success: self.update_interface()
            else: messagebox.showerror("Erro", msg)

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

        # JANELA DE EXPORTAÇÃO MELHORADA
        self.loading_window = ctk.CTkToplevel(self)
        self.loading_window.title("Exportando")
        self.center_toplevel(self.loading_window, 300, 150)
        self.set_icon(self.loading_window)
        self.loading_window.grab_set()
        
        label_text = "Gerando Excel..." if ".xlsx" in file_path else "Gerando CSV..."
        ctk.CTkLabel(self.loading_window, text=label_text, font=("Roboto", 14, "bold")).pack(pady=25)
        progress = ctk.CTkProgressBar(self.loading_window, width=220, mode="indeterminate")
        progress.pack(pady=10)
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

    # --- GRÁFICOS ---
    def on_column_change(self, choice):
        if self.current_df is None: return
        dtype = self.current_df[choice].dtype
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
            ctk.CTkLabel(self.canvas_frame, text=f"Erro: {str(e)}", text_color="red").pack(expand=True)

    def logout(self):
        self.destroy()
        from src.frontend.login import LoginScreen
        app = LoginScreen()
        app.mainloop()