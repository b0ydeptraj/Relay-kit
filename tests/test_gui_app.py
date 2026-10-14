import unittest
import customtkinter as ctk
from tools.gui_app.app import RelayKitStudioApp


class TestRelayKitStudioApp(unittest.TestCase):
    def setUp(self):
        # Initialize app in withdrawn state for headless/test environment
        self.app = RelayKitStudioApp()
        self.app.withdraw()

    def tearDown(self):
        # Stop background polling timers in views
        for view in self.app.views.values():
            if hasattr(view, "is_polling"):
                view.is_polling = False
        self.app.destroy()

    def test_app_views_initialization(self):
        self.assertIn("sniffer", self.app.views)
        self.assertIn("mobile", self.app.views)
        self.assertIn("reup", self.app.views)
        self.assertIn("uploader", self.app.views)

    def test_view_switching(self):
        for view_key in ("sniffer", "mobile", "reup", "uploader"):
            self.app._switch_view(view_key)
            self.assertEqual(
                self.app.nav_buttons[view_key].cget("text_color"),
                "#38bdf8"
            )


if __name__ == "__main__":
    unittest.main()
