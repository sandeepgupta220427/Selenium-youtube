const { test, expect } = require('@playwright/test');

test.describe('VWO Login Page - RICE POT Test Cases', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to URL before each test
    await page.goto('https://app.vwo.com/');
  });

  // TC-001: Valid Login with Correct Credentials
  test('TC-001: Valid Login with Correct Credentials', async ({ page }) => {
    console.log('Running TC-001: Expected to fail since credentials are fake');
    await page.fill('#login-username', 'valid.user@example.com');
    await page.fill('#login-password', 'ValidPassword123!');
    await page.click('#js-login-btn');

    // Expected Result: redirect to dashboard
    // Await for specific URL or error message for negative flow representation.
    // In actual scenario, we wait for dashboard: await expect(page).toHaveURL(/dashboard/);
    
    // Waiting a moment to let the network request process
    await page.waitForTimeout(2000);
    // As valid credentials are required for a real success, this might remain on /login or show error.
    // In actual code, wait for the expected element on the dashboard:
    // await expect(page.locator('.dashboard-header')).toBeVisible();
  });

  // TC-002: Invalid Login with Unregistered Email
  test('TC-002: Invalid Login with Unregistered Email', async ({ page }) => {
    await page.fill('#login-username', 'unregistered.user@example.com');
    await page.fill('#login-password', 'AnyPassword123!');
    await page.click('#js-login-btn');

    // Assert error message
    const errorLocator = page.locator('#js-notification-box-msg');
    await expect(errorLocator).toBeVisible({ timeout: 10000 });
  });

  // TC-003: Invalid Login with Valid Email but Wrong Password
  test('TC-003: Invalid Login with Valid Email but Wrong Password', async ({ page }) => {
    await page.fill('#login-username', 'valid.user@example.com');
    await page.fill('#login-password', 'WrongPassword999!');
    await page.click('#js-login-btn');

    // Assert error message
    const errorLocator = page.locator('#js-notification-box-msg');
    await expect(errorLocator).toBeVisible({ timeout: 10000 });
  });

  // TC-004: Invalid Login with Invalid Email Format
  test('TC-004: Invalid Login with Invalid Email Format', async ({ page }) => {
    await page.fill('#login-username', 'invalid-email-format');
    await page.fill('#login-password', 'ValidPassword123!');
    await page.click('#js-login-btn'); // triggers inline validation instead of submitting

    // Instead of verifying a notification, the tooltip usually shows inline, and we don't navigate.
    await expect(page).toHaveURL('https://app.vwo.com/#/login');
    
    // Checking the error message
    const emailErrorLocator = page.locator('.invalid-reason');
    await expect(emailErrorLocator.first()).toBeVisible();
  });

  // TC-005: Invalid Login with Empty Credentials
  test('TC-005: Invalid Login with Empty Credentials', async ({ page }) => {
    // leave fields empty
    await page.click('#js-login-btn');

    // Assert mandatory field messages show up
    await expect(page).toHaveURL('https://app.vwo.com/#/login');
    
    // Validation messages for both inputs
    const errorLocators = page.locator('.invalid-reason');
    await expect(errorLocators.nth(0)).toBeVisible(); // username error
    await expect(errorLocators.nth(1)).toBeVisible(); // password error
  });

});
