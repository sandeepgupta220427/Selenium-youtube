package com.enterprise.tests;

import com.enterprise.pages.LoginPage;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;
import java.time.Duration;

public class InvalidLoginTest {

    private WebDriver driver;
    private LoginPage loginPage;
    private static final String BASE_URL = "https://login.salesforce.com/?locale=in";

    @BeforeMethod
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        options.addArguments("--disable-notifications");
        driver = new ChromeDriver(options);
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        loginPage = new LoginPage(driver);
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test(priority = 1, description = "Verify login with empty username and password")
    public void verifyLoginWithEmptyCredentials() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("", "");
        Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message should be displayed for empty credentials");
    }

    @Test(priority = 2, description = "Verify login with empty username and valid password")
    public void verifyLoginWithEmptyUsername() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("", "ValidPass123");
        Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message should be displayed for empty username");
    }

    @Test(priority = 3, description = "Verify login with valid username and empty password")
    public void verifyLoginWithEmptyPassword() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("testuser@example.com", "");
        Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message should be displayed for empty password");
    }

    @Test(priority = 4, description = "Verify login with invalid username format")
    public void verifyLoginWithInvalidUsernameFormat() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("invalidusername", "Password123");
    }

    @Test(priority = 5, description = "Verify login with incorrect password")
    public void verifyLoginWithIncorrectPassword() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("testuser@example.com", "WrongPassword123");
        Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message should be displayed for incorrect password");
    }

    @Test(priority = 6, description = "Verify login with non-existent user")
    public void verifyLoginWithNonExistentUser() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("nonexistentuser12345@test.com", "SomePassword123");
        Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message should be displayed for non-existent user");
    }

    @Test(priority = 7, description = "Verify login with SQL injection attempt")
    public void verifyLoginWithSQLInjection() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("' OR '1'='1", "' OR '1'='1");
        Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message should be displayed for SQL injection attempt");
    }

    @Test(priority = 8, description = "Verify login with XSS attempt")
    public void verifyLoginWithXSSAttempt() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("<script>alert('xss')</script>", "password123");
    }

    @Test(priority = 9, description = "Verify login with special characters in username")
    public void verifyLoginWithSpecialCharacters() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("user!@#$%^&*()@test.com", "Password123");
    }

    @Test(priority = 10, description = "Verify login with very long username")
    public void verifyLoginWithLongUsername() {
        loginPage.navigateToLoginPage(BASE_URL);
        String longUsername = "a".repeat(100) + "@test.com";
        loginPage.performLogin(longUsername, "Password123");
    }

    @Test(priority = 11, description = "Verify login with very long password")
    public void verifyLoginWithLongPassword() {
        loginPage.navigateToLoginPage(BASE_URL);
        String longPassword = "p".repeat(100) + "1!";
        loginPage.performLogin("testuser@example.com", longPassword);
    }

    @Test(priority = 12, description = "Verify login remains on same page after failed attempt")
    public void verifyLoginPageAfterFailedAttempt() {
        loginPage.navigateToLoginPage(BASE_URL);
        String urlBefore = driver.getCurrentUrl();
        loginPage.performLogin("invalid@example.com", "wrongpass");
        String urlAfter = driver.getCurrentUrl();
        Assert.assertTrue(urlAfter.contains("login.salesforce.com"), "Should remain on login page after failed login");
    }

    @Test(priority = 13, description = "Verify error message is cleared on re-entering username")
    public void verifyErrorMessageClearedOnNewInput() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLogin("", "");
        Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message should be displayed");
        loginPage.enterUsername("newuser@example.com");
        Assert.assertTrue(loginPage.isLoginPageDisplayed(), "Login page should still be displayed after entering new username");
    }

    @Test(priority = 14, description = "Verify password field clears after failed login")
    public void verifyPasswordFieldClearsAfterFailedLogin() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.enterPassword("SomePassword123");
        loginPage.performLogin("test@example.com", "SomePassword123");
        String passwordValue = loginPage.getPasswordFieldType();
        Assert.assertEquals(passwordValue, "password", "Password field type should remain password");
    }
}
