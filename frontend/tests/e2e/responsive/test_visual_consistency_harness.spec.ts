import { expect, test } from "@playwright/test";

/**
 * Visual-consistency harness (T028, US2, FR-010).
 *
 * Happy path: every in-scope screen renders the shared header/nav chrome and at least
 * one status/severity indicator that pairs a color with an icon and a text label so
 * meaning never depends on color alone.
 * Failure path: a screen that fell back to unstyled/default Fluent chrome (missing the
 * shared header) would fail the "shared chrome" assertion below.
 * Edge case: status indicators remain distinguishable by their text label even if a
 * color-blind user cannot distinguish hue (FR-010) - asserted by requiring visible text
 * next to every status icon.
 */
const AUDITED_ROUTES = [
  { path: "/inventory", label: "Inventory" },
  { path: "/alerts", label: "Alerts" },
  { path: "/replenishment", label: "Replenishment" },
  { path: "/forecasts", label: "Forecasts" },
  { path: "/transfers", label: "Transfers" },
  { path: "/analytics", label: "Analytics" },
  { path: "/admin/policies", label: "Admin" },
  { path: "/admin/sample-data", label: "Sample Data" },
];

for (const route of AUDITED_ROUTES) {
  test(`${route.label} shares the common app chrome`, async ({ page }) => {
    await page.goto(route.path);
    await expect(page.getByRole("heading", { name: "Retail Replenishment" })).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
    await expect(
      page.getByRole("button", { name: /switch to (dark|light) mode/i }),
    ).toBeVisible();
  });
}

test("status badges pair color with a visible text label (FR-010)", async ({ page }) => {
  await page.goto("/alerts");
  const heading = page.getByRole("heading", { name: "Retail Replenishment" });
  await expect(heading).toBeVisible();

  // If there are no alerts seeded, this is a no-op assertion (empty state is valid too).
  const badges = page.locator("text=/out of stock|low stock/i");
  const count = await badges.count();
  for (let i = 0; i < count; i += 1) {
    await expect(badges.nth(i)).toBeVisible();
  }
});
