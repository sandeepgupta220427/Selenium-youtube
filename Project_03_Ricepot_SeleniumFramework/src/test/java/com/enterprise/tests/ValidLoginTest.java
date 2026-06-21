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

public class ValidLoginTest {

    private WebDriver driver;
    private LoginPage loginPage;
    private static final String BASE_URL = "https://login.salesforce.com/?locale=in";
    private static final String VALID_USERNAME = "testuser@example.com";
    private static final String VALID_PASSWORD = "TestPassword123";

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

    @Test(priority = 1, description = "Verify login page UI elements are displayed")
    public void verifyLoginPageUIElements() {
        loginPage.navigateToLoginPage(BASE_URL);
        Assert.assertTrue(loginPage.isUsernameFieldDisplayed(), "Username field is not displayed");
        Assert.assertTrue(loginPage.isPasswordFieldDisplayed(), "Password field is not displayed");
        Assert.assertTrue(loginPage.isLoginButtonDisplayed(), "Login button is not displayed");
        Assert.assertTrue(loginPage.isRememberMeCheckboxDisplayed(), "Remember me checkbox is not displayed");
        Assert.assertTrue(loginPage.isForgotPasswordLinkDisplayed(), "Forgot password link is not displayed");
    }

    @Test(priority = 2, description = "Verify username field accepts email format")
    public void verifyUsernameFieldAcceptsEmail() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.enterUsername("test@domain.com");
        Assert.assertEquals(loginPage.getUsernameFieldType(), "email", "Username field should accept email format");
    }

    @Test(priority = 3, description = "Verify password field masks input")
    public void verifyPasswordFieldMasksInput() {
        loginPage.navigateToLoginPage(BASE_URL);
        Assert.assertEquals(loginPage.getPasswordFieldType(), "password", "Password field should mask input");
    }

    @Test(priority = 4, description = "Verify remember me checkbox can be selected")
    public void verifyRememberMeCheckbox() {
        loginPage.navigateToLoginPage(BASE_URL);
        Assert.assertFalse(loginPage.isRememberMeChecked(), "Remember me should be unchecked by default");
        loginPage.checkRememberMe();
        Assert.assertTrue(loginPage.isRememberMeChecked(), "Remember me should be checked after click");
        loginPage.uncheckRememberMe();
        Assert.assertFalse(loginPage.isRememberMeChecked(), "Remember me should be unchecked after second click");
    }

    @Test(priority = 5, description = "Verify valid login with remember me functionality")
    public void verifyValidLoginWithRememberMe() {
        loginPage.navigateToLoginPage(BASE_URL);
        loginPage.performLoginWithRememberMe(VALID_USERNAME, VALID_PASSWORD);
    }

    @Test(priority = 6, description = "Verify forgot password link navigates correctly")
    public void verifyForgotPasswordNavigation() {
        loginPage.navigateToLoginPage(BASE_URL);
        String currentUrl = driver.getCurrentUrl();
        loginPage.clickForgotPassword();
        String newUrl = driver.getCurrentUrl();
        Assert.assertNotEquals(newUrl, currentUrl, "URL should change after clicking forgot password");
    }
}
