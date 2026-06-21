import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class InventoryPage extends BasePage {
    readonly inventoryItems: Locator;
    readonly productHeader: Locator;

    constructor(page: Page) {
        super(page);
        this.inventoryItems = page.locator('.inventory_item');
        this.productHeader = page.locator('.title');
    }

    async getInventoryCount() {
        return await this.inventoryItems.count();
    }

    async getProductHeaderText() {
        return await this.productHeader.textContent();
    }

    async isProductHeaderVisible() {
        return await this.productHeader.isVisible();
    }
}
