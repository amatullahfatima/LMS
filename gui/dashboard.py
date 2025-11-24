# gui/dashboard.py
import tkinter as tk
from tkinter import messagebox
from database.db import get_user_data, get_all_users, delete_user_db
from gui.profile_view import show_user_profile
from gui.profile_edit import edit_profile

from gui.posts import open_posts_window
from gui.search import search_students
from gui.widgets.profile_picture import create_profile_picture_frame

def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

def show_user_dashboard(root, user_email, user_id):
    clear_window(root)
    root.title("User Dashboard")
    root.geometry("500x500")

    user_data = get_user_data(user_email)
    if not user_data:
        messagebox.showerror("Error", "User data not found.")
        from gui.login import show_login_screen
        show_login_screen(root)
        return

   
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    pic_frame = create_profile_picture_frame(main_frame, user_email, user_data.get("profile_picture"), editable=False)
    pic_frame.pack(pady=10)
   

    # tk.Label(main_frame, text=f"Welcome, {user_data.get("name")}!", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(main_frame, text=f"Welcome, {user_data.get('name', 'User')}!", font=("Arial", 18, "bold")).pack(pady=10)

    tk.Label(main_frame, text="This is your main dashboard.", font=("Arial", 12)).pack(pady=5)
    tk.Button(main_frame, text="↻",font=("Arial", 20 , "bold"), width=30, bd=0, command=lambda: show_user_dashboard(root, user_email, user_id)).pack(pady=5)

    tk.Button(main_frame, text="View Profile", width=30, command=lambda: show_user_profile(root, user_email)).pack(pady=5)
    tk.Button(main_frame, text="Edit Profile", width=30, command=lambda: edit_profile(root, user_email  )).pack(pady=5)
    tk.Button(main_frame, text="Search Students", width=30, command=lambda: search_students(root, user_email)).pack(pady=5)
    tk.Button(main_frame, text="Open Posts", width=30, command=lambda: open_posts_window(user_email)).pack(pady=5)
    tk.Button(main_frame, text="Logout", width=30, command=lambda: from_gui_login(root)).pack(pady=15)

def from_gui_login(root):
    from gui.login import show_login_screen
    show_login_screen(root)

# --- Admin dashboard ---

# gui/dashboard.py

from database.db import get_db_connection
from gui.dashboard import clear_window
from gui.posts import open_posts_window
from tkinter import messagebox, Tk, Frame, Label, Button, Entry

# ---------------------- User Management Helper ----------------------

class UserManager:
    @staticmethod
    def deactivate_user(conn, email):
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if not user:
                messagebox.showerror("Error", f"No user found with email: {email}")
                return
            if user["is_active"] == 0:
                messagebox.showinfo("Info", f"User '{email}' is already deactivated")
                return
            cursor.execute("UPDATE users SET is_active = 0 WHERE email = ?", (email,))
            conn.commit()
            messagebox.showinfo("Success", f"User '{email}' has been deactivated.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    @staticmethod
    def reactivate_user(conn, email):
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if not user:
                messagebox.showerror("Error", f"No user found with email: {email}")
                return
            if user["is_active"] == 1:
                messagebox.showinfo("Info", f"User '{email}' is already active")
                return
            cursor.execute("UPDATE users SET is_active = 1 WHERE email = ?", (email,))
            conn.commit()
            messagebox.showinfo("Success", f"User '{email}' has been reactivated.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))



def show_admin_dashboard(root, admin_email):
    clear_window(root)
    root.title("Admin Dashboard")
    root.geometry("900x600")

    conn = get_db_connection()

    main_frame = Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill="both")

    Label(main_frame, text=f"Admin Dashboard - Logged in as {admin_email}",
          font=("Arial", 16, "bold")).pack(pady=10)

    Button(main_frame, text="Manage Users", width=30,
           command=lambda: show_all_users_admin(root, conn)).pack(pady=5)
    Button(main_frame, text="Manage Posts", width=30,
           command=lambda: open_posts_window(root)).pack(pady=5)
    # Button(main_frame, text="Notifications", width=30,
    #        command=lambda: show_notifications_page(root, conn)).pack(pady=5)
    Button(main_frame, text="Logout", width=30,
           command=lambda: from_gui_login(root)).pack(pady=20)


# def show_admin_dashboard(root, admin_email):
#     clear_window(root)
#     root.title("Admin Dashboard - User Management")

#     main_frame = tk.Frame(root, padx=30, pady=30)
#     main_frame.pack(expand=True)

#     tk.Label(main_frame, text="Admin Console", font=("Arial", 20, "bold"), fg="#8b0000").pack(pady=20)
#     tk.Label(main_frame, text=f"Logged in as: {admin_email}", font=("Arial", 10)).pack(pady=5)

#     tk.Button(main_frame, text="View All Users", width=30, command=lambda: show_all_users_admin(root, admin_email)).pack(pady=5)
#     tk.Button(main_frame, text="Register New User", width=30, command=lambda: from_gui_login(root)).pack(pady=5)
#     tk.Button(main_frame, text="Logout", width=30, command=lambda: from_gui_login(root)).pack(pady=20)

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

    user_listbox = tk.Listbox(list_frame, width=70, height=5, yscrollcommand=scrollbar.set)
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
