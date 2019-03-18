import os
import sys
import ebooklib
from ebooklib import epub
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon

class WebPage(QWebEngineView):
    def __init__(self, parent=None):
        QWebEngineView.__init__(self)
        self.current_url = ''
        self.load(QUrl("https://facebook.com"))
        self.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self):
        print("Url Loaded")

    def _on_file_select(self):
        self.load(QUrl("https://google.com"))

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # Initialize the Main Window
        super(MainWindow, self).__init__(parent)
        self.fileName = ''
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

        #Toolbar
        exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAct)


    #File dialog box
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if self.fileName:
            print(self.fileName)
            #Handler function call
            self.handler()


    #File Handler Function, handles pdf, html, epub, docx, txt
    #Determines what type file name is and calls appropriate function
    def handler(self):
        if self.fileName.endswith('.pdf'):
            self.pdfHandler()
        elif self.fileName.endswith('.html'):
            self.htmlHandler()
        elif self.fileName.endswith('.docx'):
            self.docxHandler()
        elif self.fileName.endswith('.epub'):
            self.epubHandler()
        else:
            print("Invlaid filename")

    #PDF Handler
    def pdfHandler(self):
        print("pdf handler called")

    #html Handler
    def htmlHandler(self):
        print("html handler called")
        self.web_widget.load(QUrl.fromLocalFile(self.fileName))

    #Docx Handler
    def docxHandler(self):
        print("docx handler called")

    #Epub Handler
    def epubHandler(self):
        print("epub handler called")
        book = epub.read_epub(self.fileName)
        book_items = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                book_items.append(ebooklib.epub.EpubHtml.get_id(item))
        self.web_widget.load(QUrl.fromLocalFile(ebooklib.epub.EpubHtml.get_content(ui=item[0])))

    #Adds web widget to central widget
    def add_web_widet(self):
        self.web_widget = WebPage(self)
        self.setCentralWidget(self.web_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec_())  # only need one app, one running event loop
