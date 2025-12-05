import tkinter as tk
from tkinter import messagebox
from database.db import update_email_in_db
from gui.theme_manager import apply_theme



def open_update_email_window(root, user_email):
    """Window to update user email."""

    from gui.dashboard import clear_window, show_user_dashboard

    clear_window(root)
    root.title("Update Email")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True)

    apply_theme(frame)

    tk.Label(frame, text="Update Email", font=("Arial", 18, "bold")).pack(pady=10)

    tk.Label(frame, text="New Email:").pack(anchor="w")
    email_entry = tk.Entry(frame, width=30)
    email_entry.pack(pady=5)
    email_entry.insert(0, user_email)

    def save_email():
        new_email = email_entry.get().strip()

        if not new_email:
            messagebox.showerror("Error", "Email cannot be empty.")
            return
        
        success = update_email_in_db(user_email, new_email)

        if success:
            messagebox.showinfo("Success", "Email updated successfully.")
            show_user_dashboard(root, new_email, None)
        else:
            messagebox.showerror("Error", "Failed to update email.")

    tk.Button(frame, text="Save", width=15, command=save_email).pack(pady=10)
    tk.Button(frame, text="Back", width=15, command=lambda: show_user_dashboard(root, user_email, None)).pack()

    apply_theme(frame)
