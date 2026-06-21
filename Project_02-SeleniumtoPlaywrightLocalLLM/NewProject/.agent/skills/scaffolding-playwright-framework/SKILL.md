---
name: scaffolding-playwright-framework
description: Scaffolds a production-ready Playwright (JS/TS) automation framework starting from scratch. Implements Page Object Model (POM), custom reporters, and follows enterprise testing standards. Triggered when the user asks to "start a new Playwright project" or "build an E2E framework".
---

# Scaffolding Playwright Framework

This skill automates the creation of a full-stack Playwright framework with a focus on Page Object Model (POM) and modularity.

## When to use this skill
- When starting a new web automation project.
- When the user provides a domain and wants a scaffolded framework.
- When migrating from a legacy framework to Playwright.

## Workflow
1.  **Gather Inputs**:
    - [ ] Ask for the **Domain URL** (Base URL).
    - [ ] Ask for **Key Pages** or **Flows** to automate (Instruction).
2.  **Environment Setup**:
    - [ ] Initialize `package.json` with Playwright dependencies.
    - [ ] Create folder structure: `tests/`, `pages/`, `utils/`, `reporters/`.
3.  **Core Component Generation**:
    - [ ] Generate `playwright.config.ts`.
    - [ ] Generate `BasePage.ts` for common actions.
    - [ ] Scaffold specific **Page Objects** based on instructions.
4.  **Reporting & Execution**:
    - [ ] Implement a `CustomReporter.ts`.
    - [ ] Provide initial `example.spec.ts`.

## Framework Guidelines
- **POM**: Locators must reside within Page classes, never in tests.
- **Naming**: Use camelCase for methods and PascalCase for Classes.
- **Independence**: Each test must be atomic and capable of running in parallel.
- **Custom Reporting**: Log specific events (navigation, clicks) to the custom reporter.

## Code Templates

### 1. Playwright Config (`playwright.config.ts`)
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  reporter: [['html'], ['./reporters/CustomReporter.ts']],
  use: {
    baseURL: '[[BASE_URL]]',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
});
```

### 2. Base Page (`pages/BasePage.ts`)
```typescript
import { Page, Locator } from '@playwright/test';

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async navigateTo(path: string = '') {
    await this.page.goto(path);
  }

  async waitForElement(locator: Locator) {
    await locator.waitFor({ state: 'visible' });
  }
}
```

### 3. Custom Reporter (`reporters/CustomReporter.ts`)
```typescript
import { FullConfig, FullResult, Reporter, Suite, TestCase, TestResult } from '@playwright/test/reporter';

class CustomReporter implements Reporter {
  onBegin(config: FullConfig, suite: Suite) {
    console.log(`Starting the run with ${suite.allTests().length} tests`);
  }

  onTestBegin(test: TestCase) {
    console.log(`>> Starting test: ${test.title}`);
  }

  onTestEnd(test: TestCase, result: TestResult) {
    console.log(`<< Finished test ${test.title}: ${result.status}`);
  }
}
export default CustomReporter;
```

## Instructions for the Agent
1.  **Read user context** (Domain & Instructions).
2.  **Generate the configuration** first.
3.  **Build Class Files** for each logical page identified.
4.  **Verify** by running `npx playwright test --list` after scaffolding.
