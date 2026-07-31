"""Unit tests for the reference-data generator (T051, US1, FR-001).

Covers determinism, uniqueness, format, and region look-up behavior of
`generate_store_ids`, `generate_sku_catalog`, `store_region_for_id`, and `make_rng`.
"""

from __future__ import annotations

from src.domain.sample_data.reference_data import (
    REGION_CITIES,
    generate_sku_catalog,
    generate_store_ids,
    make_rng,
    store_region_for_id,
)


def test_make_rng_is_deterministic_for_the_same_seed():
    first = make_rng(42)
    second = make_rng(42)
    assert [first.random() for _ in range(5)] == [second.random() for _ in range(5)]


def test_make_rng_default_seed_produces_stable_results_across_calls():
    first_ids = generate_store_ids(10, make_rng())
    second_ids = generate_store_ids(10, make_rng())
    assert first_ids == second_ids


def test_generate_store_ids_returns_requested_count():
    store_ids = generate_store_ids(25, make_rng())
    assert len(store_ids) == 25


def test_generate_store_ids_are_unique():
    store_ids = generate_store_ids(200, make_rng())
    assert len(set(store_ids)) == len(store_ids)


def test_generate_store_ids_match_expected_format():
    store_ids = generate_store_ids(5, make_rng())
    known_cities = {city for _, city in REGION_CITIES}
    for store_id in store_ids:
        parts = store_id.split("-")
        assert parts[0] == "STORE"
        assert parts[1] in known_cities
        assert parts[2].isdigit()
        assert len(parts[2]) == 3


def test_generate_store_ids_zero_count_returns_empty_list():
    assert generate_store_ids(0, make_rng()) == []


def test_store_region_for_id_resolves_known_city():
    store_ids = generate_store_ids(1, make_rng())
    region = store_region_for_id(store_ids[0])
    city = store_ids[0].split("-")[1]
    assert (region, city) in REGION_CITIES


def test_store_region_for_id_falls_back_for_unknown_city():
    assert store_region_for_id("STORE-UNKNOWNCITY-001") == REGION_CITIES[0][0]


def test_generate_sku_catalog_returns_requested_count():
    catalog = generate_sku_catalog(50)
    assert len(catalog) == 50


def test_generate_sku_catalog_is_unique_even_beyond_pool_size():
    # The static pool has 20 (category, variant) pairs; requesting more than that forces
    # repeats, which must be disambiguated with a numeric suffix to stay unique.
    catalog = generate_sku_catalog(45)
    assert len(set(catalog)) == len(catalog)


def test_generate_sku_catalog_first_occurrence_uses_canonical_form():
    catalog = generate_sku_catalog(1)
    assert catalog[0] == "SKU-COFFEE-12OZ"


def test_generate_sku_catalog_repeat_occurrence_uses_numeric_suffix():
    # Pool size is 20, so index 20 repeats the first pair (COFFEE, 12OZ) as its 2nd occurrence.
    catalog = generate_sku_catalog(21)
    assert catalog[0] == "SKU-COFFEE-12OZ"
    assert catalog[20] == "SKU-COFFEE-12OZ-2"


def test_generate_sku_catalog_is_deterministic_across_calls():
    assert generate_sku_catalog(500) == generate_sku_catalog(500)


def test_generate_sku_catalog_zero_count_returns_empty_list():
    assert generate_sku_catalog(0) == []
