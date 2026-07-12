import { test, expect, type Page } from '@playwright/test';

// The `token` cookie is HttpOnly and set by the backend on login (see
// middleware.ts + lib/api.ts). Every route except /login requires it, so
// the structural smoke tests below assert the *auth gate itself* rather
// than page content that only exists behind it.

async function loginViaUI(page: Page) {
  await page.goto('/login');
  await page.getByLabel('Usuário').fill('admin');
  await page.getByLabel('Senha').fill('admin');
  await page.getByRole('button', { name: 'Entrar' }).click();
  await expect(page).toHaveURL('/', { timeout: 15_000 });
}

test.describe('IntensiCare v3 — Smoke Tests', () => {

  test('Dashboard route requires authentication and redirects to login', async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/');
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('button', { name: 'Entrar' })).toBeVisible();
  });

  test('Login page redirects unauthenticated users', async ({ page }) => {
    // Clear any cookies
    await page.context().clearCookies();
    await page.goto('/admin');
    // Should redirect to /login
    await expect(page).toHaveURL(/\/login/);
  });

  test('Pathway catalog route requires authentication and redirects to login', async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/pathways');
    await expect(page).toHaveURL(/\/login/);
  });

  test('Alert triage route requires authentication and redirects to login', async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/alerts');
    await expect(page).toHaveURL(/\/login/);
  });

  test('Accessibility — login form fields have associated labels', async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/login');
    await expect(page.getByLabel('Usuário')).toBeVisible();
    await expect(page.getByLabel('Senha')).toBeVisible();
  });

  test('Accessibility — login page exposes an accessible brand name', async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/login');
    await expect(page.getByRole('img', { name: 'IntensiCare' })).toBeVisible();
  });

  // ───────────────────────────────────────────────────────────────────────
  // Real-backend tests — only meaningful with a live API at :8000 and a
  // bootstrapped admin/admin user. Skipped unless E2E_BACKEND=1 so the
  // default CI run (frontend only, no backend) stays green with just the
  // structural checks above.
  // ───────────────────────────────────────────────────────────────────────

  test('Real login flow authenticates and redirects to the dashboard', async ({ page }) => {
    test.skip(process.env.E2E_BACKEND !== '1', 'requires a live backend at :8000 with an admin/admin user');

    await loginViaUI(page);
    await expect(page.getByRole('list', { name: 'Lista de pacientes' })).toBeVisible({ timeout: 15_000 });
  });

  test('Authenticated dashboard shows at least one bed card with a visible severity indicator', async ({ page }) => {
    test.skip(process.env.E2E_BACKEND !== '1', 'requires a live backend at :8000 with an admin/admin user');

    await loginViaUI(page);
    await expect(page.getByRole('list', { name: 'Lista de pacientes' })).toBeVisible({ timeout: 15_000 });

    const bedCards = page.getByRole('button', { name: /^Paciente / });
    test.skip((await bedCards.count()) === 0, 'no patients on the dashboard to assert severity on');

    const severityDots = page.getByRole('status', { name: /^Severidade / });
    await expect(severityDots.first()).toBeVisible();
    expect(await severityDots.count()).toBeGreaterThan(0);
  });

  test('Two-click patient journey: bed card → patient detail → pathway detail', async ({ page }) => {
    test.skip(process.env.E2E_BACKEND !== '1', 'requires a live backend at :8000 with an admin/admin user');

    await loginViaUI(page);
    await expect(page.getByRole('list', { name: 'Lista de pacientes' })).toBeVisible({ timeout: 15_000 });

    const bedCards = page.getByRole('button', { name: /^Paciente / });
    test.skip((await bedCards.count()) === 0, 'no patients on the dashboard to click through');

    // Click 1: bed card → patient detail.
    await bedCards.first().click();
    await expect(page).toHaveURL(/\/patient\/[^/]+$/);

    // Click 2: active pathway card → pathway detail. Only guaranteed with
    // DEMO-seeded data (dev), not necessarily in CI, so skip gracefully.
    const pathwayCards = page.getByRole('button', { name: /^Trilha / });
    test.skip((await pathwayCards.count()) === 0, 'patient has no active pathway (DEMO seed data not present)');

    await pathwayCards.first().click();
    await expect(page).toHaveURL(/\/patient\/[^/]+\/pathway\/[^/]+$/);
  });

});
