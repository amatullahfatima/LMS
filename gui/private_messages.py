# gui/private_messages.py
import sqlite3
from tkinter import (
    Toplevel, Tk, Label, Button, Entry, Text, END, Listbox,
    Scrollbar, messagebox, Frame
)
from datetime import datetime
import os

# -------------------- Database Setup --------------------
DB_NAME = os.path.join("data", "social_media.db")

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to connect: {e}")
        return None

def setup_messages_table():
    """Create messages table if missing and add is_read column if missing"""
    os.makedirs("data", exist_ok=True)
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Add is_read column if it doesn't exist
            try:
                cursor.execute("SELECT is_read FROM messages LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE messages ADD COLUMN is_read INTEGER DEFAULT 0;")

            # Create table if missing
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_email TEXT NOT NULL,
                    receiver_email TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0
                );
            """)
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to setup messages table: {e}")
        finally:
            conn.close()

# -------------------- Core Message Functions --------------------
def send_private_message(sender_email, receiver_email, message_text):
    if not sender_email or not receiver_email or not message_text:
        return False
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (sender_email, receiver_email, message_text, timestamp, is_read)
                VALUES (?, ?, ?, ?, 0)
            """, (
                sender_email,
                receiver_email,
                message_text,
                datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to send message: {e}")
            return False
        finally:
            conn.close()
    return False

def get_inbox(user_email):
    conn = get_db_connection()
    messages = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, sender_email, message_text, timestamp, is_read
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

def mark_as_read(message_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (message_id,))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to mark message as read: {e}")
        finally:
            conn.close()

# -------------------- GUI Class --------------------
class PrivateMessageApp:
    def __init__(self, master, user_email, receiver_email=None, refresh_interval=5000):
        """Initialize the messaging UI."""
        self.master = master
        self.user_email = user_email
        self.refresh_interval = refresh_interval

        master.title("Private Messages")
        master.geometry("650x550")

        # ---------- Sender ----------
        Label(master, text="Your Email:").pack()
        self.sender_entry = Entry(master, width=50)
        self.sender_entry.pack()
        self.sender_entry.insert(0, user_email)
        self.sender_entry.config(state="readonly")

        # ---------- Recipient ----------
        Label(master, text="Recipient Email:").pack()
        self.receiver_entry = Entry(master, width=50)
        self.receiver_entry.pack()
        if receiver_email:
            self.receiver_entry.insert(0, receiver_email)

        # ---------- Message Box ----------
        Label(master, text="Message:").pack()
        self.message_text = Text(master, width=70, height=5)
        self.message_text.pack()

        Button(master, text="Send Message", command=self.send_message).pack(pady=5)

        # ---------- Inbox ----------
        Label(master, text="Inbox:", font=("Arial", 12, "bold")).pack(pady=10)
        list_frame = Frame(master)
        list_frame.pack()

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.inbox_listbox = Listbox(list_frame, width=85, height=15, yscrollcommand=scrollbar.set)
        self.inbox_listbox.pack()
        scrollbar.config(command=self.inbox_listbox.yview)

        Button(master, text="Refresh Inbox", command=self.load_inbox).pack(pady=5)

        # Start auto-refresh
        self.load_inbox()
        self.master.after(self.refresh_interval, self.auto_refresh_inbox)

    # -------------------- Button Functions --------------------
    def send_message(self):
        sender = self.sender_entry.get().strip()
        receiver = self.receiver_entry.get().strip()
        message = self.message_text.get("1.0", END).strip()

        if send_private_message(sender, receiver, message):
            messagebox.showinfo("Success", "Message sent!")
            self.message_text.delete("1.0", END)
            self.load_inbox()
        else:
            messagebox.showerror("Error", "Failed to send message.")

    def load_inbox(self):
        self.inbox_listbox.delete(0, END)
        messages = get_inbox(self.user_email)
        if not messages:
            self.inbox_listbox.insert(END, "No messages.")
            return
        for msg in messages:
            display = f"From: {msg['sender_email']} | {msg['timestamp']}\n{msg['message_text']}"
            if msg['is_read'] == 0:
                self.inbox_listbox.insert(END, display)
                self.inbox_listbox.itemconfig(END, {'bg':'lightyellow'})  # Highlight unread
            else:
                self.inbox_listbox.insert(END, display)
            self.inbox_listbox.insert(END, "-" * 70)
            mark_as_read(msg['id'])  # Mark as read after displaying

    def auto_refresh_inbox(self):
        """Automatically refresh inbox every few seconds."""
        self.load_inbox()
        self.master.after(self.refresh_interval, self.auto_refresh_inbox)

# -------------------- Helper Function --------------------
def open_private_messages(root, user_email, receiver_email=None):
    setup_messages_table()
    msg_win = Toplevel(root)
    PrivateMessageApp(msg_win, user_email, receiver_email)

# -------------------- Standalone Mode --------------------
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    setup_messages_table()
    root = Tk()
    PrivateMessageApp(root, "test@example.com")
    root.mainloop()
