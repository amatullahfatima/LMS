
# theme_manager.py

current_theme = "light"

themes = {
    "light": {
        "bg": "#FFFFFF",
        "fg": "#000000",
        "button_bg": "#E0E0E0",
        "button_fg": "#000000",
        "entry_bg": "#FFFFFF",
        "entry_fg": "#000000",
    },
    "dark": {
        "bg": "#1E1E1E",
        "fg": "#FFFFFF",
        "button_bg": "#333333",
        "button_fg": "#FFFFFF",
        "entry_bg": "#2A2A2A",
        "entry_fg": "#FFFFFF",
    }
}


def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"


def apply_theme(widget):
    """ Recursively apply theme to widget & all children """
    theme = themes[current_theme]

    # Window or Frame background
    try:
        widget.configure(bg=theme["bg"])
    except:
        pass

    # Check widget type and update attributes
    widget_type = widget.winfo_class()

    # Buttons
    if widget_type == "Button":
        try:
            widget.configure(bg=theme["button_bg"],
                             fg=theme["button_fg"],
                             activebackground=theme["button_bg"],
                             activeforeground=theme["button_fg"])
        except:
            pass

    # Labels
    if widget_type == "Label":
        try:
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        except:
            pass

    # Entry widgets
    if widget_type == "Entry":
        try:
            widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"],
                             insertbackground=theme["entry_fg"])
        except:
            pass

    # Text widgets
    if widget_type == "Text":
        try:
            widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"])
        except:
            pass

    # Apply theme to ALL children
    for child in widget.winfo_children():
        apply_theme(child)