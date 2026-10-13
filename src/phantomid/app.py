import os
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from cryptography.fernet import InvalidToken
from keyring.errors import KeyringError

from .auth import Auth
from .monitor import Monitor
from .profiles import ProfileRepository
from .storage import Store
from .ui.dashboard import Dashboard
from .ui.theme import COLORS, configure, label


class Application:
    def __init__(self, root, store):
        self.root, self.store = root, store
        self.auth = Auth(store)
        self.monitor = Monitor(store)
        self.poll_id = root.after(1000, self.poll_monitor)
        self.user = None
        root.title("PhantomID — Behavioral authentication")
        root.geometry("1200x1000")
        root.minsize(1000, 800)
        configure(root)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.login_screen()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_screen(self):
        self.monitor.clear()
        self.user = None
        self.clear()
        card = tk.Frame(self.root, bg="white", padx=40, pady=36)
        card.place(relx=0.5, rely=0.5, anchor="center")
        first = not self.store.users()
        label(card, "◈ PhantomID", 30, bold=True).pack(anchor="w")
        label(
            card, "Create your administrator account" if first else "Welcome back", 18
        ).pack(anchor="w", pady=(16, 8))
        label(
            card,
            "Local accounts. No cloud connection.\nMonitoring never starts without consent.",
            color=COLORS["muted"],
        ).pack(anchor="w", pady=(0, 24))
        entries = {}
        for name in ("Username", "Password"):
            label(card, name).pack(anchor="w", pady=(8, 4))
            entry = ttk.Entry(card, width=34, show="•" if name == "Password" else "")
            entry.pack(fill="x")
            entries[name] = entry
        error = label(card, "", color="#A32F36", wraplength=340)
        error.pack(anchor="w", pady=12)

        def submit():
            try:
                action = self.auth.register if first else self.auth.login
                self.user = action(entries["Username"].get(), entries["Password"].get())
                entries["Password"].delete(0, "end")
                self.show_dashboard()
            except (ValueError, PermissionError, sqlite3.IntegrityError) as exc:
                error.configure(
                    text="That username is already registered."
                    if isinstance(exc, sqlite3.IntegrityError)
                    else str(exc)
                )
                entries["Password"].delete(0, "end")

        ttk.Button(
            card,
            text="Create account" if first else "Sign in",
            command=submit,
            style="Accent.TButton",
        ).pack(fill="x")
        entries["Username"].focus_set()
        for entry in entries.values():
            entry.bind("<Return>", lambda event: submit())

    def show_dashboard(self):
        self.clear()
        self.dashboard = Dashboard(
            self.root, self.user, self.navigate, self.login_screen
        )
        self.dashboard.pack(fill="both", expand=True)
        self.navigate("Overview")

    def navigate(self, page):
        self.user = self.store.find_user(self.user["username"])
        dashboard = self.dashboard
        if page == "Stats":
            dashboard.page(page, "Aggregate behavioral profile — no content retained.")
            try:
                from phantomid.profiles import ProfileRepository

                repo = ProfileRepository(self.store)
                profile = repo.load(self.user["id"])
                if profile:
                    lines = []
                    for k, v in profile.get("features", {}).items():
                        lines.append(f"{k}: median {v[0]:.3f}, scale {v[1]:.3f}")
                    text = "\n".join(lines) or "Profile loaded."
                else:
                    text = "No saved profile. Enrollment in progress — see Overview."
                panel = dashboard.panel("Profile features (aggregate only)", text)
                label(
                    panel,
                    "Only timing / speed statistics shown. No typed content, paths, or window titles.",
                    10,
                    COLORS["muted"],
                ).pack(anchor="w", pady=(8, 4))
            except Exception as exc:
                dashboard.panel(
                    "Profile unavailable", f"Encrypted profile could not be read: {exc}"
                )
        elif page == "Overview":
            dashboard.overview(
                bool(self.user["consent"]), self.consent_dialog, self.challenge_demo
            )
            self.monitor_status = label(
                dashboard.body, self.monitor.status, bold=True, background="#E1F2F1"
            )
            self.monitor_status.pack(anchor="w", pady=(0, 4))
            self.monitor_progress = label(
                dashboard.body, self.monitor.progress(), color=COLORS["muted"]
            )
            self.monitor_progress.pack(anchor="w")
            ttk.Button(
                dashboard.body,
                text="Start / resume monitoring",
                command=self.start_monitoring,
                style="Accent.TButton",
            ).pack(side="left", pady=8)
            ttk.Button(
                dashboard.body, text="Pause monitoring", command=self.pause_monitoring
            ).pack(side="left", padx=12, pady=8)
            ttk.Button(
                dashboard.body,
                text="Show allowed aggregate stats",
                command=lambda: self.navigate("Stats"),
            ).pack(side="left", padx=12, pady=8)
        elif page == "Privacy":
            dashboard.page(page, "You decide whether behavioral collection is allowed.")
            dashboard.panel(
                "No content recording",
                "Keyboard and pointer collectors retain only aggregate timing and movement statistics. Temporary key identifiers and pointer positions are discarded after calculation. Capture stops before PhantomID password dialogs. Scroll and interaction-flow capture are not implemented yet.",
            )
            dashboard.panel(
                "Local storage",
                "Account passwords are hashed with Argon2. Behavioral profiles use authenticated encryption and an approved OS-backed keyring, with no plaintext fallback. Consent and event metadata are not encrypted. Learning samples stay in memory until the profile is ready.",
            )
            ttk.Button(
                dashboard.body,
                text="Withdraw consent" if self.user["consent"] else "Review consent",
                command=self.withdraw_consent
                if self.user["consent"]
                else self.consent_dialog,
            ).pack(anchor="w")
            ttk.Button(
                dashboard.body,
                text="Delete my behavioral profile",
                command=self.delete_profile,
            ).pack(anchor="w", pady=12)
        elif page == "Event history":
            dashboard.page(
                page, "Only event types and timestamps. No raw behavioral data."
            )
            self.table(
                ("Time (UTC)", "Event"),
                [
                    (event["created_at"], event["type"].replace("_", " "))
                    for event in self.store.events(self.user["id"])
                ],
            )
        elif page == "Users":
            dashboard.page(
                page,
                "Separate accounts, separate consent. Profile enrollment is coming next.",
            )
            if self.user["role"] != "admin":
                dashboard.panel(
                    "Administrator access required",
                    "Sign in with an administrator account to manage registered users.",
                )
                return
            self.table(
                ("Username", "Role", "Consent"),
                [
                    (
                        user["username"],
                        user["role"],
                        "Accepted" if user["consent"] else "Not given",
                    )
                    for user in self.store.users()
                ],
            )
            ttk.Button(
                dashboard.body,
                text="Add user",
                command=self.add_user_dialog,
                style="Accent.TButton",
            ).pack(anchor="w", pady=16)
        else:
            dashboard.page(
                page, "Application-scoped guest controls, not OS-wide restrictions."
            )
            dashboard.panel(
                "Guest workspace is not available yet",
                "The next guest slice will add an approved launcher and session-owned workspace. It will not restrict access to other Windows applications or folders.",
            )

    def table(self, columns, rows):
        tree = ttk.Treeview(
            self.dashboard.body, columns=columns, show="headings", height=8
        )
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=180, minwidth=100)
        for row in rows:
            tree.insert("", "end", values=row)
        tree.pack(fill="both", expand=True)
        if not rows:
            label(
                self.dashboard.body,
                "No events yet. Consent and challenge demos will appear here.",
                color=COLORS["muted"],
            ).pack(anchor="w", pady=16)

    def dialog(self, title):
        self.monitor.stop()
        window = tk.Toplevel(self.root)
        window.title(title)
        window.configure(bg="white", padx=28, pady=28)
        window.transient(self.root)
        window.grab_set()
        window.bind("<Escape>", lambda event: window.destroy())
        return window

    def consent_dialog(self):
        window = self.dialog("Behavioral privacy and consent")
        label(window, "Your patterns. Not your content.", 21, bold=True).pack(
            anchor="w"
        )
        label(
            window,
            "PhantomID processes keyboard timing and pointer movement rhythm to build your profile.\n\nIt does not store typed characters, key sequences, click destinations, screen content or window titles. Key identifiers and pointer coordinates are processed briefly to calculate timing and movement, then discarded.\n\nProfiles stay encrypted on this device. Collection begins only when you choose Start / resume monitoring. You can pause, withdraw consent or delete your profile in Privacy. Scroll and interaction-flow capture are not available yet.",
            wraplength=490,
            color=COLORS["muted"],
        ).pack(anchor="w", pady=20)
        accepted = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            window,
            text="I explicitly consent to behavioral pattern processing.",
            variable=accepted,
        ).pack(anchor="w", pady=12)

        def save():
            if not accepted.get():
                return
            self.store.set_consent(self.user["id"], True)
            self.store.add_event(self.user["id"], "consent_accepted")
            window.destroy()
            self.navigate("Overview")

        button = ttk.Button(
            window,
            text="Save consent",
            command=save,
            style="Accent.TButton",
            state="disabled",
        )
        button.pack(anchor="w", pady=12)
        accepted.trace_add(
            "write",
            lambda *args: button.configure(
                state="normal" if accepted.get() else "disabled"
            ),
        )

    def withdraw_consent(self):
        self.monitor.clear()
        if messagebox.askyesno(
            "Withdraw consent",
            "Stop permission for behavioral monitoring?",
            parent=self.root,
        ):
            self.store.set_consent(self.user["id"], False)
            self.store.add_event(self.user["id"], "consent_withdrawn")
            self.navigate("Privacy")

    def delete_profile(self):
        self.monitor.clear()
        if not messagebox.askyesno(
            "Delete behavioral profile",
            "Delete your saved behavioral profile? This does not delete your account or consent record.",
            parent=self.root,
        ):
            return
        try:
            ProfileRepository(self.store).delete(self.user["id"])
        except (RuntimeError, sqlite3.Error) as exc:
            messagebox.showerror("Profile deletion failed", str(exc), parent=self.root)
            return
        messagebox.showinfo(
            "Profile deleted",
            "No saved behavioral profile remains for your account.",
            parent=self.root,
        )

    def add_user_dialog(self):
        window = self.dialog("Add registered user")
        label(window, "Add a user", 22, bold=True).pack(anchor="w")
        fields = []
        for title in ("Username", "Password (at least 12 characters)"):
            label(window, title).pack(anchor="w", pady=(16, 4))
            entry = ttk.Entry(window, width=34, show="•" if fields else "")
            entry.pack(fill="x")
            fields.append(entry)
        error = label(window, "", color="#A32F36", wraplength=380)
        error.pack(anchor="w", pady=12)

        def save():
            try:
                self.auth.register(fields[0].get(), fields[1].get(), self.user["id"])
                fields[1].delete(0, "end")
                window.destroy()
                self.navigate("Users")
            except (ValueError, PermissionError, sqlite3.IntegrityError) as exc:
                error.configure(
                    text="Username already registered."
                    if isinstance(exc, sqlite3.IntegrityError)
                    else str(exc)
                )

        ttk.Button(
            window, text="Create user", command=save, style="Accent.TButton"
        ).pack(anchor="w")
        fields[0].focus_set()

    def challenge_demo(self, detected=False):
        self.store.add_event(
            self.user["id"], "challenge_detected" if detected else "challenge_demo"
        )
        window = self.dialog("PhantomID — Challenge demonstration")
        window.attributes("-fullscreen", True)
        panel = tk.Frame(window, bg="white")
        panel.place(relx=0.5, rely=0.5, anchor="center")
        label(panel, "Verify identity to resume", 26, bold=True).pack(anchor="w")
        label(
            panel,
            "Unusual behavior detected. Verify identity to resume.\nThis overlay is not an OS security lock. Escape leaves monitoring paused."
            if detected
            else "Manual demo — no anomaly has been detected.\nThis window is not an OS security lock. Escape exits the demo.",
            color=COLORS["muted"],
        ).pack(anchor="w", pady=20)
        label(panel, "Enter your password").pack(anchor="w")
        password = ttk.Entry(panel, show="•", width=36)
        password.pack(fill="x", pady=8)
        error = label(panel, "", color="#A32F36")
        error.pack(anchor="w", pady=8)

        def verify():
            try:
                self.auth.login(self.user["username"], password.get())
                password.delete(0, "end")
                self.store.add_event(
                    self.user["id"], "verified" if detected else "verified_demo"
                )
                window.destroy()
                if detected:
                    self.start_monitoring()
            except ValueError as exc:
                password.delete(0, "end")
                error.configure(text=str(exc))

        ttk.Button(panel, text="Verify", command=verify, style="Accent.TButton").pack(
            fill="x"
        )
        password.bind("<Return>", lambda event: verify())
        password.focus_set()

    def close(self):
        self.root.after_cancel(self.poll_id)
        self.monitor.clear()
        self.store.close()
        self.root.destroy()

    def start_monitoring(self):
        try:
            self.monitor.start(self.user["id"])
        except (
            RuntimeError,
            PermissionError,
            ValueError,
            OSError,
            sqlite3.Error,
            InvalidToken,
            KeyringError,
            ImportError,
        ):
            self.monitor.stop()
            messagebox.showerror(
                "Monitoring unavailable",
                "Check consent, desktop permissions and OS-backed key storage. Existing profiles have not been replaced. Monitoring remains off.",
                parent=self.root,
            )
        self.navigate("Overview")

    def pause_monitoring(self):
        self.monitor.stop()
        self.navigate("Overview")

    def poll_monitor(self):
        try:
            if self.monitor.tick():
                self.challenge_demo(detected=True)
            if (
                self.user
                and hasattr(self, "monitor_status")
                and self.monitor_status.winfo_exists()
            ):
                self.monitor_status.configure(text=self.monitor.status)
                self.monitor_progress.configure(text=self.monitor.progress())
        except (
            RuntimeError,
            PermissionError,
            ValueError,
            OSError,
            sqlite3.Error,
            InvalidToken,
            KeyringError,
        ):
            self.monitor.stop()
            self.monitor.status = (
                "Monitoring error — paused; review permissions or profile storage"
            )
        finally:
            self.poll_id = self.root.after(1000, self.poll_monitor)


def main():
    directory = (
        Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
        / "PhantomID"
    )
    root = tk.Tk()
    try:
        Application(root, Store(directory / "phantomid.db"))
    except (sqlite3.Error, OSError) as exc:
        messagebox.showerror("PhantomID could not start", str(exc), parent=root)
        root.destroy()
        return
    root.mainloop()
