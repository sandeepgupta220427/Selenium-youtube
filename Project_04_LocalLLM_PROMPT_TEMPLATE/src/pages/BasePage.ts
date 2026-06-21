import { Page, Locator } from '@playwright/test';

export abstract class BasePage {
    protected page: Page;
    protected path: string;

    constructor(page: Page, path: string) {
        this.page = page;
        this.path = path;
    }

    async navigate() {
        await this.page.goto(this.path);
    }

    async getTitle() {
        return await this.page.title();
    }

    async waitForUrl(url: string | RegExp) {
        await this.page.waitForURL(url);
    }
}
