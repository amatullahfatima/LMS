# gui/private_messages.py
import sqlite3
from tkinter import Tk, Label, Button, Entry, Text, END, Listbox, Scrollbar
from tkinter import messagebox
from datetime import datetime
import os

# -------------------- Database Setup --------------------
DB_NAME = os.path.join("data", "social_media.db")

def get_db_connection():
    """Connect to SQLite database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to connect: {e}")
        return None

def setup_messages_table():
    """Create messages table if it does not exist"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_email TEXT NOT NULL,
                    receiver_email TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
            """)
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to setup messages table: {e}")
        finally:
            conn.close()

# -------------------- Message Functions --------------------

def send_private_message(sender_email, receiver_email, message_text):
    """Insert a new message into the database"""
    if not sender_email or not receiver_email or not message_text:
        return False
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (sender_email, receiver_email, message_text, timestamp)
                VALUES (?, ?, ?, ?)
            """, (sender_email, receiver_email, message_text, datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to send message: {e}")
            return False
        finally:
            conn.close()
    return False

def get_inbox(user_email):
    """Retrieve all messages sent to a user"""
    conn = get_db_connection()
    messages = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sender_email, message_text, timestamp
                FROM messages
                WHERE receiver_email = ?
                ORDER BY timestamp DESC
            """, (user_email,))
            messages = cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve inbox: {e}")
        finally:
            conn.close()
    return messages

# -------------------- Tkinter GUI --------------------

class PrivateMessageApp:
    def __init__(self, master):
        self.master = master
        master.title("Private Messages")
        master.geometry("600x500")

        self.sender_label = Label(master, text="Your Email:")
        self.sender_label.pack()
        self.sender_entry = Entry(master, width=50)
        self.sender_entry.pack()

        self.receiver_label = Label(master, text="Recipient Email:")
        self.receiver_label.pack()
        self.receiver_entry = Entry(master, width=50)
        self.receiver_entry.pack()

        self.message_label = Label(master, text="Message:")
        self.message_label.pack()
        self.message_text = Text(master, width=60, height=5)
        self.message_text.pack()

        self.send_button = Button(master, text="Send Message", command=self.send_message)
        self.send_button.pack(pady=5)

        self.inbox_label = Label(master, text="Inbox:")
        self.inbox_label.pack()

        self.scrollbar = Scrollbar(master)
        self.scrollbar.pack(side="right", fill="y")

        self.inbox_listbox = Listbox(master, width=80, height=15, yscrollcommand=self.scrollbar.set)
        self.inbox_listbox.pack()
        self.scrollbar.config(command=self.inbox_listbox.yview)

        self.refresh_button = Button(master, text="Refresh Inbox", command=self.load_inbox)
        self.refresh_button.pack(pady=5)

    def send_message(self):
        sender = self.sender_entry.get().strip()
        receiver = self.receiver_entry.get().strip()
        text = self.message_text.get("1.0", END).strip()
        if send_private_message(sender, receiver, text):
            messagebox.showinfo("Success", "Message sent successfully!")
            self.message_text.delete("1.0", END)
            self.load_inbox()
        else:
            messagebox.showerror("Error", "Failed to send message.")

    def load_inbox(self):
        self.inbox_listbox.delete(0, END)
        user_email = self.sender_entry.get().strip()
        messages = get_inbox(user_email)
        for msg in messages:
            display_text = f"From: {msg['sender_email']} | {msg['timestamp']}\n{msg['message_text']}"
            self.inbox_listbox.insert(END, display_text)
            self.inbox_listbox.insert(END, "-"*60)

# -------------------- Main --------------------
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    setup_messages_table()
    root = Tk()
    app = PrivateMessageApp(root)
    root.mainloop()
