import nltk
import os
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from langdetect import detect
from nltk.tokenize import sent_tokenize
from gtts import gTTS
from pydub import AudioSegment

with open("mettest.html") as fp:
    soup = BeautifulSoup(fp,"html.parser")

tag_text = soup.p.get_text()
sentence_list = sent_tokenize(tag_text)
paragraph = AudioSegment.empty()

for sentence in sentence_list:
    lang = detect(sentence)
    myobj = gTTS(text=sentence, lang=lang, slow=False)
    myobj.save("sentence.mp3")
    sentence = AudioSegment.from_mp3("sentence.mp3")
    paragraph += sentence

paragraph.export("paragraph.mp3", format="mp3")
os.system("mpg321 paragraph.mp3")
