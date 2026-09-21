# Lab 03: Database Integration and More JSON

Use Python 3.13 or newer, as required by the lab. Extract the whole folder before running.

```text
python -m pip install -r requirements.txt
python main.py
```

Keep lab_data.db next to the Python files. The program always uses that database,
even when launched from another folder. The database includes the original 151 records.

Use the arrow keys and Enter to select menu options. Read by ID, DexNumber, Name,
either type, or Generation; read all; add; update; delete; or export JSON. Searches
by name and type ignore capitalization. Name and DexNumber searches return every
match, including forms or duplicate entries. Update and delete require confirmation.

Create example (paste a single line):
```json
{"DexNumber": 152, "Name": "Chikorita", "Type1": "Grass", "Type2": null, "Generation": 2}
```

Update example (enter the record ID first):
```json
{"Type2": "Fairy"}
```

Required create fields are DexNumber, Name, Type1, and Generation. Optional fields
are Type2, Form, Total, HP, Attack, Defense, SpecialAttack, SpecialDefense, and Speed.
DexNumber and Generation must be positive integers; stats must be nonnegative
integers. Optional fields accept null. Id is assigned by SQLite and cannot be edited.
The original snake_case field names are also accepted. Exports use database column
names and include every mapped column. Omit Id when reusing an export for creation.

Export either a single record by ID or the whole table to the console or a UTF-8 JSON
file. Relative output paths are relative to the folder from which you ran the program.
Invalid JSON and unsuccessful operations display an error and return to the menu.

## Files
- main.py: interactive menu and update/delete confirmations
- crrud.py: JSON validation and database operations
- data_model.py: ORM mapping for all Pokemon columns
- utils.py: row serialization and JSON export
- lab_data.db: provided SQLite database
- requirements.txt: dependencies

Submit the ZIP to the Lab 03 D2L drop box and be prepared to demonstrate the menu.

## Verification
Automated checks passed for all lookup modes, JSON create/update, duplicate lookups,
invalid inputs, single/full JSON exports, cancellation of update/delete, malformed
JSON handling in the menu, and deletion. Checks used a temporary database copy;
the included database is identical to the supplied file. Tests ran on Python 3.12.14
(the available runtime); the lab requires Python 3.13 or newer for your demonstration.

