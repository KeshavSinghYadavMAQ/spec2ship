import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

/**
 * WCAG 2.2 AA automated accessibility audit (T108, Constitution IV).
 *
 * Scans the alert worklist, recommendation review panel, transfer approval workflow, and
 * KPI dashboard — the core operational surfaces called out in the task — using axe-core.
 * This automated pass complements, but does not replace, manual keyboard/screen-reader
 * review noted in quickstart.md.
 */
const AUDITED_ROUTES = [
  { path: "/alerts", label: "Alert worklist" },
  { path: "/replenishment", label: "Recommendation review panel" },
  { path: "/transfers", label: "Transfer approval workflow" },
  { path: "/store-priority", label: "Store priority ranking view" },
  { path: "/analytics", label: "KPI dashboard" },
  { path: "/admin/policies", label: "Admin threshold panel" },
];

for (const route of AUDITED_ROUTES) {
  test(`${route.label} has no automatically detectable WCAG 2.2 AA violations`, async ({
    page,
  }) => {
    await page.goto(route.path);
    await expect(page.getByRole("heading", { name: "Retail Replenishment" })).toBeVisible();

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
      .analyze();

    expect(
      results.violations,
      `Accessibility violations on ${route.path}:\n${JSON.stringify(results.violations, null, 2)}`,
    ).toEqual([]);
  });
}
