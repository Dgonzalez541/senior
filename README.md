This is a foreign language e-reader that reads and displays .epub files. The files are converted to .zip and extracted. 
The content of the epub (html, htm, xml) is then parsed. Parsing included detecting what language the text is in and conversion to an mp3.
This is done on a a div by div basis for the current loaded page. The GUI is done using PyQT while parsing is handled using BS4. The final project is in
langEReader.py.
