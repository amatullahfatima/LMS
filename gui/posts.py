import smtplib
# gui/posts.py
import tkinter as tk
from email.message import EmailMessage
from tkinter import messagebox, simpledialog

from gui.theme_manager import apply_theme  

from database.db import (
    create_post,
    fetch_posts,
    add_comment,
    get_comments,
    get_post_reaction,
    set_post_reaction,
    get_comment_count,
    get_reaction_summary
)
email = 'socialmediadallascollege@gmail.com'

#send a warning to user email inbox
def send_warning(Email, UserName, Content, DatePosted):
    print(f"Sending warning to {Email}:")
    print(f"DatePosted: {DatePosted}")
    print(f"UserName: {UserName}")
    print(f"Content: {Content}")
    sender_email = email
    receiver_email = Email
    password = 'hndp egcm bkrl itgy'  # Use an app password for security, not your main password
    msg = EmailMessage()
    msg['Subject'] = 'Dallas College , Social Media | Content Flagged'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"Att {UserName}:\nA report was submitted to the administrator\n"
                        f"posting flagged/reported: {Content}\n"
                        f"date posted: {DatePosted}\nplease review the content,"
                        f"correct any posting that violates the rules\nto avoid be banned"
                        f"from the app. Thanks ")
    try:
        # Connect to the SMTP server (e.g., Gmail's)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        messagebox.showinfo("Success!!!", "Email sent successfully")
    except Exception as e:
     messagebox.showerror("Error!!!", f" Error sending the email \n{e}")


def open_posts_window(user_email):
    post_win = tk.Toplevel()
    post_win.title("Student Posts")
    post_win.geometry("600x500")
    post_win.configure(bg="white")

    tk.Label(post_win, text="Feed", font=("Times New Roman", 15, "bold"), bg="gray").pack(pady=10)

    post_text = tk.Text(post_win, height=4, width=65, relief="solid", borderwidth=1)
    post_text.pack(pady=10)

    def share_post():
        content = post_text.get("1.0", "end").strip()
        if content:
            create_post(user_email, content)
            messagebox.showinfo("Success", "Post shared!")
            post_text.delete("1.0", "end")
            refresh_feed()
        else:
            messagebox.showwarning("Empty", "Please write something before posting.")

    tk.Button(post_win, text="Share Post", command=share_post, width=15, bg="#d9d9d9").pack(pady=5)

    feed_canvas = tk.Canvas(post_win, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(post_win, orient="vertical", command=feed_canvas.yview)
    feed_frame = tk.Frame(feed_canvas, bg="white")

    feed_canvas.create_window((0, 0), window=feed_frame, anchor="nw")
    feed_canvas.configure(yscrollcommand=scrollbar.set)

    feed_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ------------------------------------------------------------
    # MAIN FEED REFRESH
    # ------------------------------------------------------------
    def refresh_feed():
        for widget in feed_frame.winfo_children():
            widget.destroy()

        posts = fetch_posts()

        for p in posts:
            post_id = p[0]
            author_email = p[2]
            content = p[3]
            created_at = p[4]

            # Reaction summary
            likes, dislikes = get_reaction_summary(post_id)
            comments_count = get_comment_count(post_id)

            # UI Box
            post_box = tk.Frame(feed_frame, bd=1, relief="solid", padx=10, pady=5, bg="white")
            post_box.pack(fill="x", padx=20, pady=8)

            # Header
            tk.Label(post_box,
                     text=f"{author_email} ({created_at})",
                     font=("Arial", 10, "bold"),
                     bg="white").pack(anchor="w")

            # Content
            tk.Label(post_box,
                     text=content,
                     font=("Arial", 10),
                     bg="white",
                     wraplength=550,
                     justify="left").pack(anchor="w", pady=5)

            # Buttons row
            btn_frame = tk.Frame(post_box, bg="white")
            btn_frame.pack(anchor="w", pady=2)

            # --- LIKE BUTTON ---
            def like_post(pid=post_id):
                set_post_reaction(pid, user_email, "like")
                refresh_feed()

            tk.Button(btn_frame,
                      text=f"Like ({likes})",
                      width=10,
                      bg="#d9d9d9",
                      command=like_post).pack(side="left", padx=5)

            # --- DISLIKE BUTTON ---
            def dislike_post(pid=post_id):
                posts = fetch_posts()
                for p in posts:
                    if p[0] == pid:
                        postings = f"post ID : {p[0]}  - email :{p[1]} - User Name: {p[2]} - content: ({p[3]}) - posted : {p[4]}\n"
                        with open('flagged.txt', 'a') as file:
                         file.write(postings)
                    print(f"flagged:\n\t{p[0]}  -  {p[1]} -  {p[2]} -  ({p[3]}) - {p[4]}")
                    Email = p[1]
                    UserName = p[2]
                    Content = p[3]
                    DatePosted = p[4]
                set_post_reaction(pid, user_email, "dislike")
                refresh_feed()

                r = tk.messagebox.askyesno("Report", "Would you like to report or flagg this post?", icon="warning")
                if r:
                    send_warning(Email, UserName, Content, DatePosted)
                    print("Post was flagged")
            tk.Button(btn_frame,
                      text=f"Dislike ({dislikes})",
                      width=10,
                      bg="#d9d9d9",
                      command=dislike_post).pack(side="left", padx=5)

            # --- COMMENT BUTTON ---
            def comment_on_post(pid=post_id):
                comment = simpledialog.askstring("Add Comment", "Write your comment:")
                if comment:
                    add_comment(pid, user_email, comment)
                    refresh_feed()

            tk.Button(btn_frame,
                      text=f"Comment ({comments_count})",
                      width=12,
                      bg="#d9d9d9",
                      command=comment_on_post).pack(side="left", padx=5)

        feed_frame.update_idletasks()
        feed_canvas.config(scrollregion=feed_canvas.bbox("all"))

    refresh_feed()
    # Apply theme again so new buttons/labels also get styled
    apply_theme(post_win)





