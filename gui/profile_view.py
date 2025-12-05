import tkinter as tk
from tkinter import messagebox
from database.db import get_user_data
from gui.widgets.profile_picture import create_profile_picture_frame
from gui.theme_manager import apply_theme  


def show_user_profile(root, user_email):
    """Display the user's profile information."""
    from gui.dashboard import clear_window, show_user_dashboard
    from gui.profile_edit import edit_profile  # imported here to avoid circular imports

    clear_window(root)
    root.title("My Profile")

    user_data = get_user_data(user_email)
    if not user_data:
        messagebox.showerror("Error", "Profile data not found.")
        show_user_dashboard(root, user_email, None)
        return

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    # Apply theme to this frame immediately
    apply_theme(main_frame)

    # Profile Picture Section
    profile_pic_frame = create_profile_picture_frame(
        main_frame,
        user_email,
        user_data.get("profile_picture")
    )
    profile_pic_frame.pack(pady=10)

    tk.Label(main_frame, text=user_data.get('name', 'User'),
             font=("Arial", 18, "bold")).pack(pady=10)

    tk.Button(
        main_frame,
        text="↻",
        font=("Arial", 20, "bold"),
        width=30,
        bd=0,
        command=lambda: show_user_profile(root, user_email)
    ).pack(pady=10)

    tk.Label(main_frame, text=f"Name: {user_data.get('name', 'N/A')}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text=f"Email: {user_data.get('email', 'N/A')}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text=f"Role: {user_data.get('role', 'user').capitalize()}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text=f"Graduation Year: {user_data.get('grad_year', 'N/A')}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text=f"Major: {user_data.get('major', 'user')}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text=f"Bio: {user_data.get('bio', 'No bio provided')}").pack(anchor="w", pady=2)

    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(pady=15)

    # Remove hardcoded colors — let theme handle it
    tk.Button(
        btn_frame,
        text="Edit Profile",
        width=20,
        command=lambda: edit_profile(root, user_email)
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Back to Dashboard",
        width=20,
        command=lambda: show_user_dashboard(root, user_email, user_data.get('id'))
    ).pack(side="left", padx=5)

    # Apply theme again so new buttons/labels also get styled
    apply_theme(main_frame)
