from datetime import date

import pytest

CONFLICT = {"detail": "An artwork with that title and artist already exists"}


def test_list_artworks_empty(client):
    response = client.get("/artworks/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_seeded_artwork(client, seeded_db):
    response = client.get("/artworks/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, **seeded_db[0]}


def test_create_artwork(client, sample_artwork):
    response = client.post("/artworks/", json=sample_artwork)
    assert response.status_code == 201
    artwork = response.json()
    assert type(artwork["id"]) is int
    assert artwork == {"id": artwork["id"], **sample_artwork}


def test_create_artwork_is_saved(client, created_artwork):
    response = client.get(f"/artworks/{created_artwork['id']}")
    assert response.status_code == 200
    assert response.json() == created_artwork


def test_update_artwork(client, created_artwork, updated_artwork):
    url = f"/artworks/{created_artwork['id']}"
    expected = {"id": created_artwork["id"], **updated_artwork}
    response = client.put(url, json=updated_artwork)
    assert response.status_code == 200
    assert response.json() == expected
    saved = client.get(url)
    assert saved.status_code == 200
    assert saved.json() == expected


def test_delete_artwork(client, created_artwork):
    url = f"/artworks/{created_artwork['id']}"
    response = client.delete(url)
    assert response.status_code == 204
    assert response.content == b""
    deleted = client.get(url)
    assert deleted.status_code == 404
    assert deleted.json() == {"detail": "Artwork not found"}


@pytest.mark.parametrize(
    "method", ["get", "put", "delete"], ids=["get", "put", "delete"]
)
def test_artwork_not_found(client, sample_artwork, method):
    kwargs = {"json": sample_artwork} if method == "put" else {}
    response = client.request(method, "/artworks/9999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Artwork not found"}


def test_non_integer_id(client):
    response = client.get("/artworks/mona-lisa")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "artwork_id"]


def test_create_duplicate(client, created_artwork, sample_artwork):
    response = client.post("/artworks/", json=sample_artwork)
    assert response.status_code == 409
    assert response.json() == CONFLICT


def test_create_duplicate_ignores_case(client, created_artwork, sample_artwork):
    body = {
        **sample_artwork,
        "title": sample_artwork["title"].upper(),
        "artist": sample_artwork["artist"].lower(),
    }
    response = client.post("/artworks/", json=body)
    assert response.status_code == 409
    assert response.json() == CONFLICT


def test_update_into_duplicate(client, seeded_db):
    body = {
        **seeded_db[1],
        "title": seeded_db[0]["title"],
        "artist": seeded_db[0]["artist"],
    }
    response = client.put("/artworks/2", json=body)
    assert response.status_code == 409
    assert response.json() == CONFLICT
    unchanged = client.get("/artworks/2")
    assert unchanged.status_code == 200
    assert unchanged.json() == {"id": 2, **seeded_db[1]}


def test_update_same_title_and_artist_is_allowed(
    client, created_artwork, sample_artwork
):
    body = {**sample_artwork, "museum": "On loan to another museum"}
    url = f"/artworks/{created_artwork['id']}"
    response = client.put(url, json=body)
    assert response.status_code == 200
    assert response.json() == {"id": created_artwork["id"], **body}
    assert client.get(url).json() == response.json()


@pytest.mark.parametrize(
    "missing_field",
    ["title", "artist", "year", "medium", "museum", "image_url"],
    ids=["title", "artist", "year", "medium", "museum", "image-url"],
)
def test_create_missing_field(client, sample_artwork, missing_field):
    body = sample_artwork.copy()
    del body[missing_field]
    response = client.post("/artworks/", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", missing_field]


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("year", date.today().year + 1),
        ("year", "nineteen-oh-seven"),
        ("title", ""),
        ("artist", ""),
    ],
    ids=["future-year", "year-not-int", "empty-title", "empty-artist"],
)
def test_create_invalid_value(client, sample_artwork, field, bad_value):
    response = client.post("/artworks/", json={**sample_artwork, field: bad_value})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]


@pytest.mark.parametrize(
    "params,expected_count",
    [
        ({}, 10),
        ({"limit": 3}, 3),
        ({"limit": 0}, 0),
        ({"skip": 20}, 0),
        ({"skip": 9, "limit": 3}, 2),
        ({"limit": 100}, 11),
    ],
    ids=["default", "limit-three", "zero-limit", "past-end", "last-page", "all"],
)
def test_pagination_counts(client, seeded_db, params, expected_count):
    response = client.get("/artworks/", params=params)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == expected_count
    skip = params.get("skip", 0)
    expected = [{"id": i + 1, **item} for i, item in enumerate(seeded_db)]
    assert results == expected[skip : skip + params.get("limit", 10)]


@pytest.mark.parametrize(
    "params,field",
    [({"skip": -1}, "skip"), ({"limit": 101}, "limit"), ({"limit": -1}, "limit")],
    ids=["negative-skip", "limit-too-large", "negative-limit"],
)
def test_pagination_invalid(client, params, field):
    response = client.get("/artworks/", params=params)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", field]


@pytest.mark.parametrize(
    "artist,expected_titles",
    [
        (
            "Claude Monet",
            ["Impression, Sunrise", "Woman with a Parasol – Madame Monet and Her Son"],
        ),
        ("da vinci", ["Mona Lisa", "Lady with an Ermine"]),
        ("Unknown Artist", []),
    ],
    ids=["exact", "lowercase-partial", "no-match"],
)
def test_filter_by_artist(client, seeded_db, artist, expected_titles):
    response = client.get("/artworks/", params={"artist": artist})
    assert response.status_code == 200
    assert [artwork["title"] for artwork in response.json()] == expected_titles
