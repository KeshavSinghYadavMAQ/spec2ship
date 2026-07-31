import { expect, test } from "@playwright/test";

const ROUTES = [
  { path: "/inventory", labels: ["SKU rows", "Total units"] },
  { path: "/alerts", labels: ["Total alerts", "Open alerts"] },
  { path: "/transfers", labels: ["Suggestions", "Feasible"] },
];

for (const route of ROUTES) {
  test(`kpi summary is readable within 5s on ${route.path}`, async ({ page }) => {
    const start = Date.now();
    await page.goto(route.path);
    for (const label of route.labels) {
      await expect(page.getByText(label)).toBeVisible();
    }
    expect(Date.now() - start).toBeLessThanOrEqual(5_000);
  });
}
