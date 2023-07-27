import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from ttkthemes import ThemedTk
import sqlite3
import webbrowser
from datetime import datetime
import random
import os

# Define constants
DATABASE_PATH = "C:/Users/nick-/OneDrive/Documents/Python/Dictionary & Thesaurus/EDMTDictionary.db"

result_window = None
search_history_window = None  # Search history window
search_history_session = []  # Search history within the current session
export_button = None

def run_dictionary_app():
    def connect_to_database():
        try:
            connection = sqlite3.connect(DATABASE_PATH)
            cursor = connection.cursor()
            return connection, cursor
        except sqlite3.Error as e:
            # Handle database connection error
            show_error_message("Database Error", str(e))

    def fetch_random_word():
        connection, cursor = connect_to_database()
        cursor.execute("SELECT DISTINCT Word FROM Word ORDER BY RANDOM() LIMIT 1")
        random_word = cursor.fetchone()  # fetches only the first record

        if random_word:
            query = "SELECT Word, Type, Description FROM Word WHERE Word = ?"
            cursor.execute(query, (random_word[0],))
            results = cursor.fetchall()
        else:
            results = []

        connection.close()
        return results
    
    def display_word_of_the_day(word_definitions):
        if word_definitions:
            # Word of the Day Frame
            word_of_day_frame = tk.Frame(window, bg="light blue", bd=5)
            word_of_day_frame.pack(pady=20, padx=20, fill='both', expand=True)

            # Word of the Day Label
            word_of_day_label = tk.Label(word_of_day_frame, text=f"Word of the Day - {datetime.now().strftime('%Y-%m-%d')}", font=("Arial", 18, "bold"), bg="light blue")
            word_of_day_label.pack()

            # Word and Type
            word_and_type_label = tk.Label(word_of_day_frame, font=("Arial", 24, "bold", "italic"), bg="light blue")
            word_and_type_label.pack()

            # Word Description
            word_description_label = tk.Label(word_of_day_frame, font=("Arial", 14), wraplength=700, bg="light blue")
            word_description_label.pack()

            # Configure colors
            word_of_day_frame.configure(bg="light blue")
            word_of_day_label.configure(bg="light blue")
            word_and_type_label.configure(bg="light blue")
            word_description_label.configure(bg="light blue")

            # Variable to keep track of the current index
            current_index = 0

            # Function to update the definition displayed
            def update_definition(change):
                nonlocal current_index
                current_index = (current_index + change) % len(word_definitions)
                word, type, description = word_definitions[current_index]
                word_and_type_label.config(text=f"{word} ({type})")
                word_description_label.config(text=description)

            # Update the definition for the first time
            update_definition(0)

            # Create "Next" and "Previous" buttons if there are multiple definitions
            if len(word_definitions) > 1:
                next_button = ttk.Button(word_of_day_frame, text="Next", command=lambda: update_definition(1), style="Custom.TButton")
                next_button.pack(side=tk.RIGHT, padx=10, anchor=tk.E)
                previous_button = ttk.Button(word_of_day_frame, text="Previous", command=lambda: update_definition(-1), style="Custom.TButton")
                previous_button.pack(side=tk.LEFT, padx=10, anchor=tk.W)

    def search_word():
        search_term = search_entry.get().capitalize()  # Convert search term to capitalized form
        if not search_term:
            show_error_message("Error", "Please enter a word to search.")
            return

        if not search_term.isalpha():
            show_error_message("Error", "Please enter a valid word.")
            return

        # Fetch word data from the database using a parameterized query
        connection, cursor = connect_to_database()
        try:
            query = "SELECT Word, Type, Description FROM Word WHERE Word = ?"
            cursor.execute(query, (search_term,))
            results = cursor.fetchall()

            if results:
                # Prepare the search results
                search_results = []
                for result in results:
                    word, word_type, description = result
                    search_result = f"Word: {word}\nType: {word_type}\nDescription: {description}"
                    search_results.append(search_result)

                # Update the results text
                update_results_text(search_results)

                # Only add the word to the search history if it's not already there
                if not any(term == search_term for term, _ in search_history_session):
                    search_history_session.append((search_term, search_results))  # Append as a tuple

            else:
                search_results = ["No results found for the given word."]
                update_results_text(search_results)
        except sqlite3.Error as e:
            # Handle database query error
            show_error_message("Database Error", str(e))
        finally:
            # Close the database connection
            if connection:
                connection.close()

    def create_new_window_with_text():
        global result_window
        if result_window is None:
            result_window = tk.Toplevel()
        else:
            result_window.deiconify()
        result_window.title("Search Result")

        # Clear previous content
        for widget in result_window.winfo_children():
            widget.destroy()

        # Create a text area to display the result text
        result_textarea = tk.Text(result_window, font=("Arial", 12))
        result_textarea.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Create a scrollbar
        scrollbar = ttk.Scrollbar(result_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Link the scrollbar to the text area
        result_textarea.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=result_textarea.yview)

        result_window.protocol("WM_DELETE_WINDOW", result_window.withdraw)

        return result_textarea

    def update_results_text(result_text):
        result_textarea = create_new_window_with_text()

        # Insert all the definitions into the text area
        for definition in result_text:
            result_textarea.insert(tk.END, f"{definition}\n\n")

        # Disable editing of the text area
        result_textarea.configure(state=tk.DISABLED)

    def update_search_history_text(search_history_session):
        result_textarea = create_new_window_with_text()

        # Set the "search_term" tag configuration
        result_textarea.tag_config("search_term", font=("Arial", 14, "bold"))

        # Get the search history contents and display them
        for term, results in reversed(search_history_session):
            result_textarea.insert(tk.END, f"Search Term: {term}\n", "search_term")
            for result in results:
                result_textarea.insert(tk.END, f"{result}\n\n")
            # Insert the line
            result_textarea.insert(tk.END, f"{'-'*50}\n\n")

        # Disable editing of the text area
        result_textarea.configure(state=tk.DISABLED)

    def open_dictionary_website(url):
        search_url = url + search_entry.get().lower() + ".html"  # Convert search term to lowercase and add .html
        webbrowser.open_new_tab(search_url)

    def show_search_history():
        global search_history_window, export_button  # Add export_button to the global variables

        if not search_history_session:  # if the search history is empty
            tk.messagebox.showinfo('Info', 'There is no search history.')
            return

        print("Search history session before showing history:", search_history_session)

        if search_history_session:
            if search_history_window is None:
                # Create the search history window if it doesn't exist
                search_history_window = tk.Toplevel()
                search_history_window.title("Search History")

                # Modify the behavior of the close button
                search_history_window.protocol("WM_DELETE_WINDOW", search_history_window.withdraw)

            # Clear previous content
            for widget in search_history_window.winfo_children():
                widget.destroy()

            # Create the Export Search History Button if it doesn't exist
            if export_button is None or not tk.Toplevel.winfo_exists(export_button):
                export_button = ttk.Button(
                    search_history_window,
                    text="Export Search History",
                    command=export_search_history
                )
                export_button.pack(side=tk.RIGHT, padx=10)

            update_search_history_text(search_history_session)
            search_history_window.deiconify()
        else:
            print("Search history is empty for this session.")

    def export_search_history():
        if not search_history_session:  # if the search history is empty
            tk.messagebox.showinfo('Info', 'There is no search history.')
            return

        # Ask for filename
        export_filename = tk.simpledialog.askstring("Input", "Enter filename for export",
                                parent=search_history_window)
        if export_filename is not None: # Proceed only if user didn't press cancel
            try:
                # Check if the filename is valid
                if not all(c.isalnum() or c in '-_.' for c in export_filename):
                    raise ValueError("Invalid filename. Filenames can only contain alphanumeric characters, hyphens, underscores, and periods.")

                # Check if the file already exists
                if os.path.exists(f"{export_filename}.txt"):
                    raise FileExistsError("A file with this name already exists.")

                with open(f"{export_filename}.txt", 'w') as f:
                    for term, results in search_history_session:
                        f.write(f"Search Term: {term}\n")
                        for result in results:
                            f.write(f"{result}\n\n")
                        f.write(f"{'-'*50}\n\n")
                tk.messagebox.showinfo('Success', f'Search history has been exported to {export_filename}.txt.')
            except Exception as e:
                tk.messagebox.showerror('Error', f'An error occurred while exporting search history: {str(e)}')
    
    def clear_search_history():
        global search_history_session, search_history_window
        search_history_session.clear()

        # Show confirmation message
        tk.messagebox.showinfo('Success', 'Search history has been cleared.')

        # Destroy the search history window if it exists
        if search_history_window:
            search_history_window.destroy()
            search_history_window = None

    def crossword_helper():
        # Ask the user for the number of letters in the word
        num_letters = simpledialog.askinteger("Input", "Enter the number of letters in the word")

        # Ask the user for the letters they know
        letters = simpledialog.askstring("Input", f"Enter the letters you know, using '_' for unknown letters (total {num_letters} characters)")

        # Check if the user entered the correct number of characters
        if len(letters) != num_letters:
            messagebox.showerror("Error", "The number of characters you entered does not match the number you specified.")
            return

        # Check if the user entered a valid string of letters
        if not all(char.isalpha() or char == "_" for char in letters):
            messagebox.showerror("Error", "Please enter a valid string of letters.")
            return

        # Convert the string of letters to a list
        letters = list(letters)

        # Connect to the database
        connection, cursor = connect_to_database()

        # Prepare the SQL query
        query = "SELECT Word, Type, Description FROM Word WHERE Word LIKE ?"
        pattern = ''.join(letters)

        # Fetch matching words from the database
        cursor.execute(query, (pattern,))
        results = cursor.fetchall()

        # Group results by word
        word_dict = {}
        for word, word_type, description in results:
            if word not in word_dict:
                word_dict[word] = []
            word_dict[word].append((word_type, description))

        # Prepare the search results
        search_results = []
        for word, definitions in word_dict.items():
            for word_type, description in definitions:
                search_result = f"Word: {word}\nType: {word_type}\nDescription: {description}"
                search_results.append(search_result)

        # Update the results text
        update_results_text(search_results)
        search_history_session.append((pattern, search_results))  # Append as a tuple

        # Close the database connection
        connection.close()

    def show_error_message(title, message):
        tk.messagebox.showerror(title, message)

    # Create the main window
    window = ThemedTk(theme="radiance")
    window.title("Dictionary/Thesaurus Application")
    window.geometry("800x600")

    # Set the window icon
    window.iconbitmap(r'C:\Users\nick-\OneDrive\Documents\Python\Dictionary & Thesaurus\DTHicon.ico')

    # Get the background color of the current theme
    bg_color = ttk.Style().lookup("TFrame", "background")

    # Header Frame
    header_frame = ttk.Frame(window)
    header_frame.pack(pady=20)

    # Load the icon image
    icon_image = tk.PhotoImage(file=r'C:\Users\nick-\OneDrive\Documents\Python\Dictionary & Thesaurus\DTHicon2.png')

    # Create a label for the icon image
    icon_label = tk.Label(header_frame, image=icon_image)
    icon_label.pack(side=tk.LEFT)

    # Styling
    style = ttk.Style()
    style.configure("Custom.TButton", background=bg_color, foreground="black", borderwidth=0, focuscolor=style.configure(".")["background"])
    style.configure("TLabel", font=("Arial", 12), background="white", foreground="black")  # Set the label's style
    style.configure("Header.TLabel", font=("Arial", 24, "bold"), background="#D9D9D9", foreground="black")  # Set the header's style
    style.configure("TEntry", font=("Arial", 14))

    # Header Label
    header_label = ttk.Label(header_frame, text="Dictionary & Thesaurus App", style = "Header.TLabel", background=bg_color)
    header_label.pack(side=tk.LEFT)

    # Search Frame
    search_frame = ttk.Frame(window)
    search_frame.pack(pady=20)

    # Search Input Field
    search_entry = ttk.Entry(search_frame, font=("Arial", 14))
    search_entry.bind('<Return>', lambda event=None: search_button.invoke())  # Bind the Enter key to the search button
    search_entry.pack(side=tk.LEFT, padx=10)

    # Search Button
    search_button = ttk.Button(
        search_frame,
        text="Search",
        command=search_word,
        style="Custom.TButton"
    )
    search_button.pack(side=tk.LEFT, padx=10)

    # Create the Clear History Button
    clear_history_button = ttk.Button(
        search_frame,
        text="Clear History",
        command=clear_search_history,
        style="Custom.TButton"
    )
    clear_history_button.pack(side=tk.LEFT, padx=10)

    # Create the Search History Button
    history_button = ttk.Button(
        search_frame,
        text="Search History",
        command=show_search_history,
        style="Custom.TButton"
    )
    history_button.pack(side=tk.LEFT, padx=10)

    # Footer Label
    # footer_label = ttk.Label(window, text="© 2023 Nicholas Wade's Dictionary & Thesaurus Application", font=("Arial", 10))
    # footer_label.pack(pady=10)

    # Create buttons for synonyms and antonyms
    synonyms_button = ttk.Button(
        window,
        text="Synonyms",
        command=lambda: open_dictionary_website("https://www.wordhippo.com/what-is/another-word-for/"),
        style="Custom.TButton"
    )
    synonyms_button.pack(pady=5)

    antonyms_button = ttk.Button(
        window,
        text="Antonyms",
        command=lambda: open_dictionary_website("https://www.wordhippo.com/what-is/the-opposite-of/"),
        style="Custom.TButton"
    )
    antonyms_button.pack(pady=5)

    # Create the Crossword Helper Button   
    crossword_helper_button = ttk.Button(
    window,
    text="Crossword Helper",
    command=crossword_helper,
    style="Custom.TButton"
)
    crossword_helper_button.pack(pady=5)

    # Fetch Word of the Day
    word_of_day = fetch_random_word()
    if word_of_day:
        display_word_of_the_day(word_of_day)  # unpack the tuple

    # Start the main event loop
    window.mainloop()

if __name__ == "__main__":
    run_dictionary_app()
