import { expect, test } from "@playwright/test";

test("login-to-dashboard stays under 10s budget", async ({ page }) => {
  const start = Date.now();
  await page.goto("/login");
  await expect(page.getByText("Sign in to continue.")).toBeVisible();
  const elapsed = Date.now() - start;
  expect(elapsed).toBeLessThan(10_000);
});
