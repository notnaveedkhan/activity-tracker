import sys

from PyQt5.QtWidgets import QApplication

from activity_tracker_gui import ActivityTrackerGUI

application = None
application_gui = None


def main():
    global application
    global application_gui
    application = QApplication(sys.argv)
    size = application.primaryScreen().size()
    application_gui = ActivityTrackerGUI(size.height(), size.width())
    application_gui.show()
    sys.exit(application.exec_())


if __name__ == '__main__':
    main()
