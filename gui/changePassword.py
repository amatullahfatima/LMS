import tkinter as tk
from tkinter import messagebox

from database.db import reset_password_db

def change_password(user_details):
    print(f"we are changing the password for: {user_details}")
    root = tk.Tk()
    root.title(f"Change Password...")
    root.geometry("280x300")
    tk.Label(root, text="Please enter your old password").grid(row=2, column=0)
    tk.Entry(root, width=10).grid(row=4, column=0)
    tk.Label(root, text="Please enter your new password").grid(row=6, column=0)
    tk.Entry(root, width=10).grid(row=8, column=0)
    tk.Label(root, text="Please re- enter your new password").grid(row=10, column=0)
    tk.Entry(root, width=10).grid(row=12, column=0)
    tk.Button(root, text="Close", command=lambda: root.destroy()).grid(row=13, column=0)

