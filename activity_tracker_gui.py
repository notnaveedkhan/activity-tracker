import random
from datetime import datetime
from threading import Thread
from time import sleep

from PIL import ImageGrab
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import *
from pynput import keyboard, mouse


class ActivityTrackerGUI(QMainWindow):

    def __init__(self, screen_height: int, screen_width: int):
        super().__init__()

        self.screen_height = screen_height
        self.screen_width = screen_width
        self.track_activity = False
        self.debug = True
        self.activity_tracker_directory = ""
        self.keyboard_listener = None
        self.mouse_listener = None

        # GUI components declarations
        self.dir_path_line_edit = None
        self.screenshot_checkbox = None
        self.keyboard_checkbox = None
        self.mouse_checkbox = None
        self.browse_button = None
        self.track_button = None

        self.setWindowTitle("Activity Tracker")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        self.stop_action = QAction("Start Tracking", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        self.stop_action.triggered.connect(self.on_track_btn_click)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(self.stop_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # self.setFixedSize(int(self.screen_width / 3), int(self.screen_height / 3))
        self.design_layout()
        pass

    def design_layout(self):
        root = QWidget()
        vBox = QVBoxLayout()
        root.setLayout(vBox)

        self.setCentralWidget(root)
        root.setLayout(vBox)

        directorySelector = self.directory_selector()

        self.screenshot_checkbox = QCheckBox("Take Random Screenshots")
        self.keyboard_checkbox = QCheckBox("Track Keyboard Activity")
        self.mouse_checkbox = QCheckBox("Track Mouse Clicks with Screenshots")
        self.track_button = QPushButton("Start Tracking")
        self.track_button.setFixedWidth(int(self.screen_width / 10))
        self.track_button.clicked.connect(self.on_track_btn_click)

        vBox.addLayout(directorySelector)
        vBox.addWidget(self.screenshot_checkbox)
        vBox.addWidget(self.keyboard_checkbox)
        vBox.addWidget(self.mouse_checkbox)
        vBox.addWidget(self.track_button)
        vBox.setAlignment(self.track_button, Qt.AlignCenter)
        pass

    def on_track_btn_click(self):
        if not self.track_activity:
            self.track_button.setText("Stop Tracking")
            self.stop_action.setText("Stop Tracking")
            self.track_activity = True
            self.screenshot_checkbox.setEnabled(False)
            self.keyboard_checkbox.setEnabled(False)
            self.mouse_checkbox.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.on_start_tracking()
        else:
            self.track_button.setText("Start Tracking")
            self.stop_action.setText("Start Tracking")
            self.track_activity = False
            self.screenshot_checkbox.setEnabled(True)
            self.keyboard_checkbox.setEnabled(True)
            self.mouse_checkbox.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.on_stop_tracking()
        pass

    def get_timestamp_str(self):
        timestamp = datetime.now()
        return timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]

    def on_key_press(self, key):
        if self.track_activity and self.keyboard_checkbox.isChecked():
            key_str = f"[{self.get_timestamp_str()}]"
            if hasattr(key, "name"):  # if key is a special key
                key_str += "={" + key.name + "}\n"
            elif hasattr(key, "char"):  # if key is a character
                key_str += "={" + key.char + "}\n"
            file = open("{}keylogger.log".format(self.activity_tracker_directory), 'a')
            file.write(key_str)
            file.close()
        pass

    def on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool):
        if self.track_activity and self.mouse_checkbox.isChecked() and pressed:
            file_path = self.take_screenshot()
            text = "[" + self.get_timestamp_str() + "]={"
            text += "x:" + str(x) + ", y:" + str(y) + ", btn:" + button.name + "}, {"
            text += file_path + "}\n"
            file = open("{}keylogger.log".format(self.activity_tracker_directory), 'a')
            file.write(text)
            file.close()
        pass

    def track_keyboard_activity(self):
        if self.keyboard_listener is None:
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
            )
            self.keyboard_listener.start()
        pass

    def track_mouse_activity(self):
        if self.mouse_listener is None:
            self.mouse_listener = mouse.Listener(
                on_click=self.on_mouse_click,
            )
            self.mouse_listener.start()
        pass

    def take_screenshot(self):
        timestamp = datetime.now()
        imageGrab = ImageGrab.grab()
        timestamp_str = timestamp.strftime('%Y-%m-%dT%H-%M-%S')
        fileName = "{}screenshot_{}_{}.png".format(self.activity_tracker_directory, timestamp_str,
                                                   timestamp.microsecond)
        imageGrab.save(fileName, 'png')
        return fileName

    def track_screen_activity(self):
        while self.track_activity:
            try:
                file_path = self.take_screenshot()
                randomNumber = random.randint(1, 5)
                if self.debug:
                    timestamp = datetime.now()
                    print(f"Taken screenshot at {timestamp.strftime('%Y/%m/%dT%H:%M:%S')} and saved at {file_path}")
                    print(f"Taking next screenshot after {randomNumber} seconds")
                sleep(randomNumber)
            except Exception as e:
                if self.debug:
                    print("Error has occurred while trying to take screenshot at location {}",
                          self.activity_tracker_directory)
                    print(e)
        pass

    def on_start_tracking(self):
        self.activity_tracker_directory = self.dir_path_line_edit.text()
        if not self.activity_tracker_directory == "":
            self.activity_tracker_directory += "/"
        if self.keyboard_checkbox.isChecked():
            keyboard_activity_tracker_thread = Thread(target=self.track_keyboard_activity, daemon=True)
            keyboard_activity_tracker_thread.start()
        if self.mouse_checkbox.isChecked():
            mouse_activity_tracker_thread = Thread(target=self.track_mouse_activity, daemon=True)
            mouse_activity_tracker_thread.start()
        if self.screenshot_checkbox.isChecked():
            screen_activity_tracker_thread = Thread(target=self.track_screen_activity, daemon=True)
            screen_activity_tracker_thread.start()
        pass

    def on_stop_tracking(self):
        self.track_activity = False
        pass

    def directory_selector(self):
        label = QLabel("Please select the directory to save activity:")
        self.browse_button = QPushButton("Browse")
        self.browse_button.setContentsMargins(0, 0, 0, 0)
        self.dir_path_line_edit = QLineEdit()
        self.dir_path_line_edit.setFixedWidth(int(self.screen_width / 5))
        self.dir_path_line_edit.setReadOnly(True)
        self.dir_path_line_edit.setContentsMargins(0, 0, 0, 0)
        self.browse_button.clicked.connect(lambda: self.browse_directory(self.dir_path_line_edit))

        column = QVBoxLayout()
        row = QHBoxLayout()
        column.addWidget(label)
        row.addWidget(self.dir_path_line_edit)
        row.addWidget(self.browse_button)
        column.addLayout(row)
        return column

    def browse_directory(self, directoryPathLineEdit: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        directoryPathLineEdit.setText(path)
        pass

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()
                pass
            pass
