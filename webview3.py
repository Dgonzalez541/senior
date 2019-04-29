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


    def _on_load_finished(self):
        print("Url Loaded")

    def _on_file_select(self):
        self.load(QUrl("https://google.com"))

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # Initialize the Main Window
        super(MainWindow, self).__init__(parent)

        self.fileName = ''
        self.chapterList = [] #List of chapters in Epub
        self.currentSection = 0 #Current section of Epub
        self.audioToggle = True
        self.chapterText = [] # list of html elements in current chapter
        self.currentText = '' #currently selected html element
        self.currentTextIndex = 0
        self.currentParagraphAudio = AudioSegment.empty() #create audio segment

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

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Return:
            self.getChapterText(self.chapterList[self.currentSection])
            self.getCurrentText(self.currentTextIndex)
            self.createMP3()
            os.system("mpg321 currentParagraphAudio.mp3")

        if e.key() == Qt.Key_Right:
            if((self.currentTextIndex + 1) <= len(self.chapterText)):
                self.currentTextIndex = self.currentTextIndex + 1
                self.getCurrentText(self.currentTextIndex)


    def createToolBar(self):

        #Toolbar
        exitAct = QAction(QIcon.fromTheme('exit'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
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

        toggleAudioAct = QAction(QIcon.fromTheme('audio-volume-high'),'Toggle Audio', self)
        toggleAudioAct.setShortcut('Ctrl+T')
        toggleAudioAct.triggered.connect(self.toggleAudio)
        self.toolbar.addAction(toggleAudioAct)

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
        self.clearData()

        shutil.copyfile(self.fileName, 'temp.zip')
        zip_ref = zipfile.ZipFile('temp.zip', 'r')
        zip_ref.extractall('tempDir')
        zip_ref.close()

        bookRead = epub.read_epub(self.fileName)
        for chapter in bookRead.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            #parse file path to content file from item object inside OBES folder
            chapter = str(chapter)
            first, second, third = chapter.split(':')
            third = third[:-1]
            if (third.endswith('.htm') or third.endswith('.xml') or third.endswith('.xhtml')):
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

        self.web_widget.load(QUrl.fromLocalFile(self.chapterList[0]))
        self.combo.addItems(self.chapterList)

        self.currentTextIndex = 0;


    def getCurrentText(self,i):
        self.currentText = self.chapterText[i].get_text()

    def getChapterText(self, file):
        self.chapterText = []
        with open(file) as fp:
            soup = BeautifulSoup(fp,"html.parser")
        self.chapterText = soup.find_all() #get all html elements in currely selected chapter
        self.currentText = self.chapterText[self.currentTextIndex].get_text() #gets text from first element in chapter text


    def createMP3(self):
        sentence_list = sent_tokenize(self.currentText)
        for sentence in sentence_list:
                lang = detect(sentence)
                print(lang)
                myobj = gTTS(text=sentence, lang=lang, slow=False)
                myobj.save("sentence.mp3")
                sentence = AudioSegment.from_mp3("sentence.mp3")
                self.currentParagraphAudio += sentence
        self.currentParagraphAudio.export("currentParagraphAudio.mp3", format="mp3")

    #Resets data for file changing
    def clearData(self):
        self.currentText = []
        self.chapterText = []
        self.chapterList = []
        self.combo.clear()
        self.currentSection = 0
        try:
            #print(os.getcwd() + '/temp.zip')
            if(os.path.exists(os.getcwd() + '/temp.zip')):
                os.rmdir(os.getcwd() + '/temp.zip')
                if(os.path.exists(os.getcwd() + '/tempDir')):
                    os.rmdir(os.getcwd() + '/tempDir')
        except:
            pass

    def toggleAudio(self):
        self.audioToggle = not self.audioToggle

    #Navigation Functions
    def pageTurnNext(self):
        print("pageTurnNext called")
        #print("CurrentP Page: " + self.currentSection)
        if((self.currentSection + 1) <= len(self.chapterList)):
            self.currentSection = self.currentSection + 1
            self.web_widget.load(QUrl.fromLocalFile(self.chapterList[self.currentSection]))
            self.getChapterText(self.chapterList[self.currentSection])
            print(self.currentText)
            self.currrentTextIndex = 0
            self.getCurrentText(self.currentTextIndex)
            os.remove("currentParagraphAudio.mp3")





    def pageTurnPrev(self):
        print("pageTurnPrev called")
        #print("CurrentP Page: " + self.currentSection)
        if((self.currentSection - 1) >= 0):
            self.web_widget.load(QUrl.fromLocalFile(self.chapterList[self.currentSection - 1]))
            self.currentSection = self.currentSection - 1

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
