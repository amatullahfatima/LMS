
import tkinter as tk
from tkinter import messagebox
from database.db import  get_all_users, delete_user_db
from gui.dashboard import clear_window
from gui.dashboard import show_admin_dashboard

def show_all_users_admin(root, admin_email):
    clear_window(root)
    root.title("Admin - Manage Users")

    users = get_all_users()

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(main_frame, text="All Registered Users", font=("Arial", 16, "bold")).pack(pady=10)

    list_frame = tk.Frame(main_frame)
    list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    user_listbox = tk.Listbox(list_frame, width=70, height=15, yscrollcommand=scrollbar.set)
    scrollbar.config(command=user_listbox.yview)
    user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    if users:
        for user in users:
            display_str = f"{user['email']} | Name: {user['name']} | Role: {user['role'].capitalize()}"
            user_listbox.insert(tk.END, display_str)
    else:
        user_listbox.insert(tk.END, "No users found in the database.")

    def prompt_delete_user():
        selected_index = user_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a user to delete.")
            return
        selected_item = user_listbox.get(selected_index[0])
        target_email = selected_item.split(' | ')[0].strip()
        if target_email == admin_email:
            messagebox.showerror("Error", "You cannot delete your own admin account.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user: {target_email}?"):
            if delete_user_db(target_email):
                messagebox.showinfo("Success", f"User {target_email} has been deleted.")
                show_all_users_admin(root, admin_email)
            else:
                messagebox.showerror("Error", "Failed to delete user.")

    tk.Button(main_frame, text="Delete Selected User", width=30, fg="red", command=prompt_delete_user).pack(pady=10)
    tk.Button(main_frame, text="Back to Admin Dashboard", width=30, command=lambda: show_admin_dashboard(root, admin_email)).pack(pady=5)
