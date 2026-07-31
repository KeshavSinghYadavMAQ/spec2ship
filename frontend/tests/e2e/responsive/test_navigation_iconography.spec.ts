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
  test(`navigation icon pills remain scanable on ${route}`, async ({ page }) => {
    await page.goto(route);
    await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();

    const links = page.getByRole("navigation", { name: "Primary" }).getByRole("link");
    const count = await links.count();
    for (let i = 0; i < count; i += 1) {
      await expect(links.nth(i).locator("svg")).toBeVisible();
    }
  });
}
