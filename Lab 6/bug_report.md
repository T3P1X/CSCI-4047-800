# Bug report

Each bug was introduced separately, tested, and undone before the next run.

| Bug | Test(s) that failed or errored during fixture setup |
| --- | --- |
| 1: POST returns 200 instead of 201 | `test_create_artwork`, `test_create_artwork_is_saved`, `test_update_artwork`, `test_delete_artwork`, `test_create_duplicate`, `test_create_duplicate_ignores_case`, `test_update_same_title_and_artist_is_allowed` |
| 2: Duplicate check is case-sensitive | `test_create_duplicate_ignores_case` |
| 3: Artwork counts as its own duplicate | `test_update_same_title_and_artist_is_allowed` |
| 4: DELETE does not delete | `test_delete_artwork` |
| 5: Artist filter only matches the start | `test_filter_by_artist[lowercase-partial]` |

Bug 1 also causes fixture setup errors because `created_artwork` correctly requires 201.

Final verification: **37 passed**, with all five bugs undone. The router matches the starter byte for byte. The SHA-256 of `artworks.db` was unchanged before and after testing: `6246e2cdace2fef91036909be9ef143e64fdcc07c965b3028dc6103480328693`.

The test client deliberately skips the production lifespan: that lifespan calls `populate()` against the real database. Requests instead use the overridden in-memory database, reset before every test. No application source changes are needed.
