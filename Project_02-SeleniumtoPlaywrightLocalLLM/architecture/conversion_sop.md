# SOP: Selenium Java (TestNG) to Playwright (JS/TS) Conversion

## 🎯 Objective
Provide a strict 1:1 functional mapping for converting automated test scripts from Java-based Selenium/TestNG to Playwright with JavaScript/TypeScript.

## 📋 Conversion Rules

### 1. Test Organization (TestNG -> Playwright Test)
- **Annotations**:
    - `@Test` -> `test('test name', async ({ page }) => { ... })`
    - `@BeforeMethod` -> `test.beforeEach(async ({ page }) => { ... })`
    - `@AfterMethod` -> `test.afterEach(async ({ page }) => { ... })`
    - `@BeforeClass` -> `test.beforeAll(async () => { ... })`
    - `@AfterClass` -> `test.afterAll(async () => { ... })`
- **Classes**: Convert Java classes to file-level scopes or `test.describe('Class Name', () => { ... })` blocks.

### 2. Browser & Navigation
- `driver.get(url)` -> `await page.goto(url)`
- `driver.navigate().to(url)` -> `await page.goto(url)`
- `driver.close()` -> `await page.close()`
- `driver.quit()` -> Managed by Playwright runner (do not convert directly unless in custom teardown).

### 3. Locators & Element Interaction
- **Strict 1:1 Element Selection**:
    - `driver.findElement(By.id("..."))` -> `page.locator('#...')`
    - `driver.findElement(By.name("..."))` -> `page.locator('[name="..."]')`
    - `driver.findElement(By.className("..."))` -> `page.locator('....')`
    - `driver.findElement(By.cssSelector("..."))` -> `page.locator('...')`
    - `driver.findElement(By.xpath("..."))` -> `page.locator('xpath=...')`
    - `driver.findElement(By.linkText("..."))` -> `page.getByRole('link', { name: '...' })` or `page.locator('text=...')`
- **Actions**:
    - `.click()` -> `await ....click()`
    - `.sendKeys("...")` -> `await ....fill("...")`
    - `.clear()` -> `await ....clear()`
    - `.getText()` -> `await ....textContent()`
    - `.getAttribute("...")` -> `await ....getAttribute("...")`
    - `.isDisplayed()` -> `await ....isVisible()`

### 4. Assertions (TestNG Assert -> Playwright Expect)
- `Assert.assertEquals(actual, expected)` -> `expect(actual).toBe(expected)`
- `Assert.assertTrue(condition)` -> `expect(condition).toBeTruthy()`
- `Assert.assertFalse(condition)` -> `expect(condition).toBeFalsy()`
- `Assert.assertNotNull(object)` -> `expect(object).not.toBeNull()`

### 5. Explicit Waits (WebDriverWait -> Playwright Auto-waiting)
- Selenium: `new WebDriverWait(driver, 10).until(ExpectedConditions.visibilityOf(element))`
- Playwright: Directly use `await page.locator('...').waitFor({ state: 'visible' })` or rely on actionability.

## 🛠️ Implementation Strategy
1. **Metadata Extraction**: Parse the Java file to identify methods and annotations.
2. **Block Processing**: Process each method block independently to ensure context is maintained.
3. **Draft Generation**: Use LLM to transcribe the logic according to this SOP.
4. **Post-Processing**: Format the code and wrap it in the Playwright test runner structure.
