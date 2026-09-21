"""Lab 2: Working with Data Structures and DataFrames."""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIRECTORY = Path(__file__).resolve().parent
MOVIES_FILE = BASE_DIRECTORY / "movies.csv"


def load_data(csv_file=MOVIES_FILE):
    """Load movies.csv and return a pandas DataFrame."""
    try:
        movies = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"File not found: {csv_file}")
        return None
    except (OSError, pd.errors.ParserError) as error:
        print(f"Unable to load the movie data: {error}")
        return None

    required_columns = [
        "movie_id",
        "title",
        "year",
        "genre",
        "director",
        "rating",
        "runtime_minutes",
        "box_office_millions",
        "budget_millions",
    ]
    missing_columns = [column for column in required_columns if column not in movies.columns]
    if missing_columns:
        print("Missing required columns: " + ", ".join(missing_columns))
        return None

    return movies


def display_data_summary(movies):
    """Display info, the first and last five rows, and missing-value counts."""
    print("\n--- DATAFRAME INFORMATION ---")
    movies.info()

    print("\n--- FIRST 5 ROWS ---")
    print(movies.head(5).to_string(index=False))

    print("\n--- LAST 5 ROWS ---")
    print(movies.tail(5).to_string(index=False))

    print("\n--- MISSING VALUES ---")
    print(movies.isna().sum().to_string())


def find_top_rated(movies, amount=5):
    """Return the highest-rated movies."""
    return movies.sort_values(
        ["rating", "title"], ascending=[False, True]
    ).head(amount)


def calculate_genre_averages(movies):
    """Return average ratings grouped by genre."""
    return (
        movies.groupby("genre")["rating"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )


def find_movies_by_decade(movies, decade):
    """Return movies released from the first through last year of a decade."""
    last_year = decade + 9
    return movies.loc[movies["year"].between(decade, last_year)].sort_values(
        ["year", "title"]
    )


def find_most_profitable(movies, amount=3):
    """Return movies with the largest box-office-to-budget ratios."""
    valid_budgets = movies.loc[movies["budget_millions"] > 0].copy()
    valid_budgets["box_office_budget_ratio"] = (
        valid_budgets["box_office_millions"]
        / valid_budgets["budget_millions"]
    )
    return valid_budgets.sort_values(
        "box_office_budget_ratio", ascending=False
    ).head(amount)


def find_movies_by_director(movies, director_name):
    """Return every movie by a director using a case-insensitive match."""
    search_name = director_name.strip().casefold()
    if not search_name:
        return movies.iloc[0:0]

    matches = movies["director"].str.casefold() == search_name
    return movies.loc[matches].sort_values(["year", "title"])


def save_json(data, filename):
    """Save a dictionary as an indented JSON file."""
    try:
        with Path(filename).open("w", encoding="utf-8") as output_file:
            json.dump(data, output_file, indent=4, ensure_ascii=False)
    except OSError as error:
        print(f"Could not save {filename}: {error}")
        return False

    print(f"Saved {Path(filename).name}")
    return True


def export_top_movies(movies, amount=5):
    """Export the top-rated movies to top_rated.json."""
    selected = find_top_rated(movies, amount)
    movie_list = []

    for rank, movie in enumerate(selected.itertuples(index=False), start=1):
        movie_list.append(
            {
                "rank": rank,
                "title": movie.title,
                "year": int(movie.year),
                "rating": float(movie.rating),
                "genre": movie.genre,
                "director": movie.director,
            }
        )

    result = {
        "export_info": {
            "export_date": datetime.now().date().isoformat(),
            "criteria": f"Top {amount} rated movies",
            "total_movies": len(movie_list),
        },
        "movies": movie_list,
    }
    save_json(result, BASE_DIRECTORY / "top_rated.json")
    return result


def export_by_genre(movies):
    """Export movie counts, ratings, revenue, and titles grouped by genre."""
    genre_analysis = {}

    for genre, group in movies.groupby("genre", sort=True):
        genre_analysis[genre] = {
            "movie_count": int(group.shape[0]),
            "average_rating": round(float(group["rating"].mean()), 2),
            "total_box_office": round(float(group["box_office_millions"].sum()), 2),
            "movies": group.sort_values("title")["title"].to_list(),
        }

    result = {"genre_analysis": genre_analysis}
    save_json(result, BASE_DIRECTORY / "movies_by_genre.json")
    return result


def export_director_portfolio(movies, director_name):
    """Export all movies by one director to director_filmography.json."""
    selected = find_movies_by_director(movies, director_name)
    movie_list = []

    for movie in selected.itertuples(index=False):
        movie_list.append(
            {
                "movie_id": int(movie.movie_id),
                "title": movie.title,
                "year": int(movie.year),
                "genre": movie.genre,
                "rating": float(movie.rating),
                "runtime_minutes": int(movie.runtime_minutes),
                "box_office_millions": float(movie.box_office_millions),
                "budget_millions": float(movie.budget_millions),
            }
        )

    display_name = selected.iloc[0]["director"] if not selected.empty else director_name.strip()
    result = {
        "export_info": {
            "export_date": datetime.now().date().isoformat(),
            "criteria": f"Movies directed by {display_name}",
            "total_movies": len(movie_list),
        },
        "director": display_name,
        "movies": movie_list,
    }
    save_json(result, BASE_DIRECTORY / "director_filmography.json")
    return result


def display_menu():
    """Display the interactive menu options."""
    print(
        """
========== MOVIE DATA MENU ==========
1. Display data summary
2. Display average ratings by genre
3. Export five top-rated movies to JSON
4. Export movies by genre to JSON
5. Export director filmography to JSON
6. Display top 3 most profitable movies
7. Display movies released in a decade
8. Exit
=====================================
"""
    )


def get_decade_from_user():
    """Prompt until the user provides a valid decade."""
    while True:
        user_entry = input("Enter a decade, such as 1990: ").strip()
        try:
            decade = int(user_entry)
        except ValueError:
            print("Invalid decade. Enter a four-digit year ending in 0.")
            continue

        if 1800 <= decade <= 9990 and decade % 10 == 0:
            return decade
        print("Invalid decade. Enter a four-digit year ending in 0.")


def main():
    """Run the movie analysis menu until the user chooses Exit."""
    movies = load_data()
    if movies is None:
        return

    while True:
        display_menu()
        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            display_data_summary(movies)

        elif choice == "2":
            print("\n--- AVERAGE RATING BY GENRE ---")
            print(calculate_genre_averages(movies).to_string())

        elif choice == "3":
            export_top_movies(movies)

        elif choice == "4":
            export_by_genre(movies)

        elif choice == "5":
            director = input("Enter the director's full name: ").strip()
            matches = find_movies_by_director(movies, director)
            if matches.empty:
                print(f"No movies were found for '{director}'.")
            else:
                export_director_portfolio(movies, director)

        elif choice == "6":
            profitable = find_most_profitable(movies, 3)
            columns = [
                "title",
                "box_office_millions",
                "budget_millions",
                "box_office_budget_ratio",
            ]
            print("\n--- TOP 3 MOST PROFITABLE MOVIES ---")
            print(
                profitable[columns].to_string(
                    index=False,
                    formatters={
                        "box_office_millions": lambda value: f"${value:,.2f}",
                        "budget_millions": lambda value: f"${value:,.2f}",
                        "box_office_budget_ratio": lambda value: f"{value:.2f}",
                    },
                )
            )

        elif choice == "7":
            decade = get_decade_from_user()
            matches = find_movies_by_decade(movies, decade)
            if matches.empty:
                print(f"No movies were found from the {decade}s.")
            else:
                print(f"\n--- MOVIES FROM THE {decade}s ---")
                print(
                    matches[["title", "year", "genre", "director"]].to_string(
                        index=False
                    )
                )

        elif choice == "8":
            print("Program ended.")
            break

        else:
            print("Invalid menu choice. Enter a number from 1 to 8.")


if __name__ == "__main__":
    main()
