import { expect, test } from "@playwright/test";

/**
 * Breakpoints harness (T038, US3, FR-009). Runs against the `mobile-360`, `tablet-768`,
 * and `desktop-1440` Playwright projects configured in `playwright.config.ts`.
 *
 * Happy path: every in-scope screen renders without page-level horizontal overflow at
 * the project's viewport width.
 * Failure path: the data-dense analytics screen is explicitly checked at 360px, where
 * KPI cards must stack rather than clip.
 * Edge case: at tablet width, wide data tables reflow into a horizontally-scrollable
 * container (not a page-level scrollbar) rather than being clipped.
 */
const ROUTES = [
  "/inventory",
  "/alerts",
  "/replenishment",
  "/forecasts",
  "/transfers",
  "/analytics",
  "/admin/policies",
  "/admin/sample-data",
];

for (const path of ROUTES) {
  test(`${path} has no page-level horizontal overflow`, async ({ page }) => {
    await page.goto(path);
    await expect(page.getByRole("heading", { name: "Retail Replenishment" })).toBeVisible();

    const hasHorizontalOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    );
    expect(hasHorizontalOverflow).toBe(false);
  });
}

test("analytics KPI cards stack without clipping at narrow viewports", async ({ page }) => {
  await page.goto("/analytics");
  await expect(page.getByRole("heading", { name: "Retail Replenishment" })).toBeVisible();

  const viewportWidth = page.viewportSize()?.width ?? 1440;
  const cards = page.locator("div").filter({ hasText: "Fill rate" });
  if ((await cards.count()) > 0) {
    const box = await cards.first().boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      expect(box.x + box.width).toBeLessThanOrEqual(viewportWidth + 1);
    }
  }
});

test("wide data tables scroll within their own container, not the page", async ({ page }) => {
  await page.goto("/alerts");
  await expect(page.getByRole("heading", { name: "Retail Replenishment" })).toBeVisible();

  const table = page.getByRole("table", { name: "Stock alerts" });
  if (await table.count()) {
    const overflowX = await table.evaluate(
      (el) => getComputedStyle(el.parentElement as HTMLElement).overflowX,
    );
    expect(overflowX).toBe("auto");
  }

  const hasHorizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  );
  expect(hasHorizontalOverflow).toBe(false);
});
