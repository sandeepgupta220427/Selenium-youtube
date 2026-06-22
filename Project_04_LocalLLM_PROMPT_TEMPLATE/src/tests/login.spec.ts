import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('VWO Login Page - POM Test Cases', () => {

    test('TC_011: Login with Invalid Credentials', async ({ page }) => {
        const loginPage = new LoginPage(page);
        await loginPage.navigate();
        await loginPage.login('valid.user@example.com', 'WrongPassword999!');
        await expect(loginPage.errorMessage).toBeVisible({ timeout: 10000 });
    });

    test('TC_010: Login with Empty Credentials', async ({ page }) => {
        const loginPage = new LoginPage(page);
        await loginPage.navigate();
        await loginPage.login('', '');
        await expect(loginPage.errorMessage).toBeVisible({ timeout: 10000 });
    });

    test('TC_012: Login with Invalid Email Format', async ({ page }) => {
        const loginPage = new LoginPage(page);
        await loginPage.navigate();
        await loginPage.login('invalid-email-format', 'SomePassword123!');
        await expect(loginPage.errorMessage).toBeVisible({ timeout: 10000 });
    });
});
