import customtkinter as ctk
from tkinter import messagebox
import os
from src.backend.auth import AuthManager

class LoginScreen(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURAÇÃO DA JANELA ---
        self.title("Login - CQLE Data Analyst")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Configurando o Ícone
        if os.path.exists("CQLE.ico"):
            self.iconbitmap("CQLE.ico")
        
        # Backend de Autenticação
        self.auth = AuthManager()

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Frame Centralizado
        frame = ctk.CTkFrame(self, width=320, height=360, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Título
        label_title = ctk.CTkLabel(frame, text="CQLE Login", font=("Roboto", 24, "bold"))
        label_title.pack(pady=(40, 20))

        # Campo Usuário
        self.entry_user = ctk.CTkEntry(frame, width=220, placeholder_text="Usuário")
        self.entry_user.pack(pady=10)

        # Campo Senha
        self.entry_pass = ctk.CTkEntry(frame, width=220, placeholder_text="Senha", show="*")
        self.entry_pass.pack(pady=10)

        # Botão Entrar
        btn_login = ctk.CTkButton(frame, text="ENTRAR", width=220, command=self.perform_login)
        btn_login.pack(pady=20)

        # Rodapé
        label_footer = ctk.CTkLabel(frame, text="v1.0.0", text_color="gray", font=("Arial", 10))
        label_footer.pack(side="bottom", pady=10)

    def perform_login(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()

        # result retorna uma tupla: (role, status) ou None
        result = self.auth.login(user, password)

        if result:
            self.open_dashboard(result)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos (ou usuário inativo).")

    def open_dashboard(self, role_info):
        """
        Gerencia o redirecionamento baseado no Role e no Status.
        """
        role = role_info[0]
        status = role_info[1]
        
        # Capturamos o username antes de destruir a tela
        username = self.entry_user.get()

        # --- IMPORTAÇÕES TARDIAS (LATE IMPORT) ---
        # Importamos aqui dentro para evitar "ImportError" circular e garantir
        # que as classes só sejam carregadas quando necessário.
        from src.frontend.admin_view import AdminDashboard
        from src.frontend.change_password import ChangePasswordScreen
        
        # Fechamos a tela de Login
        self.destroy()

        # --- LÓGICA DE ROTEAMENTO ---
        
        # 1. Se Status for 1 (Novo) ou 3 (Resetado) -> OBRIGA TROCA DE SENHA
        if status in [1, 3]:
            app = ChangePasswordScreen(username, role)
            app.mainloop()
            
        # 2. Se for ADMIN e status normal (2 ou 5)
        elif role == 'admin':
            app = AdminDashboard()
            app.mainloop()
            
        # 3. Se for USUÁRIO COMUM e status normal
        else:
            self.open_user_dashboard_placeholder()

    def open_user_dashboard_placeholder(self):
        # Tela temporária para o usuário comum
        dash = ctk.CTk()
        dash.geometry("800x600")
        dash.title("CQLE - User Dashboard")
        
        if os.path.exists("CQLE.ico"): 
            dash.iconbitmap("CQLE.ico")
            
        ctk.CTkLabel(dash, text="Bem-vindo ao Sistema", font=("Arial", 24)).pack(pady=50)
        ctk.CTkLabel(dash, text="(Painel do Usuário em Desenvolvimento)", text_color="gray").pack()
        
        dash.mainloop()