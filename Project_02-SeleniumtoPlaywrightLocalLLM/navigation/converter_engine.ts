import { promptLLM } from '../tools/llm_client.js';
import pkg from 'fs-extra';
const { readFile, writeFile, ensureDir } = pkg;
import { join } from 'path';

const SYSTEM_PROMPT = `
You are a Selenium Java to Playwright (JS/TS) conversion expert. 
Follow the strict 1:1 mapping rules:
1. @Test -> test()
2. driver.findElement -> page.locator()
3. .sendKeys -> .fill()
4. .click -> .click()
5. Assert.assertEquals -> expect().toBe()
Maintain the original logic exactly. Use Playwright best practices like auto-waiting.
`;

export async function convertSeleniumToPlaywright(sourceCode: string, targetPath: string) {
    console.log("🚀 Starting conversion engine...");

    const prompt = `
Convert the following Selenium Java (TestNG) code to Playwright TypeScript.
Ensure strict 1:1 mapping of functionality.

JAVA CODE:
${sourceCode}

PLAYWRIGHT TYPESCRIPT CODE:
`;

    const convertedCode = await promptLLM(prompt, SYSTEM_PROMPT);

    console.log("✅ Conversion complete. Saving payload...");

    await ensureDir(join(process.cwd(), '.tmp'));
    const outputPath = join(process.cwd(), '.tmp', 'converted_test.spec.ts');
    await writeFile(outputPath, convertedCode);

    return {
        convertedCode,
        outputPath
    };
}
