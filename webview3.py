import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

class WebPage(QWebEngineView):
    def __init__(self, parent=None):
        QWebEngineView.__init__(self)
        self.current_url = ''
        self.load(QUrl("https://facebook.com"))
        self.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self):
        print("Url Loaded")

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # Initialize the Main Window
        super(MainWindow, self).__init__(parent)
        self.create_menu()
        self.add_web_widet()
        self.show()

    def create_menu(self):
        ''' Creates the Main Menu '''
        self.main_menu = self.menuBar()
        self.main_menu_actions = {}

        self.file_menu = self.main_menu.addMenu("Example File Menu")
        self.file_menu.addAction(QAction("Testing Testing", self))

    def add_web_widet(self):
        self.web_widget = WebPage(self)
        self.setCentralWidget(self.web_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec_())  # only need one app, one running event loop
