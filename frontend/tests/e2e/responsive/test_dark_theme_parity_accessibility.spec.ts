import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const ROUTES = [
  "/inventory",
  "/alerts",
  "/replenishment",
  "/forecasts",
  "/transfers",
  "/store-priority",
  "/analytics",
  "/admin/policies",
  "/admin/sample-data",
];

for (const route of ROUTES) {
  test(`dark mode contrast baseline on ${route}`, async ({ page }) => {
    await page.goto(route);
    await page.getByRole("button", { name: /switch to dark mode/i }).click();
    await expect(page.getByRole("button", { name: /switch to light mode/i })).toBeVisible();

    const results = await new AxeBuilder({ page }).withTags(["wcag2aa", "wcag22aa"]).analyze();
    expect(results.violations).toEqual([]);
  });
}
