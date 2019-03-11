import ebooklib
from ebooklib import epub

book = epub.read_epub('Metamorphosis-jackson.epub')

for image in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    print (image)
    print(ebooklib.epub.EpubHtml.get_content(image))
    print("------------------------------")
