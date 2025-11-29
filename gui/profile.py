# gui/profile.py
import tkinter as tk
from tkinter import messagebox, filedialog
from database.db import get_user_data, get_db_connection
import os 
from gui.widgets.profile_picture import create_profile_picture_frame


def show_user_profile(root, user_email):
    from gui.dashboard import clear_window, show_user_dashboard

    clear_window(root)
    root.title("My Profile")

    user_data = get_user_data(user_email)
    if not user_data:
        messagebox.showerror("Error", "Profile data not found.")
        show_user_dashboard(root, user_email, None)
        return


    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

  
    profile_pic_frame = create_profile_picture_frame(main_frame, user_email, user_data.get("profile_picture"))
    profile_pic_frame.pack(pady=10)
   
    tk.Label(main_frame, text="User Profile", font=("Arial", 18, "bold")).pack(pady=10)
    tk.Label(main_frame, text=f"Name: {user_data.get('name', 'N/A')}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text=f"Email: {user_data.get('email', 'N/A')}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text=f"Role: {user_data.get('role', 'user').capitalize()}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text="Bio:").pack(anchor="w", pady=5)
    bio_text = tk.Text(main_frame, height=5, width=40, state=tk.DISABLED)
    bio_text.insert(tk.END, user_data.get('bio', 'No bio provided.'))
    bio_text.pack(pady=5)

    tk.Button(main_frame, text="Back to Dashboard", width=30, command=lambda: show_user_dashboard(root, user_email, user_data.get('id'))).pack(pady=20)

# ---------------- Edit profile (separate window) ----------------

def edit_profile(user_email):
    edit_win = tk.Toplevel()
    edit_win.title("Edit Profile")
    edit_win.geometry("450x450")
    edit_win.resizable(True, True)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, bio, grad_year, major, profile_picture FROM users WHERE email=?", (user_email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        messagebox.showerror("Error", "User not found.")
        return

    name_var = tk.StringVar(value=user[0])
    email_var = tk.StringVar(value=user[1])
    bio_var = tk.StringVar(value=user[2] if user[2] else "")
    grad_var = tk.StringVar(value=user[3] if user[3] else "")
    major_var = tk.StringVar(value=user[4] if user[4] else "")
    pic_var = tk.StringVar(value=user[5] if user[5] else "")

    def choose_picture():
        filepath = filedialog.askopenfilename(title="Select Profile Picture", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if filepath:
            pic_var.set(filepath)

    def save_profile():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET name=?, email=?, bio=?, grad_year=?, major=?, profile_picture=?
            WHERE email=?
        """, (name_var.get(), email_var.get(), bio_var.get(), grad_var.get(), major_var.get(), pic_var.get(), user_email))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Profile updated successfully!")
        edit_win.destroy()

    tk.Label(edit_win, text="Name:").pack(pady=5)
    tk.Entry(edit_win, textvariable=name_var).pack(pady=5)

    tk.Label(edit_win, text="Email:").pack(pady=5)
    tk.Entry(edit_win, textvariable=email_var).pack(pady=5)

    tk.Label(edit_win, text="Bio:").pack(pady=5)
    tk.Entry(edit_win, textvariable=bio_var).pack(pady=5)

    tk.Label(edit_win, text="Graduation Year:").pack(pady=5)
    tk.Entry(edit_win, textvariable=grad_var).pack(pady=5)

    tk.Label(edit_win, text="Major:").pack(pady=5)
    tk.Entry(edit_win, textvariable=major_var).pack(pady=5)

    tk.Label(edit_win, text="Profile Picture:").pack(pady=5)
    tk.Entry(edit_win, textvariable=pic_var, state="readonly").pack(pady=5)
    tk.Button(edit_win, text="Choose Picture", command=choose_picture).pack(pady=5)

    tk.Button(edit_win, text="Save Changes", command=save_profile, bg="lightgreen").pack(pady=15)
