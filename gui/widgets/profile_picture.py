import os, time, shutil
from tkinter import filedialog, messagebox, Frame, Canvas, Button
from PIL import Image, ImageTk, ImageDraw
from database.db import update_profile_picture_in_db

ASSETS_IMAGES_DIR = os.path.join("assets", "images")
os.makedirs(ASSETS_IMAGES_DIR, exist_ok=True)

def make_circle_image(img_path, size=140):
    """Return circular PhotoImage from given path."""
    try:
        img = Image.open(img_path).convert("RGBA")
        img.thumbnail((size, size))
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
        img.putalpha(mask)
        return ImageTk.PhotoImage(img)
    except Exception:
        blank = Image.new("RGBA", (size, size), (220, 220, 220, 255))
        return ImageTk.PhotoImage(blank)

def create_profile_picture_frame(parent, user_email, pic_path=None, editable=True):
    """Create a profile picture frame with optional edit/remove buttons."""
    frame = Frame(parent, width=140, height=140)
    frame.pack_propagate(False)
    frame.grid_propagate(False)

    canvas = Canvas(frame, width=140, height=140, highlightthickness=0)
    canvas.place(x=0, y=0)

    def display(path):
        photo = make_circle_image(path)
        canvas.image = photo
        canvas.create_image(70, 70, image=photo)

    # Initial display
    if pic_path and os.path.exists(pic_path):
        display(pic_path)
    else:
        display(None)

    # --- Action Functions ---
    def upload_image():
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if not file_path:
            return

        try:
            basename = os.path.basename(file_path)
            timestamp = int(time.time())
            dest_path = os.path.join(ASSETS_IMAGES_DIR, f"{timestamp}_{basename}")
            shutil.copy2(file_path, dest_path)
            update_profile_picture_in_db(user_email, dest_path)
            display(dest_path)
            messagebox.showinfo("Updated", "Profile picture updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload image: {e}")

    def remove_image():
        update_profile_picture_in_db(user_email, None)
        display(None)
        messagebox.showinfo("Removed", "Profile picture removed successfully!")

    # --- Buttons ---
    if editable:
        edit_btn = Button(frame, text="🖋️", font=("Arial", 12), bd=0, bg="#ffffff", command=upload_image)
        remove_btn = Button(frame, text="❌", font=("Arial", 12), bd=0, bg="#ffffff", command=remove_image)
        edit_btn.place(x=110, y=5)
        remove_btn.place(x=110, y=35)

    return frame

