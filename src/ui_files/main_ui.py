# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(749, 527)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.side_frame = QWidget(self.centralwidget)
        self.side_frame.setObjectName(u"side_frame")
        self.verticalLayout_4 = QVBoxLayout(self.side_frame)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.top_bar = QWidget(self.side_frame)
        self.top_bar.setObjectName(u"top_bar")
        self.horizontalLayout = QHBoxLayout(self.top_bar)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 5, 0)
        self.horizontalSpacer = QSpacerItem(570, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.settings_button = QPushButton(self.top_bar)
        self.settings_button.setObjectName(u"settings_button")
        self.settings_button.setEnabled(True)

        self.horizontalLayout.addWidget(self.settings_button)


        self.verticalLayout_4.addWidget(self.top_bar)

        self.main_window = QStackedWidget(self.side_frame)
        self.main_window.setObjectName(u"main_window")
        self.main_window.setStyleSheet(u"")
        self.Overview = QWidget()
        self.Overview.setObjectName(u"Overview")
        self.gridLayout_3 = QGridLayout(self.Overview)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.lov_frame = QFrame(self.Overview)
        self.lov_frame.setObjectName(u"lov_frame")
        self.lov_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.lov_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.lov_frame)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.instalocker_status_layout = QVBoxLayout()
        self.instalocker_status_layout.setObjectName(u"instalocker_status_layout")
        self.status_label = QLabel(self.lov_frame)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.instalocker_status_layout.addWidget(self.status_label)

        self.status_button = QPushButton(self.lov_frame)
        self.status_button.setObjectName(u"status_button")
        self.status_button.setCheckable(True)

        self.instalocker_status_layout.addWidget(self.status_button)


        self.verticalLayout_5.addLayout(self.instalocker_status_layout)

        self.verticalSpacer_2 = QSpacerItem(20, 34, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)

        self.instalocker_status_layout_2 = QVBoxLayout()
        self.instalocker_status_layout_2.setObjectName(u"instalocker_status_layout_2")
        self.status_label_2 = QLabel(self.lov_frame)
        self.status_label_2.setObjectName(u"status_label_2")
        self.status_label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.instalocker_status_layout_2.addWidget(self.status_label_2)

        self.status_button_2 = QPushButton(self.lov_frame)
        self.status_button_2.setObjectName(u"status_button_2")

        self.instalocker_status_layout_2.addWidget(self.status_button_2)


        self.verticalLayout_5.addLayout(self.instalocker_status_layout_2)

        self.verticalSpacer_3 = QSpacerItem(20, 33, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_3)

        self.instalocker_status_layout_3 = QVBoxLayout()
        self.instalocker_status_layout_3.setObjectName(u"instalocker_status_layout_3")
        self.status_label_3 = QLabel(self.lov_frame)
        self.status_label_3.setObjectName(u"status_label_3")
        self.status_label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.instalocker_status_layout_3.addWidget(self.status_label_3)

        self.status_button_3 = QPushButton(self.lov_frame)
        self.status_button_3.setObjectName(u"status_button_3")

        self.instalocker_status_layout_3.addWidget(self.status_button_3)


        self.verticalLayout_5.addLayout(self.instalocker_status_layout_3)

        self.verticalSpacer_4 = QSpacerItem(20, 34, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_4)

        self.instalocker_status_layout_4 = QVBoxLayout()
        self.instalocker_status_layout_4.setObjectName(u"instalocker_status_layout_4")
        self.status_label_4 = QLabel(self.lov_frame)
        self.status_label_4.setObjectName(u"status_label_4")
        self.status_label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.instalocker_status_layout_4.addWidget(self.status_label_4)

        self.status_button_4 = QPushButton(self.lov_frame)
        self.status_button_4.setObjectName(u"status_button_4")

        self.instalocker_status_layout_4.addWidget(self.status_button_4)


        self.verticalLayout_5.addLayout(self.instalocker_status_layout_4)


        self.gridLayout_3.addWidget(self.lov_frame, 0, 0, 2, 1)

        self.mov_frame = QFrame(self.Overview)
        self.mov_frame.setObjectName(u"mov_frame")
        self.mov_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.mov_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.mov_frame)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.selected_agent_label = QLabel(self.mov_frame)
        self.selected_agent_label.setObjectName(u"selected_agent_label")
        self.selected_agent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.selected_agent_label)

        self.selected_agent = QComboBox(self.mov_frame)
        self.selected_agent.setObjectName(u"selected_agent")
        font = QFont()
        font.setBold(False)
        self.selected_agent.setFont(font)

        self.verticalLayout_8.addWidget(self.selected_agent)

        self.verticalSpacer_5 = QSpacerItem(20, 51, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_5)

        self.options_label = QLabel(self.mov_frame)
        self.options_label.setObjectName(u"options_label")
        self.options_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.options_label)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.pushButton = QPushButton(self.mov_frame)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setCheckable(True)

        self.verticalLayout_6.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.mov_frame)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setCheckable(True)

        self.verticalLayout_6.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.mov_frame)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setCheckable(True)

        self.verticalLayout_6.addWidget(self.pushButton_3)


        self.verticalLayout_8.addLayout(self.verticalLayout_6)

        self.verticalSpacer_6 = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.pushButton_4 = QPushButton(self.mov_frame)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.verticalLayout_7.addWidget(self.pushButton_4)

        self.pushButton_5 = QPushButton(self.mov_frame)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setCheckable(True)

        self.verticalLayout_7.addWidget(self.pushButton_5)


        self.verticalLayout_8.addLayout(self.verticalLayout_7)


        self.gridLayout_3.addWidget(self.mov_frame, 0, 1, 2, 1)

        self.rov_frame = QFrame(self.Overview)
        self.rov_frame.setObjectName(u"rov_frame")
        self.rov_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.rov_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.rov_frame)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.last_lock_label = QLabel(self.rov_frame)
        self.last_lock_label.setObjectName(u"last_lock_label")
        self.last_lock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_9.addWidget(self.last_lock_label)

        self.last_lock_stat = QLabel(self.rov_frame)
        self.last_lock_stat.setObjectName(u"last_lock_stat")
        self.last_lock_stat.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_9.addWidget(self.last_lock_stat)


        self.verticalLayout_13.addLayout(self.verticalLayout_9)

        self.verticalSpacer_7 = QSpacerItem(20, 32, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_13.addItem(self.verticalSpacer_7)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.average_lock_label = QLabel(self.rov_frame)
        self.average_lock_label.setObjectName(u"average_lock_label")
        self.average_lock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_10.addWidget(self.average_lock_label)

        self.average_lock_stat = QLabel(self.rov_frame)
        self.average_lock_stat.setObjectName(u"average_lock_stat")
        self.average_lock_stat.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_10.addWidget(self.average_lock_stat)


        self.verticalLayout_13.addLayout(self.verticalLayout_10)

        self.verticalSpacer_8 = QSpacerItem(20, 31, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_13.addItem(self.verticalSpacer_8)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.times_used_label = QLabel(self.rov_frame)
        self.times_used_label.setObjectName(u"times_used_label")
        self.times_used_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.times_used_label)

        self.times_used_stat = QLabel(self.rov_frame)
        self.times_used_stat.setObjectName(u"times_used_stat")
        self.times_used_stat.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.times_used_stat)


        self.verticalLayout_13.addLayout(self.verticalLayout_11)

        self.verticalSpacer_9 = QSpacerItem(20, 32, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_13.addItem(self.verticalSpacer_9)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.agent_lock_label = QLabel(self.rov_frame)
        self.agent_lock_label.setObjectName(u"agent_lock_label")
        self.agent_lock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_12.addWidget(self.agent_lock_label)

        self.agent_lock_stat = QLabel(self.rov_frame)
        self.agent_lock_stat.setObjectName(u"agent_lock_stat")
        self.agent_lock_stat.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_12.addWidget(self.agent_lock_stat)


        self.verticalLayout_13.addLayout(self.verticalLayout_12)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_13.addItem(self.verticalSpacer_10)


        self.gridLayout_3.addWidget(self.rov_frame, 0, 2, 2, 1)

        self.main_window.addWidget(self.Overview)
        self.AgentToggle = QWidget()
        self.AgentToggle.setObjectName(u"AgentToggle")
        self.gridLayout_9 = QGridLayout(self.AgentToggle)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.verticalSpacer_12 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout_9.addItem(self.verticalSpacer_12, 2, 0, 1, 1)

        self.frame_2 = QFrame(self.AgentToggle)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QSize(0, 0))
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_8 = QGridLayout(self.frame_2)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_10 = QGridLayout()
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.checkBox_3 = QCheckBox(self.frame_2)
        self.checkBox_3.setObjectName(u"checkBox_3")

        self.gridLayout_10.addWidget(self.checkBox_3, 1, 2, 1, 1)

        self.checkBox_2 = QCheckBox(self.frame_2)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.gridLayout_10.addWidget(self.checkBox_2, 0, 0, 1, 1)

        self.checkBox = QCheckBox(self.frame_2)
        self.checkBox.setObjectName(u"checkBox")

        self.gridLayout_10.addWidget(self.checkBox, 0, 2, 1, 1)

        self.checkBox_4 = QCheckBox(self.frame_2)
        self.checkBox_4.setObjectName(u"checkBox_4")

        self.gridLayout_10.addWidget(self.checkBox_4, 1, 0, 1, 1)

        self.checkBox_5 = QCheckBox(self.frame_2)
        self.checkBox_5.setObjectName(u"checkBox_5")

        self.gridLayout_10.addWidget(self.checkBox_5, 0, 1, 1, 1)

        self.checkBox_6 = QCheckBox(self.frame_2)
        self.checkBox_6.setObjectName(u"checkBox_6")

        self.gridLayout_10.addWidget(self.checkBox_6, 1, 1, 1, 1)


        self.gridLayout_8.addLayout(self.gridLayout_10, 0, 0, 1, 1)


        self.gridLayout_9.addWidget(self.frame_2, 3, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.frame = QFrame(self.AgentToggle)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(15, 10, 15, 10)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.toggle_all_agent = QCheckBox(self.frame)
        self.toggle_all_agent.setObjectName(u"toggle_all_agent")
        self.toggle_all_agent.setAutoExclusive(False)

        self.horizontalLayout_2.addWidget(self.toggle_all_agent)

        self.toggle_none_agent = QCheckBox(self.frame)
        self.toggle_none_agent.setObjectName(u"toggle_none_agent")
        self.toggle_none_agent.setIconSize(QSize(16, 16))
        self.toggle_none_agent.setAutoExclusive(False)
        self.toggle_none_agent.setTristate(False)

        self.horizontalLayout_2.addWidget(self.toggle_none_agent)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


        self.horizontalLayout_3.addWidget(self.frame)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.gridLayout_9.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.verticalSpacer_11 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout_9.addItem(self.verticalSpacer_11, 0, 0, 1, 1)

        self.main_window.addWidget(self.AgentToggle)
        self.RandomSelect = QWidget()
        self.RandomSelect.setObjectName(u"RandomSelect")
        self.gridLayout_4 = QGridLayout(self.RandomSelect)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_3 = QLabel(self.RandomSelect)
        self.label_3.setObjectName(u"label_3")
        font1 = QFont()
        font1.setPointSize(20)
        self.label_3.setFont(font1)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)

        self.main_window.addWidget(self.RandomSelect)
        self.SaveFiles = QWidget()
        self.SaveFiles.setObjectName(u"SaveFiles")
        self.gridLayout_5 = QGridLayout(self.SaveFiles)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_4 = QLabel(self.SaveFiles)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_5.addWidget(self.label_4, 0, 0, 1, 1)

        self.main_window.addWidget(self.SaveFiles)
        self.Tools = QWidget()
        self.Tools.setObjectName(u"Tools")
        self.gridLayout_6 = QGridLayout(self.Tools)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_5 = QLabel(self.Tools)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font1)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_6.addWidget(self.label_5, 0, 0, 1, 1)

        self.main_window.addWidget(self.Tools)
        self.Settings = QWidget()
        self.Settings.setObjectName(u"Settings")
        self.gridLayout_7 = QGridLayout(self.Settings)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_6 = QLabel(self.Settings)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font1)
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_7.addWidget(self.label_6, 0, 0, 1, 1)

        self.main_window.addWidget(self.Settings)

        self.verticalLayout_4.addWidget(self.main_window)


        self.gridLayout.addWidget(self.side_frame, 0, 1, 1, 1)

        self.navigation_bar = QWidget(self.centralwidget)
        self.navigation_bar.setObjectName(u"navigation_bar")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.navigation_bar.sizePolicy().hasHeightForWidth())
        self.navigation_bar.setSizePolicy(sizePolicy1)
        self.navigation_bar.setMinimumSize(QSize(125, 0))
        self.navigation_bar.setMaximumSize(QSize(125, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.navigation_bar)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 5)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 10, -1, 10)
        self.title_label = QLabel(self.navigation_bar)
        self.title_label.setObjectName(u"title_label")
        font2 = QFont()
        font2.setPointSize(15)
        self.title_label.setFont(font2)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.title_label)

        self.version_label = QLabel(self.navigation_bar)
        self.version_label.setObjectName(u"version_label")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.version_label)


        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.overview_button = QPushButton(self.navigation_bar)
        self.overview_button.setObjectName(u"overview_button")
        self.overview_button.setCheckable(True)
        self.overview_button.setAutoExclusive(True)
        self.overview_button.setAutoDefault(False)
        self.overview_button.setFlat(False)

        self.verticalLayout_2.addWidget(self.overview_button)

        self.agent_toggle_button = QPushButton(self.navigation_bar)
        self.agent_toggle_button.setObjectName(u"agent_toggle_button")
        self.agent_toggle_button.setCheckable(True)
        self.agent_toggle_button.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.agent_toggle_button)

        self.random_select_button = QPushButton(self.navigation_bar)
        self.random_select_button.setObjectName(u"random_select_button")
        self.random_select_button.setCheckable(True)
        self.random_select_button.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.random_select_button)

        self.save_files_button = QPushButton(self.navigation_bar)
        self.save_files_button.setObjectName(u"save_files_button")
        self.save_files_button.setCheckable(True)
        self.save_files_button.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.save_files_button)

        self.tools_button = QPushButton(self.navigation_bar)
        self.tools_button.setObjectName(u"tools_button")
        self.tools_button.setCheckable(True)
        self.tools_button.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.tools_button)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 346, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_5 = QSpacerItem(5, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.exit_button = QPushButton(self.navigation_bar)
        self.exit_button.setObjectName(u"exit_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.exit_button.sizePolicy().hasHeightForWidth())
        self.exit_button.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.exit_button)

        self.horizontalSpacer_4 = QSpacerItem(5, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.gridLayout.addWidget(self.navigation_bar, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.exit_button.clicked.connect(MainWindow.close)

        self.main_window.setCurrentIndex(1)
        self.overview_button.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.settings_button.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.status_label.setText(QCoreApplication.translate("MainWindow", u"Instalocker", None))
        self.status_button.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.status_label_2.setText(QCoreApplication.translate("MainWindow", u"Status", None))
        self.status_button_2.setText(QCoreApplication.translate("MainWindow", u"Waiting", None))
        self.status_label_3.setText(QCoreApplication.translate("MainWindow", u"Safe Mode", None))
        self.status_button_3.setText(QCoreApplication.translate("MainWindow", u"Off", None))
        self.status_label_4.setText(QCoreApplication.translate("MainWindow", u"Current Save", None))
        self.status_button_4.setText(QCoreApplication.translate("MainWindow", u"default", None))
        self.selected_agent_label.setText(QCoreApplication.translate("MainWindow", u"Selected Agent", None))
        self.selected_agent.setCurrentText("")
        self.options_label.setText(QCoreApplication.translate("MainWindow", u"Options", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Hover", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Random Agent", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Map Specific", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Tools", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Anti-AFK", None))
        self.last_lock_label.setText(QCoreApplication.translate("MainWindow", u"Last Lock", None))
        self.last_lock_stat.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.average_lock_label.setText(QCoreApplication.translate("MainWindow", u"Average Lock", None))
        self.average_lock_stat.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.times_used_label.setText(QCoreApplication.translate("MainWindow", u"Times Used", None))
        self.times_used_stat.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.agent_lock_label.setText(QCoreApplication.translate("MainWindow", u"Agent Locks", None))
        self.agent_lock_stat.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.checkBox_3.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.checkBox_4.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.checkBox_5.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.checkBox_6.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.toggle_all_agent.setText(QCoreApplication.translate("MainWindow", u"All", None))
        self.toggle_none_agent.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Random Select", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Save Files", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Tools", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.title_label.setText(QCoreApplication.translate("MainWindow", u"VALocker", None))
        self.version_label.setText(QCoreApplication.translate("MainWindow", u"2.0.0", None))
        self.overview_button.setText(QCoreApplication.translate("MainWindow", u"Overview", None))
        self.agent_toggle_button.setText(QCoreApplication.translate("MainWindow", u"Agent Toggle", None))
        self.random_select_button.setText(QCoreApplication.translate("MainWindow", u"Random Select", None))
        self.save_files_button.setText(QCoreApplication.translate("MainWindow", u"Save Files", None))
        self.tools_button.setText(QCoreApplication.translate("MainWindow", u"Tools", None))
        self.exit_button.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
    # retranslateUi

