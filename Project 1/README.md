# Number Data Manager

This console application stores numbers, displays them in a pandas DataFrame,
calculates basic statistics, and saves or reloads the data from a JSON file.

## Running the program

Install the dependency and start the menu from this folder:

```text
python -m pip install -r requirements.txt
python main.py
```

The program loads `numbers.json` when it starts. Menu option 6 saves the current
numbers to that file, and option 7 reloads it.

## Where the lab criteria are met

- **Variables:** `main.py` creates `manager`, `choice`, and `number`; the class
  also creates values such as `total`, `average`, `minimum`, and `maximum`.
- **Data structures:** `NumberManager.numbers` is a list, while `display()`
  creates and returns a pandas DataFrame.
- **Functions:** `display_menu()` and `main()` are defined in `main.py`, and the
  class methods return values where appropriate.
- **Classes, objects, and modules:** `data_manager.py` is a custom module.
  `NumberManager` inherits from the `UserA` abstract base class, and `main.py`
  creates a `NumberManager` object and calls its methods.
- **Error handling:** startup and reload handle a missing file
  (`FileNotFoundError`), malformed JSON (`JSONDecodeError`), invalid saved data
  (`ValueError`). The Add and Remove options also handle invalid user input
  without ending the program.
- **File I/O:** `save_data()` writes the number list to `numbers.json`, and
  `load_data()` reads that JSON data back into the application.
- **User interface:** `main.py` keeps displaying an eight-option console menu
  until the user chooses Exit.

## Attribution

The DataFrame and JSON implementation was developed with OpenAI Codex assistance
and uses the official pandas and Python documentation:

- <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html>
- <https://docs.python.org/3/library/json.html>
