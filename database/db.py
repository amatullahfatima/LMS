# database/db.py
import sqlite3
from tkinter import messagebox
from utils.security import hash_password, check_password
from datetime import datetime
import os

DB_NAME = os.path.join("data", "social_media.db")
ADMIN_USER = 'admin@dcccd.edu'
TIME_FORMAT = "%m/%d/%Y at %H:%M"
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        messagebox.showerror("Database Error", "Failed to connect to the database.")
        return None

def setup_database():
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT,
            bio TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            grad_year TEXT,
            major TEXT,
            profile_picture TEXT
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY(email) REFERENCES users(email)
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            comment_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(email) REFERENCES users(email)
        );

        CREATE TABLE IF NOT EXISTS post_reactions (
            post_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            reaction_type TEXT NOT NULL CHECK(reaction_type IN ('like','dislike')),
            reacted_at TEXT NOT NULL,
            PRIMARY KEY (post_id, email),
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(email) REFERENCES users(email)
        );
                             
            CREATE TABLE IF NOT EXISTS followers (
            follower_email TEXT NOT NULL,
            following_email TEXT NOT NULL,
            PRIMARY KEY (follower_email, following_email),
            FOREIGN KEY(follower_email) REFERENCES users(email),
            FOREIGN KEY(following_email) REFERENCES users(email)
        );

        """)
        admin_password_hash = hash_password('admin123')
        try:
            cursor.execute("INSERT INTO users (email, password_hash, name, role) VALUES (?, ?, ?, ?)",
                           (ADMIN_USER, admin_password_hash, 'Administrator', 'admin'))
            conn.commit()
            print("Default admin user created.")
        except sqlite3.IntegrityError:
            pass

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error during database setup: {e}")
    finally:
        conn.close()

# --- User CRUD and authentication helpers

def register_user_db(email, password, name):
    conn = get_db_connection()
    if conn is None:
        return False

    hashed_pw = hash_password(password)
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password_hash, name, bio, role) VALUES (?, ?, ?, ?, ?)",
                       (email, hashed_pw, name, f"New user {name}", 'user'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Registration Failed", "A user with this email already exists.")
        return False
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred during registration: {e}")
        return False
    finally:
        conn.close()

def verify_user_credentials(email, password):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user and check_password(user['password_hash'], password):
            return dict(user)
        return None
    except sqlite3.Error as e:
        print(f"Error verifying credentials: {e}")
        return None
    finally:
        conn.close()

def get_all_users():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email, name, role, created_at FROM users")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []
    finally:
        conn.close()

def get_user_data(email):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, bio, role, created_at, grad_year, major, profile_picture FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        return dict(user) if user else None
    except sqlite3.Error as e:
        print(f"Error retrieving user data: {e}")
        return None
    finally:
        conn.close()
    

def update_profile_picture_in_db(email: str, profile_picture_path: str) -> bool:
    """
    Stores the profile picture path for the given user email.
    Returns True on success, False on failure.
    """
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_picture = ? WHERE email = ?", (profile_picture_path, email))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating profile picture in DB: {e}")
        return False
    finally:
        conn.close()
def delete_user_db(email):
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting user: {e}")
        messagebox.showerror("Database Error", f"An error occurred while deleting user: {e}")
        return False
    finally:
        conn.close()


def update_database_schema():
    # columns already created in setup_database; function kept for compatibility
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()
def reset_password_db(email, new_password):
    """Handles password reset logic in database layer."""
    conn = get_db_connection()
    if conn is None:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return False, "No user found with that email."

        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))
        conn.commit()
        return True, "Password updated successfully! Please log in again."

    except sqlite3.Error as e:
        return False, f"Database Error: {e}"
    finally:
        conn.close()



# --- Posts and comments (original logic preserved)

def create_post(user_email, content):
    ts = datetime.now().strftime("%m/%d/%Y at %H:%M")
    conn = get_db_connection()
    if conn is None:
        return
    try:
        c = conn.cursor()
        c.execute("INSERT INTO posts (email, content, created_at) VALUES (?, ?, ?)", (user_email, content, ts))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating post: {e}")
    finally:
        conn.close()

def fetch_posts():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        c = conn.cursor()
        c.execute("""
            SELECT p.id, p.email, u.name, p.content, p.created_at
            FROM posts p
            JOIN users u ON p.email = u.email
            ORDER BY p.id DESC
        """)
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching posts: {e}")
        return []
    finally:
        conn.close()


def update_post(post_id: int, new_text: str) -> bool:
    """Update post content and updated_at timestamp."""
    updated_ts = datetime.now().strftime(TIME_FORMAT)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE posts SET content = ?, updated_at = ? WHERE id = ?",
                    (new_text, updated_ts, post_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def delete_post(post_id: int, user_email: str) -> bool:
    """
    Delete a post if it belongs to user_email.
    Also removes related comments and reactions.
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT email FROM posts WHERE id = ?", (post_id,))
        row = cur.fetchone()
        if not row or row["email"] != user_email:
            return False
        cur.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
        cur.execute("DELETE FROM post_reactions WHERE post_id = ?", (post_id,))
        cur.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        return True
    finally:
        conn.close()

# ---------------- Comments ----------------
def add_comment(post_id: int, user_email: str, comment_text: str) -> bool:
    """Insert a comment (stores email linking to users table)."""
    if not comment_text:
        return False
    ts = datetime.now().strftime(TIME_FORMAT)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Ensure post exists and user exists
        cur.execute("SELECT 1 FROM posts WHERE id = ?", (post_id,))
        if not cur.fetchone():
            return False
        cur.execute("SELECT 1 FROM users WHERE email = ?", (user_email,))
        if not cur.fetchone():
            return False
        cur.execute("INSERT INTO comments (post_id, email, comment_text, created_at) VALUES (?, ?, ?, ?)",
                    (post_id, user_email, comment_text, ts))
        conn.commit()
        return True
    finally:
        conn.close()

def get_comments(post_id: int):
    """Return comments for a post as list of rows with username/email and comment_text."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.comment_text, c.created_at, c.email, COALESCE(u.name, u.username, '') AS name
            FROM comments c
            LEFT JOIN users u ON c.email = u.email
            WHERE c.post_id = ?
            ORDER BY c.id ASC
        """, (post_id,))
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()

# ---------------- Reactions ----------------
def get_reaction_counts(post_id: int):
    """Return a dict {'like': n, 'dislike': m} for given post."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT reaction_type, COUNT(*) AS cnt
            FROM post_reactions
            WHERE post_id = ?
            GROUP BY reaction_type
        """, (post_id,))
        rows = cur.fetchall()
        counts = {'like': 0, 'dislike': 0}
        for r in rows:
            counts[r['reaction_type']] = r['cnt']
        return counts
    finally:
        conn.close()

def set_reaction(post_id: int, user_email: str, reaction_type: str):
    """
    Toggle or set reaction for (post_id, user_email). reaction_type in ('like','dislike').
    If same reaction exists => remove it (toggle off).
    If different reaction exists => update to the new one.
    """
    if reaction_type not in ('like', 'dislike'):
        return
    now = datetime.now().strftime(TIME_FORMAT)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT reaction_type FROM post_reactions WHERE post_id = ? AND email = ?",
                    (post_id, user_email))
        existing = cur.fetchone()
        if existing:
            if existing['reaction_type'] == reaction_type:
                # toggle off
                cur.execute("DELETE FROM post_reactions WHERE post_id = ? AND email = ?", (post_id, user_email))
            else:
                cur.execute("UPDATE post_reactions SET reaction_type = ?, reacted_at = ? WHERE post_id = ? AND email = ?",
                            (reaction_type, now, post_id, user_email))
        else:
            cur.execute("INSERT INTO post_reactions (post_id, email, reaction_type, reacted_at) VALUES (?, ?, ?, ?)",
                        (post_id, user_email, reaction_type, now))
        conn.commit()
    finally:
        conn.close()
def get_reaction_summary(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reaction_type, COUNT(*) FROM post_reactions WHERE post_id=? GROUP BY reaction_type",
                   (post_id,))
    rows = cursor.fetchall()
    conn.close()

    likes = 0
    dislikes = 0
    for r_type, count in rows:
        if r_type == "like":
            likes = count
        elif r_type == "dislike":
            dislikes = count
    return likes, dislikes


def get_post_reaction(post_id, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reaction_type FROM post_reactions WHERE post_id=? AND email=?",
                   (post_id, email))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def set_post_reaction(post_id, email, reaction):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO post_reactions (post_id, email, reaction_type, reacted_at)
        VALUES (?, ?, ?, datetime('now'))
        ON CONFLICT(post_id, email) DO UPDATE SET reaction_type=excluded.reaction_type
    """, (post_id, email, reaction))
    conn.commit()
    conn.close()


def get_comment_count(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM comments WHERE post_id=?", (post_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


# --------------------------- FOLLOW / UNFOLLOW ---------------------------

def follow_user(follower_email, following_email):
    if follower_email == following_email:
        return False
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO followers (follower_email, following_email) VALUES (?, ?)",
        (follower_email, following_email)
    )
    conn.commit()
    conn.close()
    return True

def unfollow_user(follower_email, following_email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM followers WHERE follower_email=? AND following_email=?",
        (follower_email, following_email)
    )
    conn.commit()
    conn.close()

def is_following(follower_email, following_email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM followers WHERE follower_email=? AND following_email=?",
        (follower_email, following_email)
    )
    row = cur.fetchone()
    conn.close()
    return row is not None

def count_followers(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM followers WHERE following_email=?", (email,))
    count = cur.fetchone()[0]
    conn.close()
    return count

def count_following(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM followers WHERE follower_email=?", (email,))
    count = cur.fetchone()[0]
    conn.close()
    return count