# gui/login.py
import tkinter as tk
from tkinter import messagebox
from database.db import verify_user_credentials, register_user_db
from gui.dashboard import show_user_dashboard, show_admin_dashboard
from gui.profile import show_user_profile
from gui.register import  show_registration_screen
from gui.forgot_password import show_forgot_password_screen
ADMIN_USER = 'admin@dcccd.edu'

def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

def process_login(root, email, password):
    if not email or not password:
        messagebox.showerror("Login Failed", "Email and password are required.")
        return

    user_data = verify_user_credentials(email, password)

    if user_data:
        messagebox.showinfo("Login Successful", f"Welcome, {user_data['name']}!")
        if user_data['role'] == 'admin':
            show_admin_dashboard(root, user_data['email'])
        else:
            show_user_dashboard(root, user_data['email'], user_data['id'])
    else:
        messagebox.showerror("Login Failed", "Invalid email or password.")

def show_login_screen(root):
    clear_window(root)
    root.title("Login | Social Media Platform")

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="User Login", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(main_frame, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.grid(row=1, column=1, pady=5)
    email_entry.insert(0, ADMIN_USER)

    tk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
    password_entry = tk.Entry(main_frame, width=30, show="*")
    password_entry.grid(row=2, column=1, pady=5)
    password_entry.insert(0, "admin123")

    login_button = tk.Button(main_frame, text="Login", width=20,
                             command=lambda: process_login(root, email_entry.get(), password_entry.get()))
    login_button.grid(row=3, column=0, columnspan=2, pady=10)

    register_button = tk.Button(main_frame, text="Register New User", width=20,
                                command=lambda: show_registration_screen(root))
    register_button.grid(row=4, column=0, columnspan=2, pady=5)

    tk.Button(main_frame, text="Forgot Password?", width=20, command=lambda: show_forgot_password_screen(root)).grid(row=5, column=0, columnspan=2, pady=5)
