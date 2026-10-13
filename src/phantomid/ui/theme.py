import tkinter as tk
from tkinter import ttk

COLORS = {
    "background": "#EDF2F6",
    "surface": "#FFFFFF",
    "sidebar": "#193449",
    "text": "#203B4C",
    "muted": "#526A7A",
    "accent": "#087E83",
    "soft": "#E1F2F1",
    "border": "#D4DFE6",
}


def configure(root):
    root.configure(bg=COLORS["background"])
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=COLORS["background"])
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure(
        "TLabel",
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=("Segoe UI", 11),
    )
    style.configure("TButton", font=("Segoe UI", 11), padding=(16, 10))
    style.configure(
        "Accent.TButton", background=COLORS["accent"], foreground="white", borderwidth=0
    )
    style.map(
        "Accent.TButton",
        background=[("active", "#06666B")],
        foreground=[("active", "white")],
    )
    style.configure("TEntry", padding=9, font=("Segoe UI", 11))
    style.configure(
        "Treeview",
        font=("Segoe UI", 11),
        rowheight=36,
        background="white",
        fieldbackground="white",
        foreground=COLORS["text"],
    )
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=8)


def label(parent, text, size=11, color=None, bold=False, background=None, **kwargs):
    return tk.Label(
        parent,
        text=text,
        font=("Segoe UI", size, "bold" if bold else "normal"),
        fg=color or COLORS["text"],
        bg=background or parent.cget("bg"),
        anchor="w",
        justify="left",
        **kwargs,
    )
