import customtkinter as ctk
from tkinter import messagebox, Toplevel
import os
from src.backend.admin_controller import AdminController
from src.frontend.admin_params import AdminParamsWindow

class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CQLE Admin - Gestão de Usuários")
        self.geometry("1000x600")
        
        if os.path.exists("CQLE.ico"):
            self.iconbitmap("CQLE.ico")

        self.controller = AdminController()
        
        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()
        
        # Carrega dados iniciais
        self.refresh_table()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        lbl = ctk.CTkLabel(self.sidebar, text="ADMIN PAINEL", font=("Arial", 20, "bold"))
        lbl.pack(pady=30)

        btn_users = ctk.CTkButton(self.sidebar, text="Usuários", state="disabled", fg_color="gray")
        btn_users.pack(pady=10, padx=20)
        
        btn_params = ctk.CTkButton(self.sidebar, text="Parâmetros", command=self.show_params_msg)
        btn_params.pack(pady=10, padx=20)

    def show_params_msg(self):
        # Abre a janela modal de parâmetros
        param_window = AdminParamsWindow(self)
        param_window.grab_set() # Foca na janela e impede clique na janela de trás

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Cabeçalho
        header = ctk.CTkFrame(self.main_frame, height=50, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        lbl_title = ctk.CTkLabel(header, text="Gestão de Usuários", font=("Arial", 18))
        lbl_title.pack(side="left")

        btn_new = ctk.CTkButton(header, text="+ Novo Usuário", fg_color="green", command=self.open_user_modal)
        btn_new.pack(side="right")

        # Área da Tabela (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Lista de Usuários Ativos")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_table(self):
        # Limpa tabela atual
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        users = self.controller.get_all_users()

        # Cabeçalhos
        cols = ["ID", "Usuário", "Nome Completo", "Role", "Status", "Ações"]
        for i, col in enumerate(cols):
            ctk.CTkLabel(self.scroll_frame, text=col, font=("Arial", 12, "bold")).grid(row=0, column=i, padx=10, pady=5)

        # Linhas
        for idx, user in enumerate(users, start=1):
            u_id, u_user, u_name, u_role, u_status, _, _ = user
            
            ctk.CTkLabel(self.scroll_frame, text=str(u_id)).grid(row=idx, column=0, padx=5)
            ctk.CTkLabel(self.scroll_frame, text=u_user).grid(row=idx, column=1, padx=5)
            ctk.CTkLabel(self.scroll_frame, text=u_name).grid(row=idx, column=2, padx=5)
            ctk.CTkLabel(self.scroll_frame, text=u_role).grid(row=idx, column=3, padx=5)
            
            # Traduz status visualmente
            status_text = f"Status {u_status}"
            if u_status == 1: status_text += " (Novo)"
            if u_status == 3: status_text += " (Reset)"
            ctk.CTkLabel(self.scroll_frame, text=status_text).grid(row=idx, column=4, padx=5)

            # Botões de Ação
            action_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            action_frame.grid(row=idx, column=5, padx=5, pady=2)

            ctk.CTkButton(action_frame, text="Editar", width=60, command=lambda u=user: self.open_user_modal(u)).pack(side="left", padx=2)
            ctk.CTkButton(action_frame, text="Reset", width=60, fg_color="orange", command=lambda id=u_id: self.reset_user_pass(id)).pack(side="left", padx=2)
            ctk.CTkButton(action_frame, text="Excluir", width=60, fg_color="red", command=lambda id=u_id: self.delete_user_action(id)).pack(side="left", padx=2)

    # --- AÇÕES ---
    def delete_user_action(self, uid):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir (desativar) este usuário?"):
            success, msg = self.controller.delete_user(uid)
            if success:
                self.refresh_table()
            else:
                messagebox.showerror("Erro", msg)

    def reset_user_pass(self, uid):
        if messagebox.askyesno("Confirmar", "A senha será resetada para 'Mud@r123'. Confirmar?"):
            success, msg = self.controller.reset_password(uid)
            messagebox.showinfo("Info", msg)
            self.refresh_table()

    def open_user_modal(self, user_data=None):
        # Janela Modal para Criar/Editar
        modal = ctk.CTkToplevel(self)
        modal.title("Usuário")
        modal.geometry("400x400")
        modal.grab_set() # Foca na janela
        
        if os.path.exists("CQLE.ico"):
            modal.iconbitmap("CQLE.ico")

        ctk.CTkLabel(modal, text="Nome de Usuário (Login)").pack(pady=5)
        entry_user = ctk.CTkEntry(modal)
        entry_user.pack(pady=5)
        
        ctk.CTkLabel(modal, text="Nome Completo").pack(pady=5)
        entry_name = ctk.CTkEntry(modal)
        entry_name.pack(pady=5)

        ctk.CTkLabel(modal, text="Perfil (Role)").pack(pady=5)
        combo_role = ctk.CTkComboBox(modal, values=["user", "admin", "analyst"])
        combo_role.pack(pady=5)

        # Se for edição, preenche dados
        if user_data:
            entry_user.insert(0, user_data[1])
            entry_user.configure(state="disabled") # Não pode mudar username
            entry_name.insert(0, user_data[2])
            combo_role.set(user_data[3])
            btn_text = "Salvar Alterações"
        else:
            btn_text = "Criar Usuário"

        def save():
            user = entry_user.get()
            name = entry_name.get()
            role = combo_role.get()

            if not user or not name:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return

            if user_data: # Edição
                success, msg = self.controller.edit_user(user_data[0], name, role)
            else: # Criação
                success, msg = self.controller.create_user(user, name, role)

            if success:
                messagebox.showinfo("Sucesso", msg)
                modal.destroy()
                self.refresh_table()
            else:
                messagebox.showerror("Erro", msg)

        ctk.CTkButton(modal, text=btn_text, command=save).pack(pady=20)