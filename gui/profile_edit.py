import tkinter as tk
from tkinter import messagebox, filedialog
from database.db import get_user_data, get_db_connection
from gui.widgets.profile_picture import create_profile_picture_frame


def edit_profile(root, user_email):
    """Open a separate window for editing the user profile."""
    edit_win = tk.Toplevel()
    edit_win.title("Edit Profile")
    edit_win.geometry("450x500")
    edit_win.resizable(True, True)

    # Get user data using existing helper function
    user_data = get_user_data(user_email)
    if not user_data:
        messagebox.showerror("Error", "User not found.")
        return

    # Access fields by column name
    name_var = tk.StringVar(value=user_data.get("name", ""))
    email_var = tk.StringVar(value=user_data.get("email", ""))
    bio_var = tk.StringVar(value=user_data.get("bio", ""))
    grad_var = tk.StringVar(value=user_data.get("grad_year", ""))
    major_var = tk.StringVar(value=user_data.get("major", ""))
    role_var = tk.StringVar(value=user_data.get("role", ""))
    pic_var = tk.StringVar(value=user_data.get("profile_picture", ""))

    tk.Label(edit_win, text="Edit Profile", font=("Arial", 16, "bold")).pack(pady=10)

  
     #Show profile picture (using helper function)
    profile_pic_frame = create_profile_picture_frame(
        edit_win,
        user_email,
        user_data.get("profile_picture")
    )
    profile_pic_frame.pack(pady=10)
    def labeled_entry(label, var):
        tk.Label(edit_win, text=label).pack(pady=4)
        tk.Entry(edit_win, textvariable=var).pack(pady=3)

    labeled_entry("Name:", name_var)
    labeled_entry("Email:", email_var)
    labeled_entry("Bio:", bio_var)
    labeled_entry("Role:", role_var)
    labeled_entry("Graduation Year:", grad_var)
    labeled_entry("Major:", major_var)
 

   

    def save_profile():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET name=?, email=?, bio=?, role=? , grad_year=?, major=?, profile_picture=?
            WHERE email=?
        """, (
            name_var.get(),
            email_var.get(),
            bio_var.get(),
            role_var.get(),
            grad_var.get(),
            major_var.get(),
            pic_var.get(),
            user_email
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Profile updated successfully!")
        edit_win.destroy()

    tk.Button(
        edit_win, text="Save Changes",
        bg="#4CAF50", fg="white", width=20,
        command=save_profile
    ).pack(pady=15)
  
  
  