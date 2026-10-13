"""PhantomID - Login and Registration Screen"""
import customtkinter as ctk

from .theme import COLORS, get_font


class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, on_login, on_register, is_first_run):
        super().__init__(parent, fg_color=COLORS["background"])
        self.on_login = on_login
        self.on_register = on_register
        self.is_first_run = is_first_run
        self._build_ui()
    
    def _build_ui(self):
        # Center card
        self.card = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.configure(width=440, height=580)
        self.card.pack_propagate(False)
        
        # Padding container
        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=36)
        
        # Logo/Title
        ctk.CTkLabel(
            inner, text="◈ PhantomID",
            font=get_font("heading_large"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 4))
        
        subtitle = "Create your administrator account" if self.is_first_run else "Welcome back"
        ctk.CTkLabel(
            inner, text=subtitle,
            font=get_font("heading_small"),
            text_color=COLORS["muted"]
        ).pack(anchor="w", pady=(0, 8))
        
        ctk.CTkLabel(
            inner,
            text="Local accounts. No cloud connection.\nMonitoring never starts without consent.",
            font=get_font("body_small"),
            text_color=COLORS["muted"],
            justify="left"
        ).pack(anchor="w", pady=(0, 24))
        
        # Username field
        ctk.CTkLabel(inner, text="Username", font=get_font("body"), text_color=COLORS["text"]).pack(anchor="w", pady=(8, 4))
        self.username_entry = ctk.CTkEntry(
            inner,
            width=360,
            height=44,
            placeholder_text="Enter username",
            font=get_font("body"),
            corner_radius=8,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"]
        )
        self.username_entry.pack(fill="x", pady=(0, 4))
        
        # Password field
        ctk.CTkLabel(inner, text="Password", font=get_font("body"), text_color=COLORS["text"]).pack(anchor="w", pady=(8, 4))
        self.password_entry = ctk.CTkEntry(
            inner,
            width=360,
            height=44,
            placeholder_text="Enter password (min 12 chars)",
            font=get_font("body"),
            corner_radius=8,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
            show="•"
        )
        self.password_entry.pack(fill="x", pady=(0, 4))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            inner, text="",
            font=get_font("body_small"),
            text_color=COLORS["error"],
            wraplength=340,
            justify="left"
        )
        self.error_label.pack(anchor="w", pady=(12, 4))
        
        # Submit button
        btn_text = "Create account" if self.is_first_run else "Sign in"
        self.submit_btn = ctk.CTkButton(
            inner,
            text=btn_text,
            command=self._submit,
            width=360,
            height=44,
            font=get_font("body"),
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"]
        )
        self.submit_btn.pack(fill="x", pady=(8, 0))
        
        # Enter key binding
        self.username_entry.bind("<Return>", lambda e: self._submit())
        self.password_entry.bind("<Return>", lambda e: self._submit())
        
        # Focus
        self.after(100, lambda: self.username_entry.focus_set())
    
    def _submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self._show_error("Please enter both username and password")
            return
        
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
        
        if self.is_first_run:
            self.on_register(username, password)
        else:
            self.on_login(username, password)
    
    def _show_error(self, message):
        self.error_label.configure(text=message)
        self.password_entry.delete(0, "end")
    
    def clear_error(self):
        self.error_label.configure(text="")


class ConsentDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_accept):
        super().__init__(parent)
        self.on_accept = on_accept
        self.title("Behavioral Privacy and Consent")
        self.geometry("560x580")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["surface"])
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda e: self._on_close())
        self.focus_set()
    
    def _build_ui(self):
        # Main container with scroll
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=28, pady=28)
        
        ctk.CTkLabel(
            main, text="Your patterns. Not your content.",
            font=get_font("heading_medium"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 20))
        
        consent_text = (
            "PhantomID processes keyboard timing and pointer movement rhythm to build your profile.\n\n"
            "It does not store typed characters, key sequences, click destinations, "
            "screen content, or window titles. Key identifiers and pointer coordinates "
            "are processed briefly to calculate timing and movement, then discarded.\n\n"
            "Profiles stay encrypted on this device. Collection begins only when you "
            "choose Start Monitoring. You can pause, withdraw consent, or delete your "
            "profile in Privacy. Scroll and interaction-flow capture are not available yet."
        )
        
        ctk.CTkLabel(
            main, text=consent_text,
            font=get_font("body"),
            text_color=COLORS["muted"],
            wraplength=490,
            justify="left"
        ).pack(anchor="w", pady=(0, 24))
        
        # Checkbox
        self.accepted = ctk.BooleanVar(value=False)
        self.checkbox = ctk.CTkCheckBox(
            main,
            text="I explicitly consent to behavioral pattern processing.",
            variable=self.accepted,
            font=get_font("body"),
            text_color=COLORS["text"],
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            border_width=2,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._update_button
        )
        self.checkbox.pack(anchor="w", pady=(0, 16))
        
        # Save button
        self.save_btn = ctk.CTkButton(
            main,
            text="Save consent",
            command=self._save,
            width=360,
            height=44,
            font=get_font("body"),
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            state="disabled"
        )
        self.save_btn.pack(fill="x", pady=(8, 0))
        
        # Center window
        self.after(100, self._center)
    
    def _update_button(self):
        self.save_btn.configure(state="normal" if self.accepted.get() else "disabled")
    
    def _save(self):
        if not self.accepted.get():
            return
        self.on_accept()
        self.destroy()
    
    def _on_close(self):
        # Don't allow closing without explicit action
        pass
    
    def _center(self):
        self.update_idletasks()
        x = self.winfo_screenwidth() // 2 - self.winfo_width() // 2
        y = self.winfo_screenheight() // 2 - self.winfo_height() // 2
        self.geometry(f"+{x}+{y}")


class ChallengeDialog(ctk.CTkToplevel):
    """Fullscreen challenge/verification dialog"""
    def __init__(self, parent, username, on_verify, detected=False, on_success=None):
        super().__init__(parent)
        self.username = username
        self.on_verify = on_verify
        self.detected = detected
        self.on_success = on_success
        self.title("PhantomID - Verify Identity")
        self.attributes("-fullscreen", True)
        self.configure(fg_color=COLORS["surface"])
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda e: self._on_close())
        self.focus_set()
        self.after(100, lambda: self.password_entry.focus_set())
    
    def _build_ui(self):
        # Center panel
        panel = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        
        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=48, pady=48)
        
        # Title
        title_text = "Unusual behavior detected. Verify identity to resume." if self.detected else \
                     "Manual demo — no anomaly has been detected."
        ctk.CTkLabel(
            inner, text=title_text,
            font=get_font("heading_medium"),
            text_color=COLORS["text" if self.detected else "muted"],
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(0, 20))
        
        if not self.detected:
            ctk.CTkLabel(
                inner,
                text="This window is not an OS security lock. Escape exits the demo.",
                font=get_font("body_small"),
                text_color=COLORS["muted"],
                wraplength=400
            ).pack(anchor="w", pady=(0, 20))
        
        # Password field
        ctk.CTkLabel(inner, text="Enter your password", font=get_font("body"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 8))
        
        self.password_entry = ctk.CTkEntry(
            inner, width=360, height=44, font=get_font("body"),
            corner_radius=8, border_color=COLORS["border"],
            fg_color=COLORS["surface"], show="•"
        )
        self.password_entry.pack(fill="x", pady=(0, 8))
        
        # Error
        self.error_label = ctk.CTkLabel(
            inner, text="",
            font=get_font("body_small"),
            text_color=COLORS["error"],
            wraplength=360
        )
        self.error_label.pack(anchor="w", pady=(8, 4))
        
        # Verify button
        ctk.CTkButton(
            inner, text="Verify",
            command=self._verify,
            width=360, height=44,
            font=get_font("body"),
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"]
        ).pack(fill="x", pady=(8, 0))
        
        self.password_entry.bind("<Return>", lambda e: self._verify())
    
    def _verify(self):
        password = self.password_entry.get()
        if not password:
            self._show_error("Please enter your password")
            return
        
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
        
        try:
            self.on_verify(self.username, password)
            if self.on_success:
                self.on_success()
            self.destroy()
        except ValueError as e:
            self._show_error(str(e))
    
    def _show_error(self, message):
        self.error_label.configure(text=message)
        self.password_entry.delete(0, "end")
    
    def _on_close(self):
        # Just close, don't verify
        self.destroy()


class AddUserDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Add Registered User")
        self.geometry("460x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["surface"])
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda e: self._on_close())
        self.after(100, self._center)
    
    def _build_ui(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=28)
        
        ctk.CTkLabel(inner, text="Add a user", font=get_font("heading_medium"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(inner, text="Username", font=get_font("body"), text_color=COLORS["text"]).pack(anchor="w", pady=(8, 4))
        self.username_entry = ctk.CTkEntry(inner, width=400, height=44, placeholder_text="Username", font=get_font("body"), corner_radius=8)
        self.username_entry.pack(fill="x")
        
        ctk.CTkLabel(inner, text="Password (at least 12 characters)", font=get_font("body"), text_color=COLORS["text"]).pack(anchor="w", pady=(16, 4))
        self.password_entry = ctk.CTkEntry(inner, width=400, height=44, placeholder_text="Password", font=get_font("body"), corner_radius=8, show="•")
        self.password_entry.pack(fill="x")
        
        self.error_label = ctk.CTkLabel(inner, text="", font=get_font("body_small"), text_color=COLORS["error"], wraplength=380)
        self.error_label.pack(anchor="w", pady=(12, 4))
        
        ctk.CTkButton(inner, text="Create user", command=self._save, width=400, height=44, font=get_font("body"), corner_radius=8, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]).pack(fill="x", pady=(8, 0))
        
        self.username_entry.bind("<Return>", lambda e: self._save())
    
    def _save(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Please enter both username and password")
            return
        
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
        
        try:
            self.on_save(username, password)
            self.destroy()
        except (ValueError, PermissionError) as e:
            self.error_label.configure(text=str(e))
    
    def _on_close(self):
        self.destroy()
    
    def _center(self):
        self.update_idletasks()
        x = self.winfo_screenwidth() // 2 - self.winfo_width() // 2
        y = self.winfo_screenheight() // 2 - self.winfo_height() // 2
        self.geometry(f"+{x}+{y}")