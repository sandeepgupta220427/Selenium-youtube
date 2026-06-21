# Saucedemo Playwright POM Framework

A production-ready Playwright automation framework for `saucedemo.com` using the Page Object Model (POM) pattern.

## 📁 Project Structure
- `pages/`: Contains Page Object classes with locators and actions.
- `tests/`: Contains test specifications using the pages.
- `reporters/`: Custom Playwright reporter for enhanced console logging.
- `playwright.config.ts`: Main configuration file.

## 🚀 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Tests
```bash
npx playwright test
```

### 3. View Report
```bash
npx playwright show-report
```

## 🛠 Features
- **Page Object Model**: Centralized locators and reusable page actions.
- **Custom Reporting**: Clean, emoji-powered console output.
- **Auto-waiting**: Leverages Playwright's native auto-waiting for resilience.
- **Parallel Execution**: Configured to run tests in parallel by default.
- **Trace & Screenshots**: Configured to capture traces on retry and screenshots on failure.
