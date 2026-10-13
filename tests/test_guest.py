from phantomid.guest import GuestWorkspace
import tempfile, pathlib


def test_guest_session_folder_approval_and_safe_cleanup():
    with tempfile.TemporaryDirectory() as tmp:
        g = GuestWorkspace(tmp, {"notepad"})
        folder = g.start(1)
        assert folder.exists()
        assert g.approve("notepad", 1)["resource"] == "notepad"
        try:
            g.approve("chrome", 1)
            assert False, "unapproved denied"
        except PermissionError:
            pass
        g.cleanup()
        assert not folder.exists()
