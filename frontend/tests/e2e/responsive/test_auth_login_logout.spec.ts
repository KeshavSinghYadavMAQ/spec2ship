import { test } from "@playwright/test";

test.skip("user can login and logout via auth journey", async ({ page }) => {
  await page.goto("/login");
});
