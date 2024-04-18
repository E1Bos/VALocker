import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QFrame,
)

# UI Import
try:
    from ui_files.main_ui import Ui_MainWindow
except ImportError:
    print("UI file not found. Run the command `pyside6-uic src/ui_files/main_ui.ui -o src/ui_files/main_ui.py` in the terminal")
    sys.exit(1)

# Custom Imports
from CustomLogger import CustomLogger


class UIManager(QMainWindow):
    def __init__(self, parent: "VALocker"):
        super().__init__()
        self.logger = CustomLogger("GUI").get_logger()
        
        # To access variables from the main class
        self.parent = parent
        
        # UI Setup
        self.logger.info("Initializing UI")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Setting Default State
        self.set_ui_default_state()
        

    def set_theme(self, style_sheet: str):
        self.setStyleSheet(style_sheet)

    def set_ui_default_state(self) -> None:
        """
        Sets up the UI to the default state and connects the buttons to their respective functions.
        """
        # Set Current Page
        self.ui.main_window.setCurrentIndex(0)
        self.ui.overview_button.setChecked(True)

        # Hide the second safe mode frame
        self.ui.safe_mode_split_frame.hide()
        
        # Navigation Bar
        self.connect_change_frame(self.ui.overview_button, 0)
        self.connect_change_frame(self.ui.agent_toggle_button, 1)
        self.connect_change_frame(self.ui.random_select_button, 2)
        self.connect_change_frame(self.ui.save_files_button, 3)
        self.connect_change_frame(self.ui.tools_button, 4)
        self.connect_change_frame(self.ui.settings_button, 5)
        

    def connect_change_frame(self, button: QPushButton, frame_index: int) -> None:
        button.clicked.connect(lambda:
            self.ui.main_window.setCurrentIndex(frame_index)
            )

    # region: Setters

    def set_thread_running(self, value: bool = None) -> None:
        """
        Sets the thread running to the value specified.
        """
        text = "Running" if value else "Stopped"
        
        self.ui.thread_status_button.setChecked(value)
        self.ui.thread_status_button.setText(text)
        
        if value:
            self.ui.action_button.setEnabled(True)
            self.set_instalocker_status(self.parent.instalocker_status)
        else:
            self.ui.action_button.setText("None")
            self.ui.action_button.setChecked(False)
            self.ui.action_button.setEnabled(False)

    def set_instalocker_status(self, value: bool = None) -> None:
        """
        Sets the instalocker status to the value specified.
        """
        self.ui.action_button.setChecked(value)
        
        text = "Locking" if value else "Waiting"
        self.ui.action_button.setText(text)

    def set_safe_mode_enabled(self, value: bool = None) -> None:
        """
        Toggles the safe mode.
        """
        self.ui.safe_mode_button.setChecked(value)

    def set_safe_mode_strength(self, value: int = None) -> None:
        """
        Sets the safe mode strength value to the value specified.
        """
        text = ["Low", "Medium", "High"][value]
        self.ui.safe_mode_strength_button.setText(text)
        
    def set_current_save_name(self, value: str) -> None:
        """
        Sets the current save name to the value specified.
        """
        self.ui.save_redirect_button.setText(value)

    def set_selected_agent(self, value: str) -> None:
        """
        Sets the selected agent to the value specified.
        """
        self.ui.selected_agent_dropdown.setCurrentText(value)

    def set_last_lock(self, value: str) -> None:
        """
        Sets the last lock to the value specified.
        """
        self.ui.last_lock_stat.setText(value)

    def set_average_lock(self, value: str) -> None:
        """
        Sets the average lock to the value specified.
        """
        self.ui.average_lock_stat.setText(value)

    def set_times_used(self, value: str) -> None:
        """
        Sets the times used to the value specified.
        """
        self.ui.times_used_stat.setText(value)
