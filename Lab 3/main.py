import json

import questionary

from crrud import (
    create_pokemon,
    delete_pokemon,
    read_all_pokemon,
    read_pokemon_by_dex_number,
    read_pokemon_by_generation,
    read_pokemon_by_id,
    read_pokemon_by_name,
    read_pokemon_by_type,
    update_pokemon,
)
from utils import export_pokemon_to_json, pokemon_to_dict

MAIN_MENU_CHOICES = [
    "Read all Pokemon",
    "Read a Pokemon",
    "Add a Pokemon",
    "Update a Pokemon",
    "Delete a Pokemon",
    "Export Pokemon to JSON",
    "Exit",
]

READ_MENU_CHOICES = ["ID", "Dex Number", "Name", "Type", "Generation", "Back"]


def print_pokemon(pokemon) -> None:
    print(json.dumps(pokemon_to_dict(pokemon)) if pokemon is not None else "No Pokemon found")


def print_pokemon_list(pokemon_list) -> None:
    if not pokemon_list:
        print("No Pokemon found")
        return
    for pokemon in pokemon_list:
        print_pokemon(pokemon)


def read_menu() -> None:
    field = questionary.select("Read Pokemon by:", choices=READ_MENU_CHOICES).ask()
    if field is None or field == "Back":
        return

    try:
        if field == "ID":
            value = questionary.text("Enter the ID:").ask()
            if value is None:
                return
            print_pokemon(read_pokemon_by_id(value))
        elif field == "Dex Number":
            value = questionary.text("Enter the Dex Number:").ask()
            if value is None:
                return
            print_pokemon_list(read_pokemon_by_dex_number(value))
        elif field == "Name":
            value = questionary.text("Enter the Name:").ask()
            if value is None:
                return
            print_pokemon_list(read_pokemon_by_name(value))
        elif field == "Type":
            value = questionary.text("Enter the Type:").ask()
            if value is None:
                return
            print_pokemon_list(read_pokemon_by_type(value))
        elif field == "Generation":
            value = questionary.text("Enter the Generation:").ask()
            if value is None:
                return
            print_pokemon_list(read_pokemon_by_generation(value))
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")


def create_menu() -> None:
    raw_json = questionary.text(
        "Paste the JSON for the new Pokemon "
        '(e.g. {"DexNumber": 25, "Name": "Pikachu", "Type1": "Electric", "Type2": null, "Generation": 1}):'
    ).ask()
    if raw_json is None or not raw_json.strip():
        print("Create cancelled")
        return

    try:
        pokemon = create_pokemon(raw_json)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        return

    print(f"Created: {json.dumps(pokemon_to_dict(pokemon))}")


def update_menu() -> None:
    id_value = questionary.text("Enter the ID of the Pokemon you want to update:").ask()
    if id_value is None:
        print("Update cancelled")
        return

    try:
        existing = read_pokemon_by_id(id_value)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        return
    if existing is None:
        print(f"No Pokemon found with ID = {id_value}")
        return
    print(f"Current record: {json.dumps(pokemon_to_dict(existing))}")

    raw_json = questionary.text('Paste JSON with only the fields to change (e.g. {"Type1": "Fire"}):').ask()
    if raw_json is None or not raw_json.strip():
        print("Update cancelled")
        return

    if not questionary.confirm(f"Confirm update to {existing.name} (ID {existing.id})?", default=False).ask():
        print("Update cancelled")
        return

    try:
        pokemon = update_pokemon(id_value, raw_json)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        return

    print(f"Updated: {json.dumps(pokemon_to_dict(pokemon))}")


def delete_menu() -> None:
    id_value = questionary.text("Enter the ID of the Pokemon you want to delete:").ask()
    if id_value is None:
        print("Delete cancelled")
        return

    try:
        existing = read_pokemon_by_id(id_value)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        return
    if existing is None:
        print(f"No Pokemon found with ID = {id_value}")
        return

    if not questionary.confirm(f"Confirm DELETE on {existing.name} (ID {existing.id})?", default=False).ask():
        print("Delete cancelled")
        return

    try:
        pokemon = delete_pokemon(id_value)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        return

    print(f"Deleted: {json.dumps(pokemon_to_dict(pokemon))}")


def export_menu() -> None:
    scope = questionary.select(
        "Export which records?",
        choices=["All Pokemon", "A single Pokemon (by ID)", "Back"],
    ).ask()
    if scope is None or scope == "Back":
        return

    try:
        if scope == "All Pokemon":
            data = read_all_pokemon()
        else:
            id_value = questionary.text("Enter the ID of the Pokemon to export:").ask()
            if id_value is None:
                print("Export cancelled")
                return
            data = read_pokemon_by_id(id_value)
            if data is None:
                print(f"No Pokemon found with ID = {id_value}")
                return
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        return

    destination = questionary.select("Export to:", choices=["Console", "File"]).ask()
    if destination is None:
        print("Export cancelled")
        return

    filepath = None
    if destination == "File":
        filepath = questionary.text("Enter the output file path:", default="pokemon_export.json").ask()
        if filepath is None or not filepath.strip():
            print("Export cancelled")
            return

    try:
        export_pokemon_to_json(data, filepath)
    except RuntimeError as e:
        print(f"Error: {e}")


def main_menu_choice() -> str | None:
    return questionary.select("What would you like to do?", choices=MAIN_MENU_CHOICES).ask()


if __name__ == "__main__":
    while True:
        choice = main_menu_choice()

        if choice is None or choice == "Exit":
            print("Bye!")
            break
        elif choice == "Read all Pokemon":
            try:
                print_pokemon_list(read_all_pokemon())
            except RuntimeError as e:
                print(f"Error: {e}")
        elif choice == "Read a Pokemon":
            read_menu()
        elif choice == "Add a Pokemon":
            create_menu()
        elif choice == "Update a Pokemon":
            update_menu()
        elif choice == "Delete a Pokemon":
            delete_menu()
        elif choice == "Export Pokemon to JSON":
            export_menu()

        print()
