import os
import sys
import ebooklib
import shutil
import zipfile
import nltk
from ebooklib import epub
from ebooklib import utils
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from langdetect import detect
from nltk.tokenize import sent_tokenize
from gtts import gTTS
from pydub import AudioSegment

class WebPage(QWebEngineView):
    def __init__(self, parent=None):
        QWebEngineView.__init__(self)
        self.current_url = ''

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # Initialize the Main Window
        super(MainWindow, self).__init__(parent)

        self.fileName = '' #Current file
        self.chapterList = [] #List of chapters in Epub
        self.currentSection = 0 #Current section of Epub
        self.chapterText = [] # List of html elements in current chapter
        self.currentText = '' #currently selected html element
        self.currentTextIndex = 0 #Current index in text
        self.currentParagraphAudio = AudioSegment.empty() #Empty audio segment

        #Delete audio
        try:
            os.remove( os.getcwd() + '/currentParagraphAudio.mp3')
        except:
            pass

        self.create_menu()
        self.createToolBar()
        self.add_web_widet()
        self.show()

    def create_menu(self):
        #Creates the Main Menu
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

    #Keyboard event handler
    def keyPressEvent(self, e):
        #Audio play controls
        if e.key() == Qt.Key_Return:
            try: #Delete previous audio
                os.remove( os.getcwd() + '/currentParagraphAudio.mp3')
            except:
                pass
            self.currentText = []
            self.getChapterText(self.chapterList[self.currentSection])
            print("Current Index: " + str(self.currentTextIndex))
            self.currentText = self.chapterText[self.currentTextIndex]

            if(self.currentText != ''):
                self.createMP3()
                os.system("mpg321 currentParagraphAudio.mp3")
            else:
                print("empty text")

        #Arrow key controls
        if e.key() == Qt.Key_Right:
            if((self.currentTextIndex + 1) < len(self.chapterText)):
                self.currentTextIndex = self.currentTextIndex + 1

        if e.key() == Qt.Key_Left:
            if((self.currentTextIndex - 1) >= 0):
                self.currentTextIndex = self.currentTextIndex - 1


    def createToolBar(self):

        #Toolbar
        exitAct = QAction(QIcon.fromTheme('exit'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAct)

        prevPageAct = QAction(QIcon.fromTheme('go-previous'),'Prev',self)
        prevPageAct.triggered.connect(self.pageTurnPrev)
        self.toolbar.addAction(prevPageAct)

        nextPageAct = QAction(QIcon.fromTheme('go-next'),'Next',self)
        nextPageAct.triggered.connect(self.pageTurnNext)
        self.toolbar.addAction(nextPageAct)

        #Combobox for toolbar
        self.combo=QComboBox()
        self.toolbar.addWidget(self.combo)
        self.combo.addItems(self.chapterList)
        self.combo.activated[str].connect(self.onActivated)

    #File dialog box
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if self.fileName:
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

    #html Handler
    def htmlHandler(self):
        self.web_widget.load(QUrl.fromLocalFile(self.fileName))
        self.currentTextIndex = 0;

    #Epub Handler
    def epubHandler(self):
        self.clearData()

        #copy and rename epub to zip for extraction
        shutil.copyfile(self.fileName, 'temp.zip')
        zip_ref = zipfile.ZipFile('temp.zip', 'r')
        zip_ref.extractall('tempDir')
        zip_ref.close()

        bookRead = epub.read_epub(self.fileName)
        for chapter in bookRead.get_items_of_type(ebooklib.ITEM_DOCUMENT):#Parse document files from epub file
            #Get usable file location for document file by parsing returned ebooklib object
            chapter = str(chapter)
            first, second, third = chapter.split(':')
            third = third[:-1]
            if (third.endswith('.htm') or third.endswith('.xml') or third.endswith('.xhtml')): #Convert to html
                name, extension = third.split('.')
                src = os.getcwd() + "/" + "tempDir" + "/" +  third
                dest = os.getcwd() + "/" + "tempDir" + "/" + name + ".html"
                os.rename(src,dest)
                self.chapterList.append(dest)
            else:
                file = self.fileName
                file = file[:-5]
                href = file + '/' + third
                self.chapterList.append(href)

        self.web_widget.load(QUrl.fromLocalFile(self.chapterList[0])) #Load first page
        self.combo.addItems(self.chapterList) #Set navigation dropdown options
        self.currentTextIndex = 0; #initialize current text section

    #Gets current chapter text
    def getChapterText(self, file):
        self.chapterText = []
        with open(file) as fp:
            soup = BeautifulSoup(fp,"html.parser")
        newArray = []
        raw =soup.findAll(['title','p','td','em','h2','span'])#get raw html tags in list of common tags that contain text
        for i in range(len(raw)):
            self.chapterText.append(raw[i].text)
        print(len(self.chapterText))
        fp.close()

    #Create mp3 file
    def createMP3(self):
        self.currentParagraphAudio = AudioSegment.empty() #create audio segment
        sentence_list = sent_tokenize(self.currentText)
        for sentence in sentence_list: #Language detection and conversion to mp3
                lang = detect(sentence)
                myobj = gTTS(text=sentence, lang=lang, slow=False)
                myobj.save("sentence.mp3")
                sentence = AudioSegment.from_mp3("sentence.mp3")
                self.currentParagraphAudio += sentence
        self.currentParagraphAudio.export("currentParagraphAudio.mp3", format="mp3")

    #Resets data for file changing
    def clearData(self):
        self.currentText = ''
        self.chapterText = []
        self.chapterList = []
        self.combo.clear()
        self.currentSection = 0
        self.currentParagraphAudio = AudioSegment.empty()
        #Delete temp files
        try:
            if(os.path.exists(os.getcwd() + '/temp.zip')):
                os.rmdir(os.getcwd() + '/temp.zip')
                if(os.path.exists(os.getcwd() + '/tempDir')):
                    os.rmdir(os.getcwd() + '/tempDir')
        except:
            pass

        #Delete audio
        try:
            os.remove( os.getcwd() + '/currentParagraphAudio.mp3')
        except:
            pass

    #Navigation Functions
    def pageTurnNext(self):
        if((self.currentSection + 1) <= len(self.chapterList)):
            self.currentSection = self.currentSection + 1
            self.web_widget.load(QUrl.fromLocalFile(self.chapterList[self.currentSection]))
            self.getChapterText(self.chapterList[self.currentSection])
            self.currrentTextIndex = 0

    def pageTurnPrev(self):
        if((self.currentSection - 1) >= 0):
            self.currentSection = self.currentSection - 1
            self.web_widget.load(QUrl.fromLocalFile(self.chapterList[self.currentSection]))
            self.getChapterText(self.chapterList[self.currentSection])
            self.currrentTextIndex = 0

    #On activate function that sets combobox index
    def onActivated(self):
        self.web_widget.load(QUrl.fromLocalFile(self.chapterList[self.combo.currentIndex()]))

    #Adds web widget to central widget
    def add_web_widet(self):
        self.web_widget = WebPage(self)
        self.setCentralWidget(self.web_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec_())  # only need one app, one running event loop
