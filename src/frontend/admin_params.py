import customtkinter as ctk
from tkinter import messagebox
import os
from src.backend.config_manager import ConfigManager

class AdminParamsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Configuração SQL Server")
        self.geometry("400x450") # Ajustei levemente a altura já que tiramos texto
        
        if os.path.exists("CQLE.ico"):
            self.after(200, lambda: self.iconbitmap("CQLE.ico"))

        self.config_manager = ConfigManager()

        self.create_widgets()
        self.load_current_values()

    def create_widgets(self):
        # Título mantido
        ctk.CTkLabel(self, text="Parâmetros de Conexão", font=("Arial", 18, "bold")).pack(pady=20)
        
        # --- TEXTO EXPLICATIVO REMOVIDO DAQUI ---

        # Inputs
        self.entry_server = self._create_input("Servidor (IP ou Host)")
        self.entry_db = self._create_input("Nome do Banco de Dados")
        self.entry_user = self._create_input("Usuário SQL")
        self.entry_pass = self._create_input("Senha SQL", is_pass=True)

        # Botão Salvar
        ctk.CTkButton(self, text="TESTAR E SALVAR", fg_color="green", 
                      width=200, height=40, command=self.save_config).pack(pady=30)

    def _create_input(self, label_text, is_pass=False):
        ctk.CTkLabel(self, text=label_text, anchor="w").pack(padx=40, pady=(5, 0), fill="x")
        entry = ctk.CTkEntry(self, show="*" if is_pass else None)
        entry.pack(padx=40, pady=(0, 10), fill="x")
        return entry

    def load_current_values(self):
        """Preenche os campos se o arquivo já existir"""
        data = self.config_manager.load_db_config()
        if data:
            self.entry_server.insert(0, data.get("server", ""))
            self.entry_db.insert(0, data.get("database", ""))
            self.entry_user.insert(0, data.get("user", ""))
            self.entry_pass.insert(0, data.get("password", ""))

    def save_config(self):
        # 1. Coleta dados
        server = self.entry_server.get()
        db = self.entry_db.get()
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        # 2. Validação básica
        if not all([server, db, user, pwd]):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        # 3. Aviso de processamento (Visual)
        self.configure(cursor="watch") # Muda cursor para relógio
        self.update() # Força atualização da tela

        # 4. Teste de Conexão
        connected, msg_conn = self.config_manager.test_connection(server, db, user, pwd)

        self.configure(cursor="") # Volta cursor normal

        if not connected:
            # Se falhar, mostra o erro e NÃO salva
            messagebox.showerror("Falha na Conexão", f"Não foi possível conectar ao SQL Server:\n\n{msg_conn}")
            return

        # 5. Se conectou, salva o arquivo
        saved, msg_save = self.config_manager.save_db_config(server, db, user, pwd)
        
        if saved:
            messagebox.showinfo("Sucesso", "Conexão validada e configuração salva!")
            self.destroy()
        else:
            messagebox.showerror("Erro ao Salvar", msg_save)