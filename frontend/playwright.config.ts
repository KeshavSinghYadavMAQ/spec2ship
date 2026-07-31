import { defineConfig, devices } from "@playwright/test";

/**
 * Viewport projects (T003, US3, FR-009): 360px mobile minimum, 768px tablet, 1440px
 * desktop. Responsive/breakpoint specs under `tests/e2e/responsive/` run once per
 * project; `@axe-core/playwright` (see `tests/e2e/accessibility.spec.ts` and
 * `tests/e2e/responsive/test_theme_parity_harness.spec.ts`) runs against whichever
 * project a given spec targets.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: "html",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    {
      name: "mobile-360",
      use: { ...devices["Desktop Chrome"], viewport: { width: 360, height: 800 } },
    },
    {
      name: "tablet-768",
      use: { ...devices["Desktop Chrome"], viewport: { width: 768, height: 1024 } },
    },
    {
      name: "desktop-1440",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } },
    },
  ],
});
