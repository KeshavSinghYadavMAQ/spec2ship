import { expect, test } from "@playwright/test";

/**
 * Frontend responsiveness at pilot-scale data volumes (T050, SC-008).
 *
 * Running a full 1,000-store / 100,000-SKU seed against a live backend for every test run
 * is impractical (backend harness measures ~20+ minutes for the full pilot scale — see
 * `backend/tests/harness/sample_data/test_seed_performance.py`, T049). Instead, this spec
 * intercepts the relevant API calls and returns large, representative pilot-scale-sized
 * payloads directly, then verifies each screen renders within a bounded time budget with no
 * unhandled page errors — validating "no unhandled slowdowns or failures" at scale without
 * requiring a fully-seeded live backend.
 */

const RENDER_BUDGET_MS = 10_000;

function makeAlerts(count: number) {
  return Array.from({ length: count }, (_, i) => ({
    id: `alert-${i}`,
    sku_id: `SKU-${(i % 100_000).toString().padStart(6, "0")}`,
    location_id: `STORE-${(i % 1_000).toString().padStart(4, "0")}`,
    severity: i % 3 === 0 ? "out_of_stock" : "low_stock",
    status: "Open",
    owner_user_id: null,
    routing_channel: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }));
}

function makeInventoryPositions(count: number) {
  return Array.from({ length: count }, (_, i) => ({
    id: `pos-${i}`,
    sku_id: `SKU-${(i % 100_000).toString().padStart(6, "0")}`,
    location_id: `STORE-${(i % 1_000).toString().padStart(4, "0")}`,
    shelf_quantity: i % 80,
    backroom_quantity: i % 40,
    reconciled_total: (i % 80) + (i % 40),
    freshness_at: new Date().toISOString(),
    data_freshness_warning: i % 10 === 0,
  }));
}

test.describe("Pilot-scale data volume responsiveness", () => {
  test("alert worklist renders a large (2,500-row) pilot-scale result set without unhandled errors", async ({
    page,
  }) => {
    const pageErrors: Error[] = [];
    page.on("pageerror", (err) => pageErrors.push(err));

    await page.route("**/v1/alerts*", (route) =>
      route.fulfill({ json: makeAlerts(2_500) }),
    );

    const started = Date.now();
    await page.goto("/alerts");
    await expect(page.getByRole("heading", { name: "Alert Worklist" })).toBeVisible();
    await expect(page.getByRole("table", { name: "Stock alerts" })).toBeVisible();
    await expect(page.getByRole("row")).toHaveCount(2_501, { timeout: RENDER_BUDGET_MS });
    const elapsed = Date.now() - started;

    expect(elapsed, `Alert worklist took ${elapsed}ms to render 2,500 rows`).toBeLessThan(
      RENDER_BUDGET_MS,
    );
    expect(pageErrors).toEqual([]);
  });

  test("inventory position view renders a large (5,000-row) pilot-scale result set without unhandled errors", async ({
    page,
  }) => {
    const pageErrors: Error[] = [];
    page.on("pageerror", (err) => pageErrors.push(err));

    await page.route("**/v1/inventory/positions*", (route) =>
      route.fulfill({ json: makeInventoryPositions(5_000) }),
    );

    const started = Date.now();
    await page.goto("/inventory");
    await expect(page.getByRole("heading", { name: "Inventory Positions" })).toBeVisible();
    await expect(page.getByRole("table", { name: "Inventory positions" })).toBeVisible();
    await expect(page.getByRole("row")).toHaveCount(5_001, { timeout: RENDER_BUDGET_MS });
    const elapsed = Date.now() - started;

    expect(elapsed, `Inventory position view took ${elapsed}ms to render 5,000 rows`).toBeLessThan(
      RENDER_BUDGET_MS,
    );
    expect(pageErrors).toEqual([]);
  });
});
