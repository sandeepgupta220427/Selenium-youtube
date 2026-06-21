const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: 0,
  workers: 1, // keeping it 1 so we can see what's happening
  reporter: 'html',
  use: {
    trace: 'on-first-retry',
    headless: false, // Set to false to see the browser UI
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
