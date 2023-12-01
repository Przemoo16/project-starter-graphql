// @ts-check
import { expect, test } from '@playwright/test';

test('Home page contains proper title ', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveTitle(/Home/);
});
