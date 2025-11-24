import tkinter as tk
from tkinter import messagebox
from database.db import register_user_db

def show_registration_screen(root):
    reg_win = tk.Toplevel(root)
    reg_win.title("Register New User")
    reg_win.geometry("400x400")

    tk.Label(reg_win, text="Register New Account", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(reg_win, text="Name:").pack()
    name_entry = tk.Entry(reg_win)
    name_entry.pack()


    tk.Label(reg_win, text="Email:").pack()
    email_entry = tk.Entry(reg_win)
    email_entry.pack()

    tk.Label(reg_win, text="Password:").pack()
    password_entry = tk.Entry(reg_win, show="*")
    password_entry.pack()

    tk.Label(reg_win, text="Confirm Password:").pack()
    confirm_entry = tk.Entry(reg_win, show="*")
    confirm_entry.pack()

    def register_user():
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        confirm = confirm_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        success = register_user_db(email, password,name)
        if success:
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
            reg_win.destroy()
        else:
            messagebox.showerror("Error", "Email already exists. Try a different one.")

    tk.Button(reg_win, text="Register", command=register_user, bg="#0078D7", fg="white").pack(pady=10)
