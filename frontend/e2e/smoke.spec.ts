import { test, expect } from '@playwright/test';

test.describe('Smoke', () => {
  test('login page loads and shows main elements', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveTitle(/Masal Fabrikası/i);
    await expect(page.getByRole('textbox').first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button').first()).toBeVisible();
  });

  test('unauthenticated visit to / redirects to /login', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/login/);
  });

  test('health check: app shell loads', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('#root')).toBeVisible();
  });
});
