import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

/**
 * Theme-parity harness (T044, US4, FR-010, FR-013). Runs an automated WCAG 2.2 AA
 * contrast/accessibility audit (axe-core) against every in-scope screen in BOTH the
 * light theme (default) and the dark theme (after toggling), since the colorful
 * `brandVariants`/`statusTokens` palette (T010, T011, T045) must hold up in both.
 *
 * Happy path: no automatically detectable contrast violations in either theme.
 * Failure path: a low-contrast element would surface as an axe `color-contrast`
 * violation, failing the assertion below with the violating selector(s).
 * Edge case: status indicators remain legible (icon + text label, not color alone) in
 * both themes - covered by the shared `StatusBadge` component (T036) already asserted
 * in `test_shared_components_consistency.test.tsx`.
 */
const AUDITED_ROUTES = [
  { path: "/inventory", label: "Inventory" },
  { path: "/alerts", label: "Alert worklist" },
  { path: "/replenishment", label: "Recommendation review panel" },
  { path: "/forecasts", label: "Demand forecasts" },
  { path: "/transfers", label: "Transfer suggestions" },
  { path: "/analytics", label: "KPI dashboard" },
  { path: "/admin/policies", label: "Admin threshold panel" },
  { path: "/admin/sample-data", label: "Sample data panel" },
];

async function toggleToDarkMode(page: Page) {
  const toggle = page.getByRole("button", { name: /switch to dark mode/i });
  await toggle.click();
  await expect(page.getByRole("button", { name: /switch to light mode/i })).toBeVisible();
}

for (const route of AUDITED_ROUTES) {
  test(`${route.label} has no WCAG 2.2 AA contrast violations in light mode`, async ({ page }) => {
    await page.goto(route.path);
    await expect(page.getByRole("heading", { name: "Retail Replenishment" })).toBeVisible();

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2aa", "wcag22aa"])
      .analyze();

    expect(
      results.violations,
      `Light-mode contrast violations on ${route.path}:\n${JSON.stringify(results.violations, null, 2)}`,
    ).toEqual([]);
  });

  test(`${route.label} has no WCAG 2.2 AA contrast violations in dark mode`, async ({ page }) => {
    await page.goto(route.path);
    await expect(page.getByRole("heading", { name: "Retail Replenishment" })).toBeVisible();
    await toggleToDarkMode(page);

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2aa", "wcag22aa"])
      .analyze();

    expect(
      results.violations,
      `Dark-mode contrast violations on ${route.path}:\n${JSON.stringify(results.violations, null, 2)}`,
    ).toEqual([]);
  });
}
