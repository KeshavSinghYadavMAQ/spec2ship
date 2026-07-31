import { test } from "@playwright/test";

test.skip("unauthenticated users are redirected from protected routes", async ({ page }) => {
  await page.goto("/inventory");
});
