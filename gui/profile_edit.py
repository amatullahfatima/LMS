import tkinter as tk
from tkinter import messagebox, filedialog
from database.db import get_user_data, get_db_connection
from gui.widgets.profile_picture import create_profile_picture_frame

def edit_profile(root, user_email):
    """Open a separate window for editing the user profile."""
    user_data = get_user_data(user_email)
    if not user_data:
        messagebox.showerror("Error", "User not found.")
        return

    edit_win = tk.Toplevel(root)
    edit_win.title(f"{user_data.get('name', 'User')} | Edit Profile")
    edit_win.geometry("400x650")
    edit_win.resizable(True, True)

    # Tkinter variables
    name_var = tk.StringVar(value=user_data.get("name", ""))
    email_var = tk.StringVar(value=user_data.get("email", ""))
    bio_var = tk.StringVar(value=user_data.get("bio", ""))
    grad_var = tk.StringVar(value=user_data.get("grad_year", ""))
    major_var = tk.StringVar(value=user_data.get("major", ""))
    role_var = tk.StringVar(value=user_data.get("role", ""))
    pic_var = tk.StringVar(value=user_data.get("profile_picture", ""))

    # Header
    tk.Label(edit_win, text="Edit Profile", font=("Arial", 14, "bold")).pack(pady=10)

    # Profile Picture
    profile_pic_frame = create_profile_picture_frame(
        edit_win,
        user_email,
        user_data.get("profile_picture")
    )
    profile_pic_frame.pack(pady=10)

    # Helper for labeled entry
    def labeled_entry(label, var, readonly=False):
        tk.Label(edit_win, text=label).pack(pady=2)
        entry = tk.Entry(edit_win, textvariable=var)
        if readonly:
            entry.config(state="readonly")
        entry.pack(pady=2)

    labeled_entry("Name:", name_var)
    labeled_entry("Email:", email_var, readonly=True)  # Email is now read-only
    labeled_entry("Bio:", bio_var)
    labeled_entry("Role:", role_var)
    labeled_entry("Graduation Year:", grad_var)
    labeled_entry("Major:", major_var)

    # Change profile picture
    def choose_picture():
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            pic_var.set(file_path)
            for widget in profile_pic_frame.winfo_children():
                widget.destroy()
            new_frame = create_profile_picture_frame(edit_win, user_email, file_path)
            new_frame.pack()

    tk.Button(edit_win, text="Change Profile Picture", command=choose_picture).pack(pady=5)

    # Save changes
    def save_profile():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET name=?, bio=?, role=?, grad_year=?, major=?, profile_picture=?
                WHERE email=?
            """, (
                name_var.get(),
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
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {e}")

    tk.Button(edit_win, text="Save Changes", bg="#4CAF50", fg="white", width=20, command=save_profile).pack(pady=10)
    tk.Button(edit_win, text="Cancel", bg="#f44336", fg="white", width=20, command=edit_win.destroy).pack(pady=5)
