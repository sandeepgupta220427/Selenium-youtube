import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
    readonly usernameInput: Locator;
    readonly passwordInput: Locator;
    readonly loginButton: Locator;
    readonly errorMessage: Locator;
    readonly inlineErrors: Locator;

    constructor(page: Page) {
        super(page, 'https://app.vwo.com');
        this.usernameInput = page.locator('#login-username');
        this.passwordInput = page.locator('#login-password');
        this.loginButton = page.locator('#js-login-btn');
        this.errorMessage = page.locator('#js-notification-box-msg');
        this.inlineErrors = page.locator('.invalid-reason');
    }

    async login(username: string, password: string) {
        await this.usernameInput.fill(username);
        await this.passwordInput.fill(password);
        await this.loginButton.click();
    }
}
