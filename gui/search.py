# gui/search.py
import tkinter as tk
from tkinter import messagebox
from database.db import get_db_connection

def search_students(root, user_email):
    from gui.dashboard import clear_window, show_user_dashboard

    clear_window(root)
    root.title("Search Students")

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="Search for Students", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(main_frame, text="Enter student name:").grid(row=1, column=0, sticky="w", pady=5)
    search_entry = tk.Entry(main_frame, width=30)
    search_entry.grid(row=1, column=1, pady=5)

    results_frame = tk.Frame(main_frame)
    results_frame.grid(row=3, column=0, columnspan=2, pady=10)

    def perform_search():
        for widget in results_frame.winfo_children():
            widget.destroy()

        search_term = search_entry.get().strip()
        if not search_term:
            messagebox.showerror("Error", "Please enter a name to search.")
            return

        conn = get_db_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, email, bio FROM users WHERE name LIKE ? AND email != ?", (f"%{search_term}%", user_email))
            results = cursor.fetchall()

            if not results:
                tk.Label(results_frame, text="No students found.", fg="gray").pack()
                return

            for i, (name, email, bio) in enumerate(results, start=1):
                tk.Label(results_frame, text=f"{i}. {name}", font=("Arial", 12, "bold")).pack(anchor="w")
                tk.Label(results_frame, text=f"📧 {email}", fg="blue").pack(anchor="w")
                if bio:
                    tk.Label(results_frame, text=f"📝 {bio}", fg="gray").pack(anchor="w")
                tk.Label(results_frame, text="").pack()

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    tk.Button(main_frame, text="Search", width=15, command=perform_search).grid(row=2, column=0, columnspan=2, pady=10)
    tk.Button(main_frame, text="Back to Dashboard", width=20, command=lambda: show_user_dashboard(root, user_email, None)).grid(row=4, column=0, columnspan=2, pady=5)
