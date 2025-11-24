# main.py
import tkinter as tk
from database.db import setup_database, update_database_schema
from gui.login import show_login_screen
import os

# Ensure data and assets folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("assets/images", exist_ok=True)

def main():
    setup_database()
    update_database_schema()

    root = tk.Tk()
    root.geometry("450x350")
    
    root.resizable(True, True)
    show_login_screen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
