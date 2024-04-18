from PySide6.QtCore import Qt, QFile, QTextStream, QRect
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

from ui_files.main_ui import Ui_MainWindow
from ThemeManager import ThemeManager

import sys


class UIManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set Current Page
        self.ui.main_window.setCurrentIndex(0)
        self.ui.overview_button.setChecked(True)

        # Could dynamically add buttons
        # newButton = QPushButton("hello")
        # self.ui.verticalLayout_2.addWidget(newButton)

        self.create_links()

    def create_links(self):
        """
        Create the links between the buttons and the stacked widget
        """
        self.ui.overview_button.clicked.connect(lambda: self.change_frame(0))
        self.ui.agent_toggle_button.clicked.connect(lambda: self.change_frame(1))
        self.ui.random_select_button.clicked.connect(lambda: self.change_frame(2))
        self.ui.save_files_button.clicked.connect(lambda: self.change_frame(3))
        self.ui.tools_button.clicked.connect(lambda: self.change_frame(4))
        self.ui.settings_button.clicked.connect(lambda: self.change_frame(5))

    def change_frame(self, index: int):
        """
        Changes the current frame to the index specified
        """
        self.ui.main_window.setCurrentIndex(index)

        buttons = self.ui.navigation_bar.findChildren(QPushButton)

        # De-selects the buttons if the settings button is clicked
        for button in buttons:
            if index in [5]:
                button.setAutoExclusive(False)
                button.setChecked(False)
            else:
                button.setAutoExclusive(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    theme_manager = ThemeManager()
    theme_manager.setTheme("default")

    app.setStyleSheet(theme_manager.getTheme())

    window = UIManager()
    window.show()

    app.exec()
