import tkinter as tk 
from tkinter import messagebox

from database.db import reset_password_db 

def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

def show_forgot_password_screen(root):
    clear_window(root)
    root.title("Forgot Password")

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="Reset Your Password", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    # Email field
    tk.Label(main_frame, text="Enter your registered email:").grid(row=1, column=0, sticky="w", pady=5)
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.grid(row=1, column=1, pady=5)

    # New Password
    tk.Label(main_frame, text="New Password:").grid(row=2, column=0, sticky="w", pady=5)
    new_pw_entry = tk.Entry(main_frame, width=30, show="*")
    new_pw_entry.grid(row=2, column=1, pady=5)

    # Confirm Password
    tk.Label(main_frame, text="Confirm Password:").grid(row=3, column=0, sticky="w", pady=5)
    confirm_pw_entry = tk.Entry(main_frame, width=30, show="*")
    confirm_pw_entry.grid(row=3, column=1, pady=5)

    def reset_password():
        email = email_entry.get().strip()
        new_pw = new_pw_entry.get().strip()
        confirm_pw = confirm_pw_entry.get().strip()

        if not email or not new_pw:
            messagebox.showerror("Error", "All fields are required.")
            return
        if new_pw != confirm_pw:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        if len(new_pw) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters.")
            return

        # ✅ Call the separate database function
        result, message = reset_password_db(email, new_pw)

        if result:
            messagebox.showinfo("Success", message)
            go_back_to_login(root)
        else:
            messagebox.showerror("Error", message)

    tk.Button(main_frame, text="Reset Password", width=20, command=reset_password).grid(row=4, column=0, columnspan=2, pady=10)
    tk.Button(main_frame, text="Back to Login", width=20, command=lambda: go_back_to_login(root)).grid(row=5, column=0, columnspan=2, pady=5)



    def go_back_to_login(root):
        from gui.login import show_login_screen 
        show_login_screen(root)
