import customtkinter as ctk
from tkinter import messagebox
import os
from src.backend.auth import AuthManager

# Tema padrão
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class LoginScreen(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURAÇÃO DA JANELA ---
        self.title("Acesso Restrito - CQLE")
        self.geometry("400x550") # Aumentei um pouco para caber os créditos
        self.resizable(False, False)
        
        # Centralizar na tela
        self.center_window(400, 550)
        
        # Configurando o Ícone
        if os.path.exists("CQLE.ico"):
            self.iconbitmap("CQLE.ico")
        
        self.auth = AuthManager()
        self.create_widgets()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def create_widgets(self):
        # Frame "Card" Centralizado com borda sutil
        self.frame = ctk.CTkFrame(self, width=340, height=420, corner_radius=20, border_width=1, border_color="#404040")
        self.frame.place(relx=0.5, rely=0.45, anchor="center") # Um pouco para cima para caber o rodapé

        # Logo / Título
        ctk.CTkLabel(self.frame, text="CQLE Analyst", font=("Roboto Medium", 28)).pack(pady=(40, 10))
        ctk.CTkLabel(self.frame, text="Bem-vindo de volta", font=("Roboto", 14), text_color="gray").pack(pady=(0, 20))

        # Campo Usuário
        self.entry_user = ctk.CTkEntry(self.frame, width=260, height=40, placeholder_text="Usuário", font=("Roboto", 14))
        self.entry_user.pack(pady=10)

        # Campo Senha
        self.entry_pass = ctk.CTkEntry(self.frame, width=260, height=40, placeholder_text="Senha", show="*", font=("Roboto", 14))
        self.entry_pass.pack(pady=10)

        # Switch Mostrar Senha
        self.show_pass_var = ctk.StringVar(value="off")
        self.switch_show = ctk.CTkSwitch(
            self.frame, 
            text="Mostrar Senha", 
            variable=self.show_pass_var, 
            onvalue="on", offvalue="off",
            command=self.toggle_password,
            font=("Roboto", 12),
            width=260
        )
        self.switch_show.pack(pady=(5, 20))

        # Botão Entrar
        self.btn_login = ctk.CTkButton(
            self.frame, text="ENTRAR", width=260, height=40, 
            font=("Roboto", 14, "bold"), 
            command=self.perform_login
        )
        self.btn_login.pack(pady=10)

        # --- CRÉDITOS NO RODAPÉ (Fora do Card) ---
        self.lbl_version = ctk.CTkLabel(self, text="Versão 1.0", font=("Arial", 10), text_color="gray")
        self.lbl_version.pack(side="bottom", pady=(0, 5))
        
        self.lbl_credits = ctk.CTkLabel(self, text="Desenvolvido por Marciano Silva\nCQLE Softwares", font=("Arial", 11, "bold"), text_color="#1f6aa5")
        self.lbl_credits.pack(side="bottom", pady=(0, 10))

    def toggle_password(self):
        if self.show_pass_var.get() == "on":
            self.entry_pass.configure(show="")
        else:
            self.entry_pass.configure(show="*")

    def perform_login(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()
        result = self.auth.login(user, password)

        if result:
            self.open_dashboard(result)
        else:
            messagebox.showerror("Acesso Negado", "Usuário ou senha incorretos.")

    def open_dashboard(self, role_info):
        role = role_info[0]
        status = role_info[1]
        username = self.entry_user.get()

        from src.frontend.admin_view import AdminDashboard
        from src.frontend.change_password import ChangePasswordScreen
        
        self.destroy()

        if status in [1, 3]:
            app = ChangePasswordScreen(username, role)
            app.center_window(app, 400, 450) # Assumindo que implementaremos helper lá, ou deixa padrão
            app.mainloop()
        elif role == 'admin':
            app = AdminDashboard()
            app.mainloop()
        else:
            self.open_user_dashboard_placeholder()

    def open_user_dashboard_placeholder(self):
        from src.frontend.user_dashboard import UserDashboard
        app = UserDashboard()
        app.mainloop()