import tkinter as tk
from tkinter import ttk

from .theme import COLORS, label


class Dashboard(tk.Frame):
    def __init__(self, parent, user, navigate, sign_out):
        super().__init__(parent, bg=COLORS["background"])
        self.user = user
        self.navigate = navigate
        self.sign_out = sign_out
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # Scrollable body
        canvas = tk.Canvas(self, bg=COLORS["background"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=2, sticky="ns")
        canvas.grid(row=0, column=1, sticky="nsew")
        self.body = tk.Frame(canvas, bg=COLORS["background"])
        self.canvas = canvas
        self.body_id = canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.body.pack(fill=tk.BOTH, expand=True)
        self.body.bind("<Configure>", lambda e: (canvas.configure(scrollregion=canvas.bbox("all")), self.resize_canvas()))
        self.bind("<Configure>", lambda e: self.resize_canvas())
        rail = tk.Frame(self, bg=COLORS["sidebar"], width=218)
        rail.grid(row=0, column=0, sticky="nsew")
        rail.pack_propagate(False)
        label(rail, "◈  PhantomID", 22, "white", True).pack(
            anchor="w", padx=24, pady=(30, 4)
        )
        label(rail, "Behavior, not content.", 10, "#BED2DF").pack(
            anchor="w", padx=24, pady=(0, 38)
        )
        self.nav_buttons = {}
        for title in (
            "Overview",
            "Users",
            "Event history",
            "Privacy",
            "Guest workspace",
        ):
            button = tk.Button(
                rail,
                text=title,
                command=lambda value=title: navigate(value),
                font=("Segoe UI", 11),
                anchor="w",
                padx=20,
                pady=12,
                fg="white",
                bg=COLORS["sidebar"],
                activebackground="#2C526B",
                activeforeground="white",
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                highlightcolor="#91D8DA",
                highlightthickness=1,
            )
            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[title] = button
        footer = tk.Frame(rail, bg=COLORS["sidebar"])
        footer.pack(side="bottom", fill="x", padx=24, pady=24)
        label(footer, user["username"], 12, "white", True).pack(anchor="w")
        label(
            footer,
            "Administrator" if user["role"] == "admin" else "Registered user",
            10,
            "#BED2DF",
        ).pack(anchor="w", pady=(4, 16))
        ttk.Button(footer, text="Sign out", command=sign_out).pack(fill="x")
        self.body = tk.Frame(self, bg=COLORS["background"])
        self.body.grid(row=0, column=1, sticky="nsew", padx=32, pady=28)

    def resize_canvas(self, event=None):
        # Option A: make body window fill available canvas width
        try:
            w = self.canvas.winfo_width() - 4
            h = self.canvas.winfo_height() - 4
            if w > 100 and h > 100:
                self.canvas.itemconfig(self.body_id, width=w, height=h)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except (tk.TclError, ValueError):
            pass

    def page(self, title, subtitle):
        for widget in self.body.winfo_children():
            widget.destroy()
        for name, button in self.nav_buttons.items():
            button.configure(bg="#2C526B" if name == title else COLORS["sidebar"])
        label(self.body, title, 28, bold=True).pack(anchor="w")
        label(self.body, subtitle, color=COLORS["muted"], wraplength=650).pack(
            anchor="w", pady=(8, 24)
        )

    def panel(self, title, description):
        panel = tk.Frame(
            self.body,
            bg="white",
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        panel.pack(fill="x", pady=(0, 16))
        label(panel, title, 17, bold=True).pack(anchor="w", padx=24, pady=(20, 8))
        label(panel, description, color=COLORS["muted"], wraplength=660).pack(
            anchor="w", padx=24, pady=(0, 18)
        )
        return panel

    def overview(self, consent, open_consent, demonstrate):
        self.page(
            "Overview",
            "Your session at a glance. Private by design, transparent by default.",
        )
        status = "Your behavioral session" if consent else "Your permission comes first"
        intro = self.panel(
            status,
            "Start monitoring below to learn your keyboard and pointer rhythm. Detection begins as soon as enough samples are available."
            if consent
            else "Review what PhantomID processes before enabling any behavioral collection.",
        )
        ttk.Button(
            intro,
            text="Review consent" if consent else "Review and consent",
            style="Accent.TButton",
            command=open_consent,
        ).pack(anchor="w", padx=24, pady=(0, 20))
        strip = tk.Frame(self.body, bg=COLORS["soft"])
        strip.pack(fill="x", pady=(0, 24))
        label(
            strip,
            "Local processing • No typed content or cursor paths retained",
            color="#075C60",
            background=COLORS["soft"],
            bold=True,
        ).pack(anchor="w", padx=20, pady=16)
        label(self.body, "Behavioral streams", 18, bold=True).pack(
            anchor="w", pady=(0, 12)
        )
        banner = tk.Frame(self.body, bg="#075C60")
        banner.pack(fill="x", pady=(0, 12))
        label(
            banner,
            "● Monitoring: green=active/amber=learning/gray=paused ● Pause/Start/Stats below ● Resize if needed",
            10,
            "white",
            True,
        ).pack(anchor="w", padx=12, pady=8)
        rows = tk.Frame(
            self.body,
            bg="white",
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        rows.pack(fill="x")
        for name, detail in (
            ("Keyboard", "Press intervals and dwell timing"),
            ("Pointer", "Movement rhythm and direction changes"),
            ("Scrolling", "Burst duration and intervals"),
            ("Interaction flow", "Content-free transition timing"),
        ):
            row = tk.Frame(rows, bg="white")
            row.pack(fill="x", padx=20, pady=9)
            label(row, name, bold=True, width=17).pack(side="left")
            label(row, detail, color=COLORS["muted"]).pack(side="left")
            label(
                row,
                "See session status"
                if name in {"Keyboard", "Pointer"}
                else "Not available yet",
                10,
                COLORS["muted"],
            ).pack(side="right")
        bottom = tk.Frame(self.body, bg=COLORS["background"])
        bottom.pack(fill="x", pady=24)
        label(
            bottom,
            "3 fresh anomalies → immediate challenge\nNo fixed waiting period. No intermediate warnings.",
            color=COLORS["muted"],
        ).pack(side="left")
        ttk.Button(bottom, text="Try challenge demo", command=demonstrate).pack(
            side="right"
        )
        label(
            self.body,
            "Research prototype • The overlay is not a Windows security lock.",
            10,
            COLORS["muted"],
        ).pack(anchor="w")
