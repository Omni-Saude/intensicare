import { test, expect } from '@playwright/test';

test.describe('IntensiCare v3 — Smoke Tests', () => {

  test('Dashboard renders without errors', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1, [role="main"]')).toBeVisible();
    // Should show at least the page structure even without API
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('Login page redirects unauthenticated users', async ({ page }) => {
    // Clear any cookies
    await page.context().clearCookies();
    await page.goto('/admin');
    // Should redirect to /login
    await expect(page).toHaveURL(/\/login/);
  });

  test('Pathway catalog renders', async ({ page }) => {
    await page.goto('/pathways');
    await expect(page.locator('[role="main"]')).toBeVisible();
  });

  test('Alert triage renders', async ({ page }) => {
    await page.goto('/alerts');
    await expect(page.locator('[role="main"]')).toBeVisible();
  });

  test('Accessibility — pages have main landmark', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('main')).toBeVisible();
  });

  test('Accessibility — skip-link or proper heading structure', async ({ page }) => {
    await page.goto('/');
    const headings = page.locator('h1, h2');
    await expect(headings.first()).toBeVisible();
  });

});
