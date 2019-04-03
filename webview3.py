import os
import sys
import ebooklib
import shutil
import zipfile
from ebooklib import epub
from ebooklib import utils
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
        self.chapterList = []
        self.currentSection = 0

        self.create_menu()
        self.createToolBar()
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
        next_page_action.triggered.connect(self.pageTurnNext)
        self.navigation_menu.addAction(next_page_action)

        previous_page_action = QAction("Previous Page", self)
        previous_page_action.setShortcut('Ctrl+P')
        previous_page_action.triggered.connect(self.pageTurnPrev)
        self.navigation_menu.addAction(previous_page_action)

        choose_page_action = QAction("Choose Page", self)
        choose_page_action.setShortcut('Ctrl+C')
        self.navigation_menu.addAction(choose_page_action)

    def createToolBar(self):

        #Toolbar
        exitAct = QAction(QIcon.fromTheme('exit'), 'Exit', self)
        #exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAct)

        prevPageAct = QAction(QIcon.fromTheme('go-previous'),'Prev',self)
        #prevPageAct.setShortcut('Ctrl+P')
        prevPageAct.triggered.connect(self.pageTurnPrev)
        self.toolbar.addAction(prevPageAct)

        nextPageAct = QAction(QIcon.fromTheme('go-next'),'Next',self)
        #nextPageAct.setShortcut('Ctrl+N')
        nextPageAct.triggered.connect(self.pageTurnNext)
        self.toolbar.addAction(nextPageAct)

        #Combobox for toolbar
        self.combo=QComboBox()
        self.toolbar.addWidget(self.combo)
        self.combo.addItems(self.chapterList)


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

        book = self.fileName
        zip = 'temp.zip'
        directory = 'tempDir'

        shutil.copyfile(book, zip)

        zip_ref = zipfile.ZipFile(zip, 'r')
        zip_ref.extractall(directory)
        zip_ref.close()

        bookRead = epub.read_epub(self.fileName)

        for chapter in bookRead.get_items_of_type(ebooklib.ITEM_DOCUMENT):

            #parse file path to content file from item object inside OBES folder
            chapter = str(chapter)
            first, second, third = chapter.split(':')
            third = third[:-1]

            if (third.endswith('.htm') or third.endswith('.xml') or third.endswith('.xhtml')):
                name, extension = third.split('.')
                src = os.getcwd() + "/" + directory + "/" +  third
                dest = os.getcwd() + "/" + directory + "/" + name + ".html"
                print("Adjusted dest" + dest)
                os.rename(src,dest)
                self.chapterList.append(dest)
            else:
                file = self.fileName
                file = file[:-5]
                href = file + '/' + third
                self.chapterList.append(href)

        self.web_widget.load(QUrl.fromLocalFile(self.chapterList[0]))
        self.combo.addItems(self.chapterList)


    #Adds web widget to central widget
    def add_web_widet(self):
        self.web_widget = WebPage(self)
        self.setCentralWidget(self.web_widget)

    def pageTurnNext(self):
        print("pageTurnNext called")
        #print("CurrentP Page: " + self.currentSection)
        if((self.currentSection + 1) <= len(self.chapterList)):
            self.web_widget.load(QUrl.fromLocalFile(self.chapterList[self.currentSection + 1]))
            self.currentSection = self.currentSection + 1

    def pageTurnPrev(self):
        print("pageTurnPrev called")
        #print("CurrentP Page: " + self.currentSection)
        if((self.currentSection - 1) >= 0):
            self.web_widget.load(QUrl.fromLocalFile(self.chapterList[self.currentSection - 1]))
            self.currentSection = self.currentSection - 1



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec_())  # only need one app, one running event loop
