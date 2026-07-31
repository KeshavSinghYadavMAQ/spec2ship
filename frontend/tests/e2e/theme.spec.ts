import { expect, test, type Page } from "@playwright/test";

const ROUTES = [
  { path: "/inventory", label: "Inventory" },
  { path: "/alerts", label: "Alerts" },
  { path: "/replenishment", label: "Replenishment" },
  { path: "/admin/policies", label: "Admin" },
  { path: "/analytics", label: "Analytics" },
];

const VIEWPORTS = [
  { name: "mobile", width: 390, height: 844 },
  { name: "tablet", width: 834, height: 1112 },
  { name: "desktop", width: 1440, height: 900 },
];

async function currentBackgroundColor(page: Page): Promise<string> {
  return page.evaluate(() => {
    const root = document.getElementById("root")?.firstElementChild;
    return root ? getComputedStyle(root).backgroundColor : "";
  });
}

test.describe("Theme and responsiveness (T100, dashboards/admin/alert worklist)", () => {
  test("toggles between light and dark mode and changes the rendered background", async ({
    page,
  }) => {
    await page.goto("/alerts");

    const toggle = page.getByRole("button", { name: /switch to (dark|light) mode/i });
    await expect(toggle).toBeVisible();

    const beforeColor = await currentBackgroundColor(page);
    await toggle.click();
    await expect(page.getByRole("button", { name: /switch to (dark|light) mode/i })).toBeVisible();

    const afterColor = await currentBackgroundColor(page);
    expect(afterColor).not.toBe(beforeColor);

    // Toggling back returns to the original theme.
    await page.getByRole("button", { name: /switch to (dark|light) mode/i }).click();
    const restoredColor = await currentBackgroundColor(page);
    expect(restoredColor).toBe(beforeColor);
  });

  test("theme preference persists across navigation", async ({ page }) => {
    await page.goto("/inventory");
    const toggle = page.getByRole("button", { name: /switch to (dark|light) mode/i });
    const initialLabel = await toggle.getAttribute("aria-label");
    await toggle.click();
    const toggledLabel = await toggle.getAttribute("aria-label");
    expect(toggledLabel).not.toBe(initialLabel);

    await page.getByRole("link", { name: "Analytics" }).click();
    await expect(page).toHaveURL(/\/analytics$/);
    const labelAfterNav = await page
      .getByRole("button", { name: /switch to (dark|light) mode/i })
      .getAttribute("aria-label");
    expect(labelAfterNav).toBe(toggledLabel);
  });

  for (const viewport of VIEWPORTS) {
    for (const route of ROUTES) {
      test(`renders ${route.label} without horizontal overflow at ${viewport.name} width`, async ({
        page,
      }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto(route.path);

        await expect(page.getByRole("heading", { name: "Retail Replenishment" })).toBeVisible();

        const hasHorizontalOverflow = await page.evaluate(
          () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        );
        expect(hasHorizontalOverflow).toBe(false);
      });
    }
  }
});
