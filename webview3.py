import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

class WebPage(QWebEngineView):
    def __init__(self, parent=None):
        QWebEngineView.__init__(self)
        self.current_url = ''
        self.current_file_path = ''
        self.load(QUrl("https://facebook.com"))
        self.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self):
        print("Url Loaded")

    def _on_file_select(self):
        print("New File path selected")

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

        #Define Menus
        self.file_menu = self.main_menu.addMenu("File")
        self.navigation_menu = self.main_menu.addMenu("Navigation")

        #File Menu Actions
        open_file_action = QAction("Open File", self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.triggered.connect(self.openFileNameDialog)
        self.file_menu.addAction(open_file_action)


        #Navigation Menu Actions
        next_page_action = QAction("Next Page",self)
        next_page_action.setShortcut('Ctrl+N')
        self.navigation_menu.addAction(next_page_action)

        previous_page_action = QAction("Previous Page", self)
        previous_page_action.setShortcut('Ctrl+P')
        self.navigation_menu.addAction(previous_page_action)

        choose_page_action = QAction("Choose Page", self)
        choose_page_action.setShortcut('Ctrl+C')
        self.navigation_menu.addAction(choose_page_action)

    #File dialog box
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            WebPage.current_file_path = fileName
            WebPage._on_file_select(self)

    #Adds web widget to central widget
    def add_web_widet(self):
        self.web_widget = WebPage(self)
        self.setCentralWidget(self.web_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec_())  # only need one app, one running event loop
