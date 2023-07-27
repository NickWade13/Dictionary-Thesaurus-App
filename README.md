Dictionary & Thesaurus Application

This is a Python-based application that provides dictionary and thesaurus functionalities. It uses a SQLite database to store and retrieve word definitions. The application also includes additional features such as displaying a random "Word of the Day", maintaining a search history, and a crossword helper.

Features:

Word Search: Users can search for the definitions of words. The search results are displayed in a new window.

Word of the Day: A random word and its definition(s) are displayed each time the application is launched.

Search History: The application maintains a history of the words searched during a session. Users can view the search history in a separate window.

Export Search History: Users can export the search history to a text file.

Clear Search History: Users can clear the search history.

Synonyms and Antonyms: Users can search for synonyms and antonyms of a word. This feature opens a new browser tab and performs the search on the WordHippo website.

Crossword Helper: Users can enter a pattern of known and unknown letters (using '_' for unknown letters), and the application will fetch matching words from the database.

Prerequisites
Python 3.x
Tkinter
ttkthemes
SQLite3

Installation:

Clone the repository or download the source code.

Ensure that you have Python installed on your machine. You can download Python here: https://www.python.org/downloads/

Install the necessary Python libraries using pip and the following commands:

pip install tkinter

pip install sqlite3

pip install ttkthemes

Files in the Repository:

dictionary_app.py: This is the main Python script that you run to start the application.

dict_app_gui.py: This Python script contains the main code for the application.

EDMTDictionary.db: This is the SQLite database file that contains the word definitions.

DTHicon.ico and DTHicon.png: These are icon files used in the application.

Usage:

Run the dictionary_app.py script to start the application

Use the GUI to search for word definitions, view the word of the day, and use other features of the application.



