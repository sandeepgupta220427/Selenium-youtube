import { convertSeleniumToPlaywright } from '../navigation/converter_engine.js';

const sampleJava = `
package com.example;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.Assert;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class LoginTest {
    WebDriver driver;

    @BeforeMethod
    public void setup() {
        driver = new ChromeDriver();
        driver.get("https://example.com/login");
    }

    @Test
    public void testLoginSuccess() {
        driver.findElement(By.id("username")).sendKeys("testuser");
        driver.findElement(By.id("password")).sendKeys("password123");
        driver.findElement(By.cssSelector("button[type='submit']")).click();
        
        String welcomeText = driver.findElement(By.tagName("h1")).getText();
        Assert.assertEquals(welcomeText, "Welcome, testuser!");
    }
}
`;

async function runTest() {
    try {
        const result = await convertSeleniumToPlaywright(sampleJava, 'converted_test.spec.ts');
        console.log("--- CONVERTED CODE START ---");
        console.log(result.convertedCode);
        console.log("--- CONVERTED CODE END ---");
        console.log(`Payload saved to: ${result.outputPath}`);
    } catch (error) {
        console.error("Test execution failed:", error);
    }
}

runTest();
