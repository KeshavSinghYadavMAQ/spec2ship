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
  test(`light theme redesign chrome is present on ${route}`, async ({ page }) => {
    await page.goto(route);
    await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
    await expect(page.getByRole("button", { name: /switch to dark mode/i })).toBeVisible();
  });
}
