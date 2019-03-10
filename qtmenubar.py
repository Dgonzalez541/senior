import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, qApp,
 QWidget, QHBoxLayout, QVBoxLayout, QLabel)
from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MenuDemo(QMainWindow):
    def __init__(self):
        super().__init__()



        #Create menu bar
        bar = self.menuBar()

        #Create Root Menues
        file = bar.addMenu('File')
        edit = bar.addMenu('Edit')

        #Cereate Actions for Menues
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')

        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')

        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Ctrl+Q')

        find_action = QAction('Find...', self)

        replace_action = QAction('Replace...', self)

        #Add actions to Menues
        file.addAction(new_action)
        file.addAction(save_action)
        file.addAction(quit_action)

        find_menu = edit.addMenu('Find...')
        find_menu.addAction(find_action)
        find_menu.addAction(replace_action)

        #Events
        quit_action.triggered.connect(self.quit_trigger)
        file.triggered.connect(self.selected)


        self.setWindowTitle('My menues')
        self.resize(600, 400)

        #Add two labels to page
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        l1 = QLabel('Test')
        l2 = QLabel('Example')

        vbox = QVBoxLayout()
        vbox.addWidget(l1)
        vbox.addWidget(l2)
        self.centralWidget().setLayout(vbox)


        self.show()

    def quit_trigger(self):
        qApp.quit()

    def selected(self, q):
        print(q.text() + ' selected')




app = QApplication(sys.argv)
menues = MenuDemo()
sys.exit(app.exec_())
