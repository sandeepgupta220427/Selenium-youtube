# 🔍 Findings & Research

## Initial Observations
- Project goal: Selenium to Playwright Javascript/Typescript converter.
- Protocol: B.L.A.S.T.
- Architecture: A.N.T. (3-layer).

## Research Items
- [ ] Existing Selenium to Playwright migration tools (e.g., Playwright's own codegen or migration guides).
- [x] Common Java TestNG annotations and their Playwright equivalents.
    - `@Test` -> `test('name', async ({ page }) => { ... })`
    - `@BeforeMethod` -> `test.beforeEach(async ({ page }) => { ... })`
    - `@AfterMethod` -> `test.afterEach(async ({ page }) => { ... })`
    - `@BeforeClass` -> `test.beforeAll(async () => { ... })`
    - `@AfterClass` -> `test.afterAll(async () => { ... })`
    - `@DataProvider` -> Handled via `for...of` loops or data-driven `test()` calls.
- [x] Java Selenium WebDriver methods to Playwright locators and actions.
    - `driver.get(url)` -> `await page.goto(url)`
    - `findElement(By.id("id"))` -> `page.locator('#id')`
    - `findElement(By.cssSelector(".class"))` -> `page.locator('.class')`
    - `findElement(By.xpath("//..."))` -> `page.locator('xpath=//...')`
    - `click()` -> `click()`
    - `sendKeys("text")` -> `fill("text")`
    - `getText()` -> `textContent()` or `innerText()`
    - `Assert.assertEquals(act, exp)` -> `expect(act).toBe(exp)`
- [x] Tools for Java AST parsing:
    - `java-parser` npm package or using LLM for structured transcription.
