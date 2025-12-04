import sqlite3
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

# --- Configuration for Email Sending (Placeholders) ---
# NOTE: Replace these with actual details to send real emails.
SMTP_SERVER = "daniellenana400@gmail.com" 
SMTP_PORT = 587 
SENDER_EMAIL = "notifications@socialapp.com"
SENDER_PASSWORD = "YOUR_SECURE_APP_PASSWORD" 
DB_FILE = "social_media_full.db"
TIME_FORMAT = "%m/%d/%Y at %H:%M"


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn       

def setup_database():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            commenter_id INTEGER NOT NULL, -- The user who commented
            comment_text TEXT NOT NULL,
            commented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY (commenter_id) REFERENCES users(id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS post_reactions (
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            reaction_type TEXT NOT NULL CHECK(reaction_type IN ('like','dislike')),
            reacted_at TEXT NOT NULL,
            liker_id INTEGER NOT NULL, -- The user who performed the like
            liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, liker_id),
            PRIMARY KEY (post_id, user_id),
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    # Likes table (records who liked which post)
    c.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        post_id INTEGER NOT NULL,
        liker_id INTEGER NOT NULL, -- The user who performed the like
        liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(post_id, liker_id), 
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (liker_id) REFERENCES users(id)
    );
    """)
    
    # Follows table (records user-to-user follows)
    c.execute("""
    CREATE TABLE IF NOT EXISTS follows (
        follower_id INTEGER NOT NULL, -- The user who initiated the follow
        followed_id INTEGER NOT NULL, -- The user being followed (the recipient of the notification)
        followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(follower_id, followed_id), 
        FOREIGN KEY (follower_id) REFERENCES users(id),
        FOREIGN KEY (followed_id) REFERENCES users(id)
    );
    """)
    
    conn.commit()
    conn.close()

def get_user_data(conn, user_id):
    """Retrieves user name and email given their ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def get_post_owner_data(conn, post_id):
    """Retrieves the owner's ID and post content for a given post."""
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, content FROM posts WHERE id = ?", (post_id,))
    return cursor.fetchone()

def send_like_notification_email(recipient_email, post_owner_name, liker_name, post_preview):
    """
    Sends a simulated email notification about a post like.
    
    This simulation prints the email content to the console instead of connecting 
    to an actual SMTP server.
    """
    subject = f"🥳 Your post was liked by {liker_name}!"
    body = f"""
Dear {post_owner_name},

This is an automatic notification to let you know that {liker_name} just liked one of your posts on {datetime.now().strftime("%Y-%m-%d")}.

Post Snippet: "{post_preview[:50]}..."
You can log in to see the details.

Thanks,
The Social App Team
"""
def send_comment_notification_email(recipient_email, post_owner_name, commenter_name, comment_text, post_preview):
    """Constructs and sends a notification email about a new comment."""
    subject = f"💬 New comment from {commenter_name} on your post!"
    body = f"""
Dear {post_owner_name},

{commenter_name} commented on your post on {datetime.now().strftime("%Y-%m-%d")}.

Original Post: "{post_preview[:50]}..."
Comment: "{comment_text[:80]}..."

Action: View and reply to the comment!

Thanks,
The Social App Team
"""
    return send_simulated_email(recipient_email, subject, body, post_owner_name)

def send_follow_notification_email(recipient_email, followed_user_name, follower_name):
    """Constructs and sends a notification email about a new follower."""
    subject = f"🚶 New follower: {follower_name} is now following you!"
    body = f"""
Dear {followed_user_name},

Great news! {follower_name} just started following you on {datetime.now().strftime("%Y-%m-%d")}.

Check out their profile and follow them back to see their latest posts!

Action: Visit {follower_name}'s profile.

Thanks,
The Social App Team
"""
    return send_simulated_email(recipient_email, subject, body, followed_user_name)
    
    if SENDER_PASSWORD == "YOUR_SECURE_APP_PASSWORD":
        print(f"\n--- SIMULATED EMAIL SENT ---")
        print(f"To: {recipient_email} ({post_owner_name})")
        print(f"Subject: {subject}")
        print(f"Body:\n{body.strip()}")
        print(f"--------------------------")
        return True
    
    # Real SMTP logic would go here
    # ...
    return False

def process_post_like_comment_follow(post_id, liker_user_id, commenter_id, comment_text, follower_id, followed_id):
    """
    Core function: records the like, records the comment, validates, and sends the email notification.
    The followed_id is the recipient of the notification.
    """
    conn = get_conn()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()
        
        # 1. Record the follow (will raise IntegrityError if duplicate)
        try:
            cursor.execute(
                "INSERT INTO follows (follower_id, followed_id) VALUES (?, ?)",
                (follower_id, followed_id)
            )
            conn.commit()
            print(f"Follow recorded: User {follower_id} is now following User {followed_id}.")
        except sqlite3.IntegrityError:
            print(f"User {follower_id} already follows user {followed_id}. No action needed.")
            return True
        # 2. Record the comment
        try:
            cursor.execute(
                "INSERT INTO comments (post_id, commenter_id, comment_text) VALUES (?, ?, ?)",
                (post_id, commenter_id, comment_text)
            )
            conn.commit()
            print(f"Comment recorded on Post {post_id} by Commenter {commenter_id}.")
        except sqlite3.Error as e:
            print(f"An unexpected database error occurred during commenting: {e}")
            return False
        
        # 3. Record the like (will raise IntegrityError if duplicate)
        try:
            # Assumes the application calls this function only when a like occurs
            cursor.execute(
                "INSERT INTO likes (post_id, liker_id) VALUES (?, ?)", 
                (post_id, liker_user_id)
            )
            conn.commit()
            print(f"Like recorded: Post {post_id} by Liker {liker_user_id}.")
            
        except sqlite3.IntegrityError:
            print(f"Liker {liker_user_id} already liked post {post_id}. No action needed.")
            return True 

        # 3. Retrieve necessary data
        post_row = get_post_owner_data(conn, post_id)
        if not post_row:
            print(f"ERROR: Post {post_id} not found.")
            return False
            
        post_owner_id = post_row['user_id']
        post_content = post_row['content']
        
        # Suppress notification if user likes their own post
        if post_owner_id == liker_user_id:
            print("Self-like detected. Email notification suppressed.")
            return True
            
        # Get recipient and liker details
        owner_data = get_user_data(conn, post_owner_id)
        liker_data = get_user_data(conn, liker_user_id)
        
        if not owner_data or not liker_data:
            print("ERROR: Could not retrieve user data for notification.")
            return False
            
        # Suppress notification if user comments on their own post
        if post_owner_id == commenter_id:
            print("Self-comment detected. Email notification suppressed.")
            return True

        # Get recipient and commenter details
        owner_data = get_user_data(conn, post_owner_id)
        commenter_data = get_user_data(conn, commenter_id)

        if not owner_data or not commenter_data:
            print("ERROR: Could not retrieve user data for comment notification.")
            return False
            
        # Suppress notification if user follows themselves
        if follower_id == followed_id:
            print("Self-follow detected. Email notification suppressed.")
            return True

        # Get recipient (followed user) and follower details
        followed_data = get_user_data(conn, followed_id)
        follower_data = get_user_data(conn, follower_id)

        if not followed_data or not follower_data:
            print("ERROR: Could not retrieve user data for follow notification.")
            return False
            
        # 3. Send Notification
        send_email_notification(
            recipient_email=owner_data['email'],
            post_owner_name=owner_data['name'],
            liker_name=liker_data['name'],
            post_preview=post_content
        )
        
        return True
        
        send_comment_notification_email(
            recipient_email=owner_data['email'],
            post_owner_name=owner_data['name'],
            commenter_name=commenter_data['name'],
            comment_text=comment_text,
            post_preview=post_content
        )
        
        return True
        
        send_follow_notification_email(
            recipient_email=followed_data['email'],
            followed_user_name=followed_data['name'],
            follower_name=follower_data['name']
        )
        
        return True
        
    except sqlite3.Error as e:
        print(f"An unexpected database error occurred: {e}")
        print(f"An unexpected database error occurred during commenting: {e}")
        print(f"An unexpected database error occurred during following: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- DEMONSTRATION / MOCK DATA ---

def populate_mock_data(conn):
    """Inserts mock users and posts for demonstration."""
    cursor = conn.cursor()
    
    # User IDs: 1 (Alice - Post Owner/Followed), 2 (Bob - Liker/Commenter/Follower), 3 (Charlie - Commenter), 4 (David - Follower)
    users = [
        (1, 'Alice', 'alice.owner@socialapp.com'),
        (2, 'Bob', 'bob.interactor@socialapp.com'),
        (3, 'Charlie', 'charlie.other@socialapp.com'),
        (4, 'David', 'david.follower@socialapp.com'),
    ]
    cursor.executemany("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", users)

    # Post 101 by Alice
    posts = [
        (101, 1, 'Having a great day climbing mountains! #outdoors #adventure'),
    ]
    cursor.executemany("INSERT OR IGNORE INTO posts (id, user_id, content) VALUES (?, ?, ?)", posts)
    
    conn.commit()
    
if __name__ == "__main__":
    # Clean up and setup database
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = get_conn()
    if conn:
        setup_database()
        populate_mock_data(conn)
        conn.close()

    POST_ID = 101 # Alice's Post
    ALICE_ID = 1  # Alice (Owner, Followed)
    BOB_ID = 2    # Bob (Liker/Commenter/Follower)
    CHARLIE_ID = 3 # Charlie (Commenter)
    DAVID_ID = 4   # David (Follower)

    print("--- Starting Social Notification Service Test ---")

      
    # --- LIKE TEST (Existing functionality) ---
    print("\n[TEST 1: Bob (ID 2) likes Alice's post (ID 1)]")
    process_post_like_comment_follow(BOB_ID, ALICE_ID, BOB_ID, ALICE_ID, DAVID_ID, ALICE_ID)

    # --- COMMENT TEST (New functionality) ---
    print("\n[TEST 2: Charlie (ID 3) comments on Alice's post (ID 1)]")
    process_post_like_comment_follow(
        post_id=POST_ID, 
        commenter_id=CHARLIE_ID, 
        comment_text="Wow, that looks amazing! What trail are you on?",
        liker_user_id=ALICE_ID,
        follower_id=DAVID_ID, 
        followed_id=ALICE_ID
    )
    
    # --- SELF-COMMENT TEST (Suppressed notification) ---
    print("\n[TEST 3: Alice (ID 1) comments on her own post (Self-Comment)]")
    process_post_like_comment_follow(
        post_id=POST_ID, 
        commenter_id=ALICE_ID, 
        comment_text="I should add that this is the Eagle Peak Trail.",
        liker_user_id=ALICE_ID,
        follower_id=DAVID_ID, 
        followed_id=ALICE_ID
    )
      
    # --- FOLLOW INTERACTION TESTS ---
    print("\n--- Testing Follow Interactions ---")
    
    print("\n[TEST 3: David (ID 4) follows Alice (ID 1)]")
    process_post_like_comment_follow(
        post_id=POST_ID, 
        commenter_id=CHARLIE_ID, 
        comment_text="Are you OK?",
        liker_user_id=ALICE_ID,
        follower_id=DAVID_ID, 
        followed_id=ALICE_ID
    )
    
    print("\n[TEST 4: David (ID 4) tries to follow Alice (ID 1) again (Duplicate)]")
    process_post_like_comment_follow(
    post_id=POST_ID, 
        commenter_id=CHARLIE_ID, 
        comment_text="I like today weather",
        liker_user_id=ALICE_ID,
        follower_id=DAVID_ID, 
        followed_id=ALICE_ID
    )
    
    print("\n[TEST 5: Bob (ID 2) follows himself (Self-Follow)]")
    process_post_like_comment_follow(
    post_id=POST_ID, 
        commenter_id=CHARLIE_ID, 
        comment_text="I am planning a big party for my graduation",
        liker_user_id=ALICE_ID,
        follower_id=BOB_ID, 
        followed_id=BOB_ID
    )
    
    print("\n--- Testing Complete ---")

    
