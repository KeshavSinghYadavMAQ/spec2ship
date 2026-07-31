"""Curated static reference pools + deterministic identifier generation (T008, US1, FR-001).

No third-party fake-data library dependency (research.md #1): a small, curated set of
realistic region/city and product category/variant pools, combined deterministically via a
fixed-seed `random.Random`, produces plausible-looking (not random-gibberish) store and SKU
identifiers that are stable across repeated seeding runs given the same batch parameters.
"""

from __future__ import annotations

import random

DEFAULT_RANDOM_SEED = 20240602

# (region_code, city_name) - realistic North American grocery/convenience retail footprint.
REGION_CITIES: list[tuple[str, str]] = [
    ("US-IL", "CHICAGO"),
    ("US-TX", "AUSTIN"),
    ("US-CA", "FRESNO"),
    ("US-NY", "ALBANY"),
    ("US-WA", "SPOKANE"),
    ("US-CO", "DENVER"),
    ("US-GA", "ATLANTA"),
    ("US-OH", "COLUMBUS"),
    ("US-AZ", "TUCSON"),
    ("US-NC", "DURHAM"),
    ("US-MI", "LANSING"),
    ("US-OR", "SALEM"),
    ("US-TN", "MEMPHIS"),
    ("US-MN", "DULUTH"),
    ("US-FL", "TAMPA"),
]

# (category, variant) - realistic grocery/convenience product assortment.
PRODUCT_CATALOG_POOL: list[tuple[str, str]] = [
    ("COFFEE", "12OZ"),
    ("COFFEE", "20OZ"),
    ("TEA", "20CT"),
    ("SNACK", "BAR"),
    ("SNACK", "CHIPS"),
    ("SODA", "12PK"),
    ("SODA", "2LTR"),
    ("CEREAL", "18OZ"),
    ("PASTA", "16OZ"),
    ("RICE", "5LB"),
    ("MILK", "1GAL"),
    ("BREAD", "LOAF"),
    ("EGGS", "DOZEN"),
    ("WATER", "24PK"),
    ("JUICE", "64OZ"),
    ("YOGURT", "32OZ"),
    ("CANDY", "BAG"),
    ("SOUP", "CAN"),
    ("BUTTER", "16OZ"),
    ("PAPERTOWEL", "6PK"),
]


def generate_store_ids(count: int, rng: random.Random) -> list[str]:
    """Deterministic, unique `STORE-{CITY}-{seq:03d}` identifiers (e.g. `STORE-CHICAGO-014`)."""
    cities = [city for _, city in REGION_CITIES]
    per_city_counter: dict[str, int] = {}
    store_ids: list[str] = []
    for _ in range(count):
        city = cities[rng.randrange(len(cities))]
        per_city_counter[city] = per_city_counter.get(city, 0) + 1
        store_ids.append(f"STORE-{city}-{per_city_counter[city]:03d}")
    return store_ids


def store_region_for_id(store_id: str) -> str:
    """Look up the region code for a store id produced by `generate_store_ids`."""
    city = store_id.split("-")[1]
    for region_code, region_city in REGION_CITIES:
        if region_city == city:
            return region_code
    return REGION_CITIES[0][0]


def generate_sku_catalog(count: int) -> list[str]:
    """Deterministic, unique `SKU-{CATEGORY}-{VARIANT}` identifiers. The first occurrence
    of each category/variant pair uses the canonical form (e.g. `SKU-COFFEE-12OZ`);
    subsequent repeats append a running suffix (e.g. `SKU-COFFEE-12OZ-2`) so the catalog
    can scale past the size of the static pool while staying stable/reproducible."""
    sku_ids: list[str] = []
    pair_counter: dict[tuple[str, str], int] = {}
    pool_size = len(PRODUCT_CATALOG_POOL)
    for index in range(count):
        category, variant = PRODUCT_CATALOG_POOL[index % pool_size]
        pair_counter[(category, variant)] = pair_counter.get((category, variant), 0) + 1
        occurrence = pair_counter[(category, variant)]
        if occurrence == 1:
            sku_ids.append(f"SKU-{category}-{variant}")
        else:
            sku_ids.append(f"SKU-{category}-{variant}-{occurrence}")
    return sku_ids


def make_rng(seed: int = DEFAULT_RANDOM_SEED) -> random.Random:
    return random.Random(seed)
