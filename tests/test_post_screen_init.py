import os
import sys
import unittest

try:
    from PyQt6.QtWidgets import QApplication
    _HAS_PYQT6 = True
except ModuleNotFoundError:
    _HAS_PYQT6 = False
    print("[TEST SKIP] PyQt6 no está instalado — pruebas GUI serán omitidas.")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.post_screen import PostScreen


class PostScreenInitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not _HAS_PYQT6:
            raise unittest.SkipTest("PyQt6 no disponible — saltando tests de UI.")
        cls.app = QApplication.instance() or QApplication([])

    def test_postscreen_initializes(self):
        screen = PostScreen()
        self.assertTrue(hasattr(screen, "_build_ui"))
        self.assertTrue(hasattr(screen, "engine"))
        self.assertTrue(hasattr(screen, "log_output"))


if __name__ == "__main__":
    unittest.main()
