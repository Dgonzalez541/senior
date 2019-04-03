import os
import shutil
import zipfile
import ebooklib
from ebooklib import epub
from ebooklib import utils

book = 'spanish.epub'
zip = 'tempspanish.zip'
directory = 'tempSpanishDir'

shutil.copyfile(book, zip)

zip_ref = zipfile.ZipFile(zip, 'r')
zip_ref.extractall(directory)
zip_ref.close()

bookRead = epub.read_epub(book)

for chapter in bookRead.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    chapter = str(chapter)
    first, second, third = chapter.split(':')
    third = third[:-1]

    if (third.endswith('.htm') or third.endswith('.xml') or third.endswith('.xhtml')):
        name, extension = third.split('.')
        src = directory + "/" +  third
        dest = directory + "/" + name + ".html"
        os.rename(src,dest)
    print(third)

os.remove(zip)
shutil.rmtree(directory)
