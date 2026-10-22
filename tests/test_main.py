"""Exercise command-line startup behavior."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from src.main import main


class MainTests(unittest.TestCase):
    """Verify main() forwards the startup file path to the app layer."""

    @patch("src.main.launch_app")
    def test_main_passes_first_startup_path(self, launch_app_mock) -> None:
        main(["example.rtf"])

        launch_app_mock.assert_called_once_with(Path("example.rtf"))

    @patch("src.main.launch_app")
    def test_main_without_startup_path_uses_empty_editor(
        self,
        launch_app_mock,
    ) -> None:
        main([])

        launch_app_mock.assert_called_once_with(None)