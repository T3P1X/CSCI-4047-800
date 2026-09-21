import json
from pathlib import Path

from sqlalchemy import create_engine, select, or_, func, URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from data_model import Pokemon, Base

CONNECTION_STRING = URL.create("sqlite", database=str(Path(__file__).with_name("lab_data.db")))
engine = create_engine(CONNECTION_STRING)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)

REQUIRED_CREATE_FIELDS = {
    "dex_number": int,
    "name": str,
    "type_one": str,
    "generation": int,
}
OPTIONAL_FIELDS = {"type_two": str, "form": str, "total": int, "hp": int,
                   "attack": int, "defense": int, "special_attack": int,
                   "special_defense": int, "speed": int}
UPDATABLE_FIELDS = {**REQUIRED_CREATE_FIELDS, **OPTIONAL_FIELDS}
JSON_FIELDS = {"DexNumber": "dex_number", "Name": "name", "Type1": "type_one",
               "Type2": "type_two", "Generation": "generation", "Form": "form",
               "Total": "total", "HP": "hp", "Attack": "attack", "Defense": "defense",
               "SpecialAttack": "special_attack", "SpecialDefense": "special_defense",
               "Speed": "speed"}


def _parse_json_object(raw_json: str) -> dict:
    """Parse `raw_json` into a dict, raising ValueError with a friendly message on failure."""
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON ({e.msg} at line {e.lineno}, column {e.colno})") from e
    if not isinstance(parsed, dict):
        raise ValueError("JSON input must be an object (e.g. {\"name\": \"Pikachu\"})")
    normalized = {}
    for key, value in parsed.items():
        field = JSON_FIELDS.get(key, key)
        if field in normalized:
            raise ValueError(f"Field '{field}' was provided more than once")
        normalized[field] = value
    return normalized


def _validate_create_fields(fields: dict) -> dict:
    missing = [key for key in REQUIRED_CREATE_FIELDS if key not in fields]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")

    unknown = [key for key in fields if key not in UPDATABLE_FIELDS]
    if unknown:
        raise ValueError(f"Unknown field(s): {', '.join(unknown)}")

    return _validate_field_types(fields)


def _validate_update_fields(fields: dict) -> dict:
    if not fields:
        raise ValueError("No fields provided to update")

    unknown = [key for key in fields if key not in UPDATABLE_FIELDS]
    if unknown:
        raise ValueError(f"Unknown field(s): {', '.join(unknown)}")

    return _validate_field_types(fields)


def _validate_field_types(fields: dict) -> dict:
    validated = dict(fields)
    for key, value in fields.items():
        expected_type = UPDATABLE_FIELDS[key]
        if key in OPTIONAL_FIELDS and value is None:
            continue
        if type(value) is not expected_type:
            raise ValueError(f"Field '{key}' must be of type {expected_type.__name__}, got {type(value).__name__}")
        if expected_type is str:
            validated[key] = value.strip()
            if not validated[key]:
                if key in OPTIONAL_FIELDS:
                    validated[key] = None
                else:
                    raise ValueError(f"Field '{key}' must not be empty")
        elif value < (1 if key in ("dex_number", "generation") else 0):
            raise ValueError(f"Field '{key}' is outside its allowed range")
    return validated


def _parse_positive_int(value, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f"{field_name} must be a whole number")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number")
    if parsed < 1:
        raise ValueError(f"{field_name} must be a positive number")
    return parsed


def create_pokemon(create_json: str) -> Pokemon:
    fields = _validate_create_fields(_parse_json_object(create_json))
    pokemon = Pokemon(**fields)
    try:
        with Session() as session:
            session.add(pokemon)
            session.commit()
            session.refresh(pokemon)
            session.expunge(pokemon)
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to create Pokemon: {e}") from e
    return pokemon


def read_pokemon_by_id(id) -> Pokemon | None:
    id = _parse_positive_int(id, "ID")
    try:
        with Session() as session:
            statement = select(Pokemon).filter_by(id=id)
            return session.scalars(statement).one_or_none()
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to read Pokemon by ID: {e}") from e


def read_pokemon_by_dex_number(dex_number) -> list[Pokemon]:
    dex_number = _parse_positive_int(dex_number, "Dex Number")
    try:
        with Session() as session:
            statement = select(Pokemon).filter_by(dex_number=dex_number)
            return list(session.scalars(statement).all())
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to read Pokemon by Dex Number: {e}") from e


def read_pokemon_by_name(name: str) -> list[Pokemon]:
    if not name or not name.strip():
        raise ValueError("Name must not be empty")
    try:
        with Session() as session:
            statement = select(Pokemon).where(func.lower(Pokemon.name) == name.strip().lower())
            return list(session.scalars(statement).all())
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to read Pokemon by name: {e}") from e


def read_pokemon_by_type(type_name: str) -> list[Pokemon]:
    if not type_name or not type_name.strip():
        raise ValueError("Type must not be empty")
    try:
        with Session() as session:
            type_name = type_name.strip().lower()
            statement = select(Pokemon).where(or_(func.lower(Pokemon.type_one) == type_name, func.lower(Pokemon.type_two) == type_name))
            return list(session.scalars(statement).all())
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to read Pokemon by type: {e}") from e


def read_pokemon_by_generation(generation) -> list[Pokemon]:
    generation = _parse_positive_int(generation, "Generation")
    try:
        with Session() as session:
            statement = select(Pokemon).filter_by(generation=generation)
            return list(session.scalars(statement).all())
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to read Pokemon by generation: {e}") from e


def read_all_pokemon() -> list[Pokemon]:
    try:
        with Session() as session:
            return list(session.scalars(select(Pokemon)).all())
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to read Pokemon: {e}") from e


def update_pokemon(id, updates_json: str) -> Pokemon:
    id = _parse_positive_int(id, "ID")
    updates = _validate_update_fields(_parse_json_object(updates_json))
    try:
        with Session() as session:
            statement = select(Pokemon).filter_by(id=id)
            pokemon = session.scalars(statement).one_or_none()
            if pokemon is None:
                raise ValueError(f"No Pokemon found with ID = {id}")
            for key, value in updates.items():
                setattr(pokemon, key, value)
            session.commit()
            session.refresh(pokemon)
            session.expunge(pokemon)
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to update Pokemon: {e}") from e
    return pokemon


def delete_pokemon(id) -> Pokemon:
    id = _parse_positive_int(id, "ID")
    try:
        with Session() as session:
            statement = select(Pokemon).filter_by(id=id)
            pokemon_to_delete = session.scalars(statement).one_or_none()
            if pokemon_to_delete is None:
                raise ValueError(f"No Pokemon found with ID = {id}")
            session.delete(pokemon_to_delete)
            session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to delete Pokemon: {e}") from e
    return pokemon_to_delete
