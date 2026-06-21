import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { InventoryPage } from '../pages/InventoryPage';

test.describe('SauceDemo Login and Inventory Tests', () => {
    let loginPage: LoginPage;
    let inventoryPage: InventoryPage;

    test.beforeEach(async ({ page }) => {
        loginPage = new LoginPage(page);
        inventoryPage = new InventoryPage(page);
        await loginPage.navigateTo('/');
    });

    test('should login successfully and see inventory', async ({ page }) => {
        await test.step('Login with valid credentials', async () => {
            await loginPage.login('standard_user', 'secret_sauce');
        });

        await test.step('Verify inventory page is displayed', async () => {
            const headerVisible = await inventoryPage.isProductHeaderVisible();
            expect(headerVisible).toBeTruthy();

            const headerText = await inventoryPage.getProductHeaderText();
            expect(headerText).toBe('Products');
        });

        await test.step('Verify inventory items are listed', async () => {
            const itemCount = await inventoryPage.getInventoryCount();
            console.log(`Found ${itemCount} items in inventory`);
            expect(itemCount).toBeGreaterThan(0);
        });
    });

    test('should show error for invalid credentials', async ({ page }) => {
        await test.step('Login with invalid credentials', async () => {
            await loginPage.login('locked_out_user', 'secret_sauce');
        });

        await test.step('Verify error message', async () => {
            const error = await loginPage.getErrorMessage();
            expect(error).toContain('Epic sadface: Sorry, this user has been locked out.');
        });
    });
});
