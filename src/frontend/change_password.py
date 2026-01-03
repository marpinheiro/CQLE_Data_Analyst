import customtkinter as ctk
from tkinter import messagebox
import os
from src.backend.auth import AuthManager

# Importação condicional para evitar erro de importação circular se necessário
# Mas aqui vamos importar dentro do método para garantir
# from src.frontend.admin_view import AdminDashboard 

class ChangePasswordScreen(ctk.CTk):
    def __init__(self, username, role):
        super().__init__()
        
        self.username = username
        self.role = role
        self.auth = AuthManager()

        self.title("CQLE - Alteração de Senha Obrigatória")
        self.geometry("400x450")
        
        if os.path.exists("CQLE.ico"):
            self.iconbitmap("CQLE.ico")

        self.create_widgets()

    def create_widgets(self):
        # Frame
        frame = ctk.CTkFrame(self, width=320, height=360, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Troca de Senha", font=("Arial", 20, "bold")).pack(pady=(30, 10))
        
        msg = "Seu acesso é novo ou foi resetado.\nPor segurança, defina uma nova senha."
        ctk.CTkLabel(frame, text=msg, font=("Arial", 12), text_color="yellow").pack(pady=10)

        # Nova Senha
        self.entry_new = ctk.CTkEntry(frame, width=220, placeholder_text="Nova Senha", show="*")
        self.entry_new.pack(pady=10)

        # Confirmar Senha
        self.entry_conf = ctk.CTkEntry(frame, width=220, placeholder_text="Confirmar Nova Senha", show="*")
        self.entry_conf.pack(pady=10)

        # Botão Salvar
        ctk.CTkButton(frame, text="SALVAR NOVA SENHA", width=220, fg_color="green", command=self.save_password).pack(pady=20)

    def save_password(self):
        new_pass = self.entry_new.get()
        conf_pass = self.entry_conf.get()

        if not new_pass or not conf_pass:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        if new_pass != conf_pass:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
            
        if len(new_pass) < 4: # Regra básica
             messagebox.showwarning("Aviso", "A senha deve ter no mínimo 4 caracteres.")
             return

        # Chama Backend
        success, msg = self.auth.force_password_change(self.username, new_pass)
        
        if success:
            messagebox.showinfo("Sucesso", "Senha atualizada! Redirecionando...")
            self.redirect_to_dashboard()
        else:
            messagebox.showerror("Erro", msg)

    def redirect_to_dashboard(self):
        self.destroy() # Fecha tela de troca de senha
        
        # Redirecionamento baseado no Role
        if self.role == 'admin':
            from src.frontend.admin_view import AdminDashboard
            app = AdminDashboard()
            app.mainloop()
        else:
            # Dashboard do Usuário Comum (ainda usaremos o placeholder)
            self.open_user_dashboard()

    def open_user_dashboard(self):
        # Janela temporária até criarmos o Dashboard Real na próxima etapa
        dash = ctk.CTk()
        dash.geometry("800x600")
        dash.title("CQLE - User Dashboard")
        if os.path.exists("CQLE.ico"): dash.iconbitmap("CQLE.ico")
        ctk.CTkLabel(dash, text="Bem-vindo ao Sistema (Usuário)", font=("Arial", 24)).pack(pady=50)
        dash.mainloop()