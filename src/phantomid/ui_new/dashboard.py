"""PhantomID - Main Dashboard with Sidebar Navigation"""
import customtkinter as ctk

from .theme import COLORS, get_font


class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, user, navigate_callback, sign_out_callback):
        super().__init__(parent, fg_color=COLORS["background"])
        self.user = user
        self.navigate = navigate_callback
        self.sign_out = sign_out_callback
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self._build_sidebar()
        self._build_body()
        self.current_page = None
    
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS["sidebar"], width=218, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(1, weight=1)
        
        # Logo
        ctk.CTkLabel(
            self.sidebar, text="◈  PhantomID",
            font=get_font("heading_medium"),
            text_color="#FFFFFF"
        ).grid(row=0, column=0, padx=24, pady=(30, 4), sticky="w")
        
        ctk.CTkLabel(
            self.sidebar, text="Behavior, not content.",
            font=get_font("caption"),
            text_color="#BED2DF"
        ).grid(row=1, column=0, padx=24, pady=(0, 38), sticky="w")
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Overview", "📊"),
            ("Users", "👥"),
            ("Event History", "📋"),
            ("Privacy", "🔒"),
            ("Guest Workspace", "🏠"),
            ("Stats", "📈"),
        ]
        
        for i, (title, icon) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {title}",
                command=lambda v=title: self.navigate(v),
                font=get_font("body"),
                anchor="w",
                height=44,
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color="#FFFFFF",
                corner_radius=8,
                border_width=0
            )
            btn.grid(row=2+i, column=0, padx=12, pady=3, sticky="ew")
            self.nav_buttons[title] = btn
        
        # Footer with user info
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=8, column=0, padx=24, pady=24, sticky="sew")
        
        ctk.CTkLabel(footer, text=self.user["username"], font=get_font("heading_small"), text_color="#FFFFFF").pack(anchor="w")
        role_text = "Administrator" if self.user["role"] == "admin" else "Registered user"
        ctk.CTkLabel(footer, text=role_text, font=get_font("caption"), text_color="#BED2DF").pack(anchor="w", pady=(4, 16))
        
        ctk.CTkButton(
            footer, text="Sign out",
            command=self.sign_out,
            width=170, height=36,
            font=get_font("body"),
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            border_width=1,
            border_color=COLORS["border"]
        ).pack(fill="x")
        
        self.sidebar.grid_columnconfigure(0, weight=1)
    
    def _build_body(self):
        self.body = ctk.CTkScrollableFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.body.grid(row=0, column=1, sticky="nsew", padx=32, pady=28)
        self.body.grid_columnconfigure(0, weight=1)
    
    def show_page(self, page_name, user_data, monitor_active=False):
        self.user = user_data
        self.monitor_active = monitor_active
        # Update nav button states
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color=COLORS["sidebar_hover"])
            else:
                btn.configure(fg_color="transparent")
        
        # Clear body
        for widget in self.body.winfo_children():
            widget.destroy()
        
        self.current_page = page_name
        
        # Call appropriate page builder
        if page_name == "Overview":
            self._build_overview()
        elif page_name == "Privacy":
            self._build_privacy()
        elif page_name == "Event History":
            self._build_event_history()
        elif page_name == "Users":
            self._build_users()
        elif page_name == "Guest Workspace":
            self._build_guest()
        elif page_name == "Stats":
            self._build_stats()
    
    def _page_header(self, title, subtitle):
        ctk.CTkLabel(self.body, text=title, font=get_font("heading_large"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(self.body, text=subtitle, font=get_font("body"), text_color=COLORS["muted"], wraplength=650).pack(anchor="w", pady=(0, 24))
    
    def _panel(self, title, description, action_btn=None, action_text=None, action_cmd=None):
        panel = ctk.CTkFrame(self.body, fg_color=COLORS["surface"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        panel.pack(fill="x", pady=(0, 16))
        panel.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(panel, text=title, font=get_font("heading_small"), text_color=COLORS["text"]).pack(anchor="w", padx=24, pady=(20, 8))
        ctk.CTkLabel(panel, text=description, font=get_font("body"), text_color=COLORS["muted"], wraplength=660, justify="left").pack(anchor="w", padx=24, pady=(0, 18))
        
        if action_btn and action_text and action_cmd:
            btn = ctk.CTkButton(
                panel, text=action_text, command=action_cmd,
                width=200, height=36,
                font=get_font("body"), corner_radius=8,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
            )
            btn.pack(anchor="w", padx=24, pady=(0, 20))
        
        return panel
    
    def _build_overview(self):
        self._page_header("Overview", "Your session at a glance. Private by design, transparent by default.")
        
        consent = self.user.get("consent", 0)
        is_active = getattr(self, "monitor_active", False)
        
        # Monitoring status indicator bar — clearly visible
        is_active = getattr(self, "monitor_active", False)
        status_text = "● Monitoring active" if is_active else ("● Monitoring paused" if consent else "● Ready — tap Start")
        status_color = COLORS["success"] if is_active else (COLORS["muted"] if consent else COLORS["accent"])
        ctk.CTkLabel(self.body, text=status_text, font=get_font("body_small"), text_color=status_color, fg_color=COLORS["soft"], corner_radius=6).pack(anchor="w", padx=12, pady=(8, 4))
        status = "Monitoring ready" if consent else "Your permission comes first"
        desc = "Start monitoring below to learn your keyboard and pointer rhythm. Detection begins as soon as enough samples are available." if consent else \
               "Review what PhantomID processes before enabling any behavioral collection."
        
        self._panel(
            status, desc,
            action_btn=True, action_text="Review consent" if consent else "Review and consent",
            action_cmd=lambda: self.navigate("Privacy")
        )
        
        # Status strip
        strip = ctk.CTkFrame(self.body, fg_color=COLORS["soft"], corner_radius=8)
        strip.pack(fill="x", pady=(0, 24))
        ctk.CTkLabel(
            strip,
            text="Local processing • No typed content or cursor paths retained",
            font=get_font("body"), text_color=COLORS["success"],
            justify="left"
        ).pack(anchor="w", padx=20, pady=16)
        
        # Behavioral streams
        ctk.CTkLabel(self.body, text="Behavioral streams", font=get_font("heading_medium"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 12))
        
        streams = [
            ("Keyboard", "Press intervals and dwell timing"),
            ("Pointer", "Movement rhythm and direction changes"),
            ("Scrolling", "Burst duration and intervals"),
            ("Interaction flow", "Content-free transition timing (not implemented)"),
        ]
        
        streams_frame = ctk.CTkFrame(self.body, fg_color=COLORS["surface"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        streams_frame.pack(fill="x", pady=(0, 16))
        
        for name, detail in streams:
            row = ctk.CTkFrame(streams_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=9)
            ctk.CTkLabel(row, text=name, font=get_font("body"), text_color=COLORS["text"], width=150).pack(side="left")
            ctk.CTkLabel(row, text=detail, font=get_font("body"), text_color=COLORS["muted"]).pack(side="left")
            status_text = "See session status" if name in ("Keyboard", "Pointer") else "Not available yet"
            ctk.CTkLabel(row, text=status_text, font=get_font("caption"), text_color=COLORS["muted"]).pack(side="right")
        
        # Bottom actions
        bottom = ctk.CTkFrame(self.body, fg_color="transparent")
        bottom.pack(fill="x", pady=24)
        
        ctk.CTkLabel(
            bottom,
            text="3 fresh anomalies → immediate challenge\nNo fixed waiting period. No intermediate warnings.",
            font=get_font("caption"), text_color=COLORS["muted"], justify="left"
        ).pack(side="left")
        
        ctk.CTkButton(
            bottom, text="Try challenge demo",
            command=lambda: self.navigate("Challenge"),
            width=180, height=36,
            font=get_font("body"), corner_radius=8,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(side="right")
        
        ctk.CTkLabel(
            self.body,
            text="Research prototype • The overlay is not a Windows security lock.",
            font=get_font("caption"), text_color=COLORS["muted"]
        ).pack(anchor="w", pady=(16, 0))
        
        # Monitoring controls
        controls = ctk.CTkFrame(self.body, fg_color="transparent")
        controls.pack(fill="x", pady=(8, 0))
        
        ctk.CTkButton(
            controls, text="Start / resume monitoring",
            command=lambda: self.navigate("StartMonitoring"),
            width=220, height=40,
            font=get_font("body"), corner_radius=8,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(side="left", padx=(0, 12))
        
        ctk.CTkButton(
            controls, text="Pause monitoring",
            command=lambda: self.navigate("PauseMonitoring"),
            width=180, height=40,
            font=get_font("body"), corner_radius=8,
            fg_color=COLORS["soft"], hover_color="#C8D6E0", border_color=COLORS["border"], border_width=2, text_color=COLORS["text"]
        ).pack(side="left", padx=12)
        
        ctk.CTkButton(
            controls, text="Show aggregate stats",
            command=lambda: self.navigate("Stats"),
            width=200, height=40,
            font=get_font("body"), corner_radius=8,
            fg_color=COLORS["soft"], hover_color="#C8D6E0", border_color=COLORS["border"], border_width=2, text_color=COLORS["text"]
        ).pack(side="left", padx=12)
    
    def _build_privacy(self):
        self._page_header("Privacy", "You decide whether behavioral collection is allowed.")
        
        self._panel(
            "No content recording",
            "Keyboard and pointer collectors retain only aggregate timing and movement statistics. "
            "Temporary key identifiers and pointer positions are discarded after calculation. "
            "Capture stops before PhantomID password dialogs. Scroll and interaction-flow capture are not implemented yet."
        )
        
        self._panel(
            "Local storage",
            "Account passwords are hashed with Argon2. Behavioral profiles use authenticated encryption "
            "and an approved OS-backed keyring, with no plaintext fallback. Consent and event metadata "
            "are not encrypted. Learning samples stay in memory until the profile is ready."
        )
        
        action_text = "Withdraw consent" if self.user.get("consent", 0) else "Review consent"
        action_cmd = lambda: self.navigate("WithdrawConsent" if self.user.get("consent", 0) else "Consent")
        
        self._panel(
            "Consent management",
            "Withdraw consent to stop behavioral monitoring and delete your profile.",
            action_btn=True, action_text=action_text,
            action_cmd=action_cmd
        )
        
        self._panel(
            "Delete behavioral profile",
            "Permanently delete your saved behavioral profile. This does not delete your account or consent record.",
            action_btn=True, action_text="Delete my behavioral profile",
            action_cmd=lambda: self.navigate("DeleteProfile")
        )
    
    def _build_event_history(self):
        self._page_header("Event History", "Only event types and timestamps. No raw behavioral data.")
        # Events will be populated by the app
    
    def set_event_history(self, events):
        for widget in self.body.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and hasattr(widget, '_is_event_table'):
                widget.destroy()
        
        if not events:
            self._page_header("Event History", "Only event types and timestamps. No raw behavioral data.")
            ctk.CTkLabel(self.body, text="No events yet. Consent and challenge demos will appear here.", font=get_font("body"), text_color=COLORS["muted"]).pack(anchor="w", pady=16)
            return
        
        self._page_header("Event History", "Only event types and timestamps. No raw behavioral data.")
        
        table_frame = ctk.CTkFrame(self.body, fg_color=COLORS["surface"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        table_frame.pack(fill="both", expand=True)
        table_frame._is_event_table = True
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=1)
        
        # Headers
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=12)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header_frame, text="Time (UTC)", font=get_font("body_small"), text_color=COLORS["muted"]).grid(row=0, column=0, sticky="w", padx=16)
        ctk.CTkLabel(header_frame, text="Event", font=get_font("body_small"), text_color=COLORS["muted"]).grid(row=0, column=1, sticky="w", padx=16)
        
        for event in events:
            row = ctk.CTkFrame(table_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row, text=event["created_at"], font=get_font("body"), text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", padx=16)
            ctk.CTkLabel(row, text=event["type"].replace("_", " "), font=get_font("body"), text_color=COLORS["text"]).grid(row=0, column=1, sticky="w", padx=16)
    
    def _build_users(self):
        self._page_header("Users", "Separate accounts, separate consent.")
        
        if self.user.get("role") != "admin":
            self._panel("Administrator access required", "Sign in with an administrator account to manage registered users.")
            return
        
        # Table will be populated by app
    
    def set_users_table(self, users):
        for widget in self.body.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and hasattr(widget, '_is_users_table'):
                widget.destroy()
        
        self._page_header("Users", "Separate accounts, separate consent.")
        
        table_frame = ctk.CTkFrame(self.body, fg_color=COLORS["surface"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        table_frame.pack(fill="both", expand=True)
        table_frame._is_users_table = True
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=1)
        table_frame.grid_columnconfigure(2, weight=1)
        
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=12)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        ctk.CTkLabel(header_frame, text="Username", font=get_font("body_small"), text_color=COLORS["muted"]).grid(row=0, column=0, sticky="w", padx=16)
        ctk.CTkLabel(header_frame, text="Role", font=get_font("body_small"), text_color=COLORS["muted"]).grid(row=0, column=1, sticky="w", padx=16)
        ctk.CTkLabel(header_frame, text="Consent", font=get_font("body_small"), text_color=COLORS["muted"]).grid(row=0, column=2, sticky="w", padx=16)
        
        for user in users:
            row = ctk.CTkFrame(table_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=1)
            ctk.CTkLabel(row, text=user["username"], font=get_font("body"), text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", padx=16)
            ctk.CTkLabel(row, text=user["role"], font=get_font("body"), text_color=COLORS["text"]).grid(row=0, column=1, sticky="w", padx=16)
            ctk.CTkLabel(row, text="Accepted" if user["consent"] else "Not given", font=get_font("body"), text_color=COLORS["text"]).grid(row=0, column=2, sticky="w", padx=16)
        
        ctk.CTkButton(
            self.body, text="Add user",
            command=lambda: self.navigate("AddUser"),
            width=200, height=40,
            font=get_font("body"), corner_radius=8,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(anchor="w", pady=16)
    
    def _build_guest(self):
        self._page_header("Guest Workspace", "Application-scoped guest controls, not OS-wide restrictions.")
        self._panel(
            "Guest workspace is not available yet",
            "The next guest slice will add an approved launcher and session-owned workspace. "
            "It will not restrict access to other Windows applications or folders."
        )
    
    def _build_stats(self):
        self._page_header("Stats", "Aggregate behavioral profile — no content retained.")
        self._panel("Aggregate profile", "Profile details appear when enrollment completes and a profile is saved. Only median and scale values are shown — never raw behavioral content.")
    
    def set_stats(self, profile):
        for widget in self.body.winfo_children():
            if hasattr(widget, '_is_stats_panel'):
                widget.destroy()
        
        self._page_header("Stats", "Aggregate behavioral profile — no content retained.")
        
        if not profile:
            self._panel("No saved profile", "Enrollment in progress — see Overview for monitoring status.")
            return
        
        panel = ctk.CTkFrame(self.body, fg_color=COLORS["surface"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        panel.pack(fill="x", pady=(0, 16))
        panel._is_stats_panel = True
        
        ctk.CTkLabel(panel, text="Profile features (aggregate only)", font=get_font("heading_small"), text_color=COLORS["text"]).pack(anchor="w", padx=24, pady=(20, 8))
        
        features = profile.get("features", {})
        if features:
            for k, v in features.items():
                row = ctk.CTkFrame(panel, fg_color="transparent")
                row.pack(fill="x", padx=24, pady=4)
                ctk.CTkLabel(row, text=f"{k}:", font=get_font("body"), text_color=COLORS["text"], width=200).pack(side="left")
                ctk.CTkLabel(row, text=f"median {v[0]:.3f}, scale {v[1]:.3f}", font=get_font("mono"), text_color=COLORS["muted"]).pack(side="left")
        else:
            ctk.CTkLabel(panel, text="No features available", font=get_font("body"), text_color=COLORS["muted"]).pack(anchor="w", padx=24, pady=18)
        
        ctk.CTkLabel(panel, text="Only timing / speed statistics shown. No typed content, paths, or window titles.", font=get_font("caption"), text_color=COLORS["muted"]).pack(anchor="w", padx=24, pady=(8, 18))