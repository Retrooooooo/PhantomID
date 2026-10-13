"""Guest demonstration — application-scoped only."""

import os
import shutil
from pathlib import Path


class GuestWorkspace:
    def __init__(self, parent_folder, approved_apps):
        self.parent = Path(parent_folder).resolve()
        self.approved = set(approved_apps)
        self.session = None

    def start(self, admin_id):
        if not self.approved:
            raise ValueError("At least one approved resource required.")
        folder = self.parent / f"phantomid_guest_{os.getpid()}"
        folder.mkdir(parents=True, exist_ok=True)
        # Verify resolved location below parent; deny symlink/reparse escape.
        try:
            folder.resolve(strict=True)
        except Exception as exc:
            folder.rmdir()
            raise ValueError("Session folder must resolve safely.") from exc
        if folder.resolve() != folder:
            folder.rmdir()
            raise ValueError("Session folder resolves outside parent; refused.")
        self.session = folder
        return folder

    def approve(self, resource_id, admin_id, minutes=10):
        if resource_id not in self.approved:
            raise PermissionError("Only approved resources allowed.")
        if not self.session:
            raise RuntimeError("No active session.")
        return {"resource": resource_id, "until": minutes, "approved_by": admin_id}

    def cleanup(self):
        if not self.session:
            return
        resolved = self.session.resolve()
        if not resolved.exists() or resolved.parent.resolve() != self.parent.resolve():
            raise ValueError("Cleanup refused: session folder changed or missing.")
        # Only delete contents owned by session; never follow links.
        for entry in resolved.iterdir():
            try:
                if entry.is_file() and not entry.is_symlink():
                    entry.unlink()
                elif entry.is_dir() and not entry.is_symlink():
                    shutil.rmtree(entry)
            except Exception:
                pass
        try:
            resolved.rmdir()
        except Exception:
            pass
        self.session = None
