import customtkinter as ctk
from tkinter import filedialog
from src.backend.data_loader import DataLoader

# Configuração visual padrão
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("CQLE Data Analyst - v1.0")
        self.geometry("900x600")
        
        # Backend Instance
        self.data_loader = DataLoader()

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Frame Lateral (Menu)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="CQLE Analyst", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=(20, 10))

        self.btn_load = ctk.CTkButton(self.sidebar, text="Carregar Dados", command=self.upload_file)
        self.btn_load.pack(padx=20, pady=10)

        # Área Principal
        self.main_area = ctk.CTkFrame(self, corner_radius=10)
        self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.info_label = ctk.CTkLabel(self.main_area, text="Bem-vindo! Carregue um arquivo para começar.", font=("Arial", 16))
        self.info_label.pack(pady=20)

        # Área de Texto para Relatório (Simulação)
        self.report_text = ctk.CTkTextbox(self.main_area, width=600, height=400)
        self.report_text.pack(pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Dados", "*.csv;*.xlsx;*.xls")])
        
        if file_path:
            success, message = self.data_loader.load_file(file_path)
            self.info_label.configure(text=message)
            
            if success:
                # Mostra um resumo rápido no box de texto
                summary = self.data_loader.get_summary()
                self.report_text.delete("0.0", "end")
                self.report_text.insert("0.0", summary)