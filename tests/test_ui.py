import tkinter as tk

from phantomid.app import Application
from phantomid.storage import Store


def test_desktop_pages_render_without_collecting_behavior(tmp_path):
    root = tk.Tk()
    root.withdraw()
    app = Application(root, Store(tmp_path / "ui.db"))
    try:
        app.user = app.auth.register("alice", "long password 123")
        app.show_dashboard()
        root.update_idletasks()
        for page in (
            "Overview",
            "Users",
            "Event history",
            "Privacy",
            "Guest workspace",
        ):
            app.navigate(page)
            root.update_idletasks()
            assert app.dashboard.body.winfo_children()
        app.consent_dialog()
        root.update_idletasks()
        dialogs = [
            widget
            for widget in root.winfo_children()
            if isinstance(widget, tk.Toplevel)
        ]
        assert len(dialogs) == 1
        dialogs[0].destroy()
        assert app.store.find_user("alice")["consent"] == 0
        assert app.store.events(app.user["id"]) == []
    finally:
        app.close()
