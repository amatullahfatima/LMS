import tkinter as tk
from gui.theme_manager import apply_theme
from gui.changePassword import change_password   # your existing one
from gui.update_email import open_update_email_window         # we will create next


def open_settings(root, user_email):
    """Open the settings window (email + password update)."""

    from gui.dashboard import clear_window, show_user_dashboard

    clear_window(root)
    root.title("Settings")

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill="both")

    # Apply theme
    apply_theme(main_frame)

    tk.Label(main_frame, text="⚙ Settings", font=("Arial", 20, "bold")).pack(pady=15)

    # ---- Update Email ----
    tk.Button(
        main_frame,
        text="Update Email",
        width=25,
        command=lambda: open_update_email_window(root, user_email)
    ).pack(pady=8)

    # ---- Change Password ----
    tk.Button(
        main_frame,
        text="Change Password",
        width=25,
        command=lambda: change_password(user_email)
    ).pack(pady=8)

    # ---- Back Button ----
    tk.Button(
        main_frame,
        text="Back to Dashboard",
        width=25,
        command=lambda: show_user_dashboard(root, user_email, None)
    ).pack(pady=20)

    # Apply theme again after widgets added
    apply_theme(main_frame)
