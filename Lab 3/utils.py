import json

from data_model import Pokemon

def pokemon_to_dict(pokemon: Pokemon) -> dict:
    return {
        "Id": pokemon.id,
        "DexNumber": pokemon.dex_number,
        "Name": pokemon.name,
        "Type1": pokemon.type_one,
        "Type2": pokemon.type_two,
        "Generation": pokemon.generation,
        "Form": pokemon.form,
        "Total": pokemon.total,
        "HP": pokemon.hp,
        "Attack": pokemon.attack,
        "Defense": pokemon.defense,
        "SpecialAttack": pokemon.special_attack,
        "SpecialDefense": pokemon.special_defense,
        "Speed": pokemon.speed,
    }

def export_pokemon_to_json(data: Pokemon | list[Pokemon], filepath: str | None = None) -> None:
    # The menu offers both formatted console output and UTF-8 JSON file export.
    if isinstance(data, list):
        payload = [pokemon_to_dict(pokemon) for pokemon in data]
        count = len(payload)
    else:
        payload = pokemon_to_dict(data)
        count = 1

    exported_json = json.dumps(payload, indent=2)

    if filepath is None:
        print(exported_json)
        print(f"Exported {count} record(s) to console")
    else:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(exported_json)
        except OSError as e:
            raise RuntimeError(f"Failed to write export file '{filepath}': {e}") from e
        print(f"Exported {count} record(s) to {filepath}")
