# gui/private_messages.py
from database.db import get_db_connection
from datetime import datetime
from tkinter import messagebox

TIME_FORMAT = "%m/%d/%Y at %H:%M"

# ------------------- DATABASE SETUP -------------------

def setup_messages_table():
    """
    Create the private_messages table if it doesn't exist.
    """
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS private_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_email TEXT NOT NULL,
                receiver_email TEXT NOT NULL,
                message_text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                FOREIGN KEY(sender_email) REFERENCES users(email),
                FOREIGN KEY(receiver_email) REFERENCES users(email)
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating private_messages table: {e}")
        messagebox.showerror("Database Error", f"Failed to setup messages table: {e}")
    finally:
        conn.close()


# ------------------- MESSAGE FUNCTIONS -------------------

def send_private_message(sender_email, receiver_email, message_text):
    """
    Send a private message from sender to receiver.
    """
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        ts = datetime.now().strftime(TIME_FORMAT)
        cursor.execute("""
            INSERT INTO private_messages (sender_email, receiver_email, message_text, timestamp)
            VALUES (?, ?, ?, ?)
        """, (sender_email, receiver_email, message_text, ts))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        messagebox.showerror("Message Error", f"Failed to send message: {e}")
        return False
    finally:
        conn.close()


def get_inbox(receiver_email):
    """
    Retrieve all messages received by a user, newest first.
    """
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sender_email, message_text, timestamp, is_read
            FROM private_messages
            WHERE receiver_email = ?
            ORDER BY timestamp DESC
        """, (receiver_email,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving inbox: {e}")
        return []
    finally:
        conn.close()


def get_sent_messages(sender_email):
    """
    Retrieve all messages sent by a user, newest first.
    """
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT receiver_email, message_text, timestamp
            FROM private_messages
            WHERE sender_email = ?
            ORDER BY timestamp DESC
        """, (sender_email,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving sent messages: {e}")
        return []
    finally:
        conn.close()


def mark_message_as_read(message_id):
    """
    Mark a message as read.
    """
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE private_messages SET is_read = 1 WHERE id = ?", (message_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error marking message as read: {e}")
        return False
    finally:
        conn.close()


# ------------------- INITIALIZE -------------------

if __name__ == "__main__":
    setup_messages_table()
    print("Private messages table is ready.")
