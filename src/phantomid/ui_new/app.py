"""PhantomID - Main Application Controller (CustomTkinter)"""
import os
import sqlite3
import sys
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from phantomid.auth import Auth
from phantomid.monitor import Monitor
from phantomid.profiles import ProfileRepository
from phantomid.storage import Store

from .dashboard import Dashboard
from .login import AddUserDialog, ChallengeDialog, ConsentDialog, LoginScreen
from .theme import setup_theme


class Application:
    def __init__(self, root, store):
        self.root = root
        self.store = store
        self.auth = Auth(store)
        self.profiles = ProfileRepository(store)
        self.monitor = Monitor(store)
        self.user = None
        self.poll_id = None
        
        # Configure window
        self.root.title("PhantomID — Behavioral Authentication")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 750)
        
        # Setup theme
        setup_theme()
        
        # Protocol handlers
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Show login screen
        self._show_login()
    
    def _clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def _show_login(self):
        self.user = None
        self._clear()
        
        first_run = not self.store.users()
        
        self.login_screen = LoginScreen(
            self.root,
            on_login=self._handle_login,
            on_register=self._handle_register,
            is_first_run=first_run
        )
        self.login_screen.pack(fill="both", expand=True)
    
    def _handle_register(self, username, password):
        try:
            self.user = self.auth.register(username, password)
            self._show_dashboard()
        except (ValueError, PermissionError) as e:
            self.login_screen._show_error(str(e))
    
    def _handle_login(self, username, password):
        try:
            self.user = self.auth.login(username, password)
            self._show_dashboard()
        except ValueError as e:
            self.login_screen._show_error(str(e))
    
    def _show_dashboard(self):
        self._clear()
        
        self.dashboard = Dashboard(
            self.root,
            self.user,
            navigate_callback=self._navigate,
            sign_out_callback=self._show_login
        )
        self.dashboard.pack(fill="both", expand=True)
        
        # Start polling for monitor
        self._start_polling()
        
        # Initial navigation
        self._navigate("Overview")
    
    def _navigate(self, page):
        # Refresh user data
        row = self.store.find_user(self.user["username"])
        self.user = dict(row) if row else None
        
        if page == "Overview":
            is_active = getattr(self.monitor, "active", False) if hasattr(self, "monitor") else False
            self.dashboard.show_page("Overview", self.user, monitor_active=is_active)
        elif page == "Privacy":
            self.dashboard.show_page("Privacy", self.user)
        elif page == "Event History":
            self.dashboard.show_page("Event History", self.user)
            events = self.store.events(self.user["id"])
            self.dashboard.set_event_history(events)
        elif page == "Users":
            self.dashboard.show_page("Users", self.user)
            if self.user.get("role") == "admin":
                users = self.store.users()
                self.dashboard.set_users_table(users)
        elif page == "Guest Workspace":
            self.dashboard.show_page("Guest Workspace", self.user)
        elif page == "Stats":
            self.dashboard.show_page("Stats", self.user)
            try:
                profile = self.profiles.load(self.user["id"])
                self.dashboard.set_stats(profile)
            except (RuntimeError, ValueError, OSError):
                self.dashboard.set_stats(None)
        elif page == "Consent":
            self._show_consent()
        elif page == "PrivacyConsent":
            self._show_consent()
        elif page == "WithdrawConsent":
            self._withdraw_consent()
        elif page == "DeleteProfile":
            self._delete_profile()
        elif page == "AddUser":
            self._show_add_user()
        elif page == "Challenge":
            self._show_challenge()
        elif page == "StartMonitoring":
            self._start_monitoring()
        elif page == "PauseMonitoring":
            self._pause_monitoring()
        elif page == "WithdrawConsent":
            self._withdraw_consent()
        elif page == "DeleteProfile":
            self._delete_profile()
    
    def _show_consent(self):
        def on_accept():
            self.store.set_consent(self.user["id"], True)
            self.store.add_event(self.user["id"], "consent_accepted")
            self._navigate("Overview")
        
        ConsentDialog(self.root, on_accept)
    
    def _withdraw_consent(self):
        if messagebox.askyesno("Withdraw consent", "Stop permission for behavioral monitoring?", parent=self.root):
            self.store.set_consent(self.user["id"], False)
            self.store.add_event(self.user["id"], "consent_withdrawn")
            self.monitor.clear()
            self._navigate("Privacy")
    
    def _delete_profile(self):
        if messagebox.askyesno("Delete behavioral profile", "Delete your saved behavioral profile? This does not delete your account or consent record.", parent=self.root):
            try:
                self.profiles.delete(self.user["id"])
            except (RuntimeError, ValueError, OSError) as e:
                messagebox.showerror("Profile deletion failed", str(e), parent=self.root)
                return
            messagebox.showinfo("Profile deleted", "No saved behavioral profile remains for your account.", parent=self.root)
    
    def _show_add_user(self):
        def on_save(username, password):
            self.auth.register(username, password, self.user["id"])
            self._navigate("Users")
        
        AddUserDialog(self.root, on_save)
    
    def _show_challenge(self, detected=False):
        self.monitor.stop()
        
        def on_verify(username, password):
            self.auth.login(username, password)
        
        def on_success():
            self.store.add_event(self.user["id"], "verified" if detected else "verified_demo")
            self._start_monitoring()
        
        self.store.add_event(self.user["id"], "challenge_detected" if detected else "challenge_demo")
        
        ChallengeDialog(
            self.root,
            self.user["username"],
            on_verify=on_verify,
            detected=detected,
            on_success=on_success
        )
    
    def _start_monitoring(self):
        try:
            self.monitor.start(self.user["id"])
        except (RuntimeError, PermissionError, ValueError, OSError, ImportError):
            messagebox.showerror("Monitoring unavailable", 
                "Check consent, desktop permissions and OS-backed key storage. "
                "Existing profiles have not been replaced. Monitoring remains off.", 
                parent=self.root)
        self._navigate("Overview")
    
    def _pause_monitoring(self):
        self.monitor.stop()
        self._navigate("Overview")
    
    def _start_polling(self):
        if self.poll_id:
            self.root.after_cancel(self.poll_id)
        self._poll_monitor()
    
    def _poll_monitor(self):
        try:
            if self.monitor.tick():
                self._show_challenge(detected=True)
            
            # Update status if on Overview
            if self.dashboard.current_page == "Overview":
                pass
        except (RuntimeError, ValueError, OSError) as e:
            self.monitor.stop()
            print(f"Monitor error: {e}")
        finally:
            self.poll_id = self.root.after(1000, self._poll_monitor)
    
    def _on_close(self):
        if self.poll_id:
            self.root.after_cancel(self.poll_id)
        self.monitor.clear()
        self.store.close()
        self.root.destroy()


def main():
    # Setup theme before creating any widgets
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create root window
    root = ctk.CTk()
    
    # Data directory
    directory = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "PhantomID"
    
    try:
        store = Store(directory / "phantomid.db")
    except (OSError, sqlite3.Error) as e:
        messagebox.showerror("PhantomID could not start", str(e))
        root.destroy()
        return
    
    Application(root, store)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()