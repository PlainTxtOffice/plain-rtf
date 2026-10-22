"""Exercise application startup wiring."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from src.gui.app import launch_app


class LaunchAppTests(unittest.TestCase):
    """Verify the app launch path initializes the root window correctly."""

    @patch("src.gui.app.RootWindow")
    @patch("src.gui.app.DocumentAdapter")
    @patch("src.gui.app.configure_logging")
    def test_launch_app_passes_startup_path_to_root_window(
        self,
        configure_logging_mock,
        document_adapter_class,
        root_window_class,
    ) -> None:
        startup_path = Path("example.rtf")

        launch_app(startup_path)

        configure_logging_mock.assert_called_once_with("rtf-editor")
        document_adapter = document_adapter_class.return_value
        root_window_class.assert_called_once_with(
            document_adapter=document_adapter,
            startup_path=startup_path,
        )
        root_window_class.return_value.run.assert_called_once_with()

    @patch("src.gui.app.STORAGE_MODE", "portable")
    @patch("src.gui.app.messagebox.showerror")
    @patch("src.gui.app.tk.Tk")
    @patch("src.gui.app.RootWindow")
    @patch("src.gui.app.configure_logging", side_effect=PermissionError("Read-only drive"))
    def test_unwritable_portable_storage_stops_startup(
        self, configure_logging_mock, root_window_class, tk_class, showerror,
    ):
        launch_app()

        configure_logging_mock.assert_called_once()
        root_window_class.assert_not_called()
        tk_class.return_value.withdraw.assert_called_once()
        tk_class.return_value.destroy.assert_called_once()
        self.assertIn("will not be redirected to AppData", showerror.call_args.kwargs["message"])

    @patch("src.gui.app._show_storage_error")
    @patch("src.gui.app.configure_logging")
    def test_wrapped_log_write_error_is_reported(self, configure_logging_mock, show_storage_error):
        cause = PermissionError("Log file is locked")
        error = ValueError("Unable to configure handler")
        error.__cause__ = cause
        configure_logging_mock.side_effect = error
        launch_app()
        show_storage_error.assert_called_once_with(cause)

    @patch("src.gui.app.configure_logging", side_effect=ValueError("Invalid configuration"))
    def test_other_configuration_errors_are_not_hidden(self, configure_logging_mock):
        with self.assertRaises(ValueError):
            launch_app()
