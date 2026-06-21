# VWO Login Page — Test Cases (RICE POT Method)

---

## Role

You are a **QA Automation Tester with 15 years of experience** in software quality assurance across enterprise IT and CRM platforms, including Salesforce.com, HubSpot, and marketing automation tools like VWO (Visual Website Optimizer). You bring deep expertise in functional testing, regression testing, and UI validation. Your test cases are authored with production-level precision, covering both happy path and edge case scenarios to ensure zero defect leakage into production.

---

## RICE POT Method — Reference Guide

| Component | Description |
|-----------|-------------|
| **R** — Requirement / Reference | The functional or business requirement being validated |
| **I** — Input Data | The data values entered into the system under test |
| **C** — Conditions | Environment, browser, network, or system state at the time of testing |
| **E** — Expected Result | The correct, acceptable outcome as per the requirement |
| **P** — Pre-conditions | Setup that must be true before the test case can execute |
| **O** — Output / Actual Result | Observed outcome recorded during execution (filled at runtime) |
| **T** — Test Steps | Step-by-step actions performed to execute the test |

---

## Test Suite: Login Functionality — `app.vwo.com`

**Application Under Test:** VWO (Visual Website Optimizer)
**Login URL:** `https://app.vwo.com/`
**Test Type:** Functional UI Testing
**Authored By:** QA Automation Tester (Senior)
**Total Test Cases:** 5

---

---

## TC-001: Valid Login with Correct Credentials

**Priority:** Critical
**Test Type:** Positive / Happy Path

---

**R — Requirement / Reference**

The system must authenticate a registered, active VWO user when valid email and password credentials are submitted, and redirect them to the VWO Dashboard upon successful login.

---

**I — Input Data**

| Field | Value |
|-------|-------|
| Email | `valid.user@example.com` |
| Password | `ValidPassword123!` |

---

**C — Conditions**

- Browser: Chrome (latest stable) / Firefox (latest stable)
- Network: Stable broadband connection with no proxy interference
- VWO backend authentication server must be online and reachable
- No active session or cached cookies from a prior login

---

**E — Expected Result**

- User is authenticated without error
- Browser redirects to the VWO Dashboard (`https://app.vwo.com/#/dashboard` or equivalent)
- Page title reflects the authenticated state (e.g., "Dashboard — VWO")
- A valid session cookie or authentication token is generated and stored in the browser
- No error banners, alerts, or warning messages are visible post-login

---

**P — Pre-conditions**

- The user account `valid.user@example.com` must be actively registered and verified in the VWO system
- The account must not be suspended, locked, or expired
- The correct password `ValidPassword123!` must be set and active for the account
- The tester must clear all browser cookies and cache before test execution

---

**O — Output / Actual Result**

> *(To be filled during execution)*
> Example: User successfully authenticated and landed on the VWO Dashboard. Session token confirmed in browser DevTools under Application > Cookies.

---

**T — Test Steps**

1. Open the browser and navigate to `https://app.vwo.com/`
2. Verify that the login page loads completely with the Email field, Password field, and Sign In button visible
3. Click on the **Email** input field and enter `valid.user@example.com`
4. Click on the **Password** input field and enter `ValidPassword123!`
5. Click the **"Sign In"** button
6. Wait for the page to load and observe the URL change
7. Assert that the current URL contains `/dashboard` or the authenticated route
8. Assert that the page title contains "VWO" or "Dashboard"
9. Open browser DevTools → Application → Cookies → Verify session cookie is present
10. Assert that no error message or alert banner is displayed on screen

---

---

## TC-002: Invalid Login with Unregistered Email

**Priority:** High
**Test Type:** Negative

---

**R — Requirement / Reference**

The system must deny login access for any email address that is not registered in the VWO database and must display a user-friendly, informative error message to indicate the failure.

---

**I — Input Data**

| Field | Value |
|-------|-------|
| Email | `unregistered.user@example.com` |
| Password | `AnyPassword123!` |

---

**C — Conditions**

- Browser: Chrome (latest stable)
- Network: Normal, stable internet connection
- No rate-limiting or IP blocks in place on the test environment
- Server-side validation must be active

---

**E — Expected Result**

- Login is denied and the user remains on the login page
- An error message is displayed on screen such as: *"That email address doesn't exist"* or *"Invalid credentials"*
- No session cookie or authentication token is created
- The page does not redirect to any authenticated route

---

**P — Pre-conditions**

- The email `unregistered.user@example.com` must NOT exist in the VWO staging or production database
- Confirm non-existence via backend admin panel or database query prior to execution
- Browser cookies must be cleared before test execution

---

**O — Output / Actual Result**

> *(To be filled during execution)*
> Example: Error message "That email address doesn't exist" appeared below the form. User remained on the login page. No redirect occurred.

---

**T — Test Steps**

1. Open the browser and navigate to `https://app.vwo.com/`
2. Verify the login page has loaded successfully with all UI elements visible
3. Click on the **Email** input field and enter `unregistered.user@example.com`
4. Click on the **Password** input field and enter `AnyPassword123!`
5. Click the **"Sign In"** button
6. Observe the page response — assert no redirect to the dashboard occurs
7. Assert that an error message is visible on the UI
8. Assert that the error message text matches expected content (e.g., *"doesn't exist"* or *"Invalid credentials"*)
9. Verify the current URL is still `https://app.vwo.com/`
10. Open browser DevTools → Application → Cookies → Confirm no session cookie was created

---

---

## TC-003: Invalid Login with Valid Email but Wrong Password

**Priority:** High
**Test Type:** Negative

---

**R — Requirement / Reference**

The system must deny access when the submitted password does not match the registered password for a valid email address. The system must display an appropriate error message and must not expose any sensitive account information.

---

**I — Input Data**

| Field | Value |
|-------|-------|
| Email | `valid.user@example.com` |
| Password | `WrongPassword999!` |

---

**C — Conditions**

- Browser: Chrome (latest stable)
- Network: Normal, stable internet connection
- Backend authentication server must be active and processing requests
- Account must not be locked from prior failed attempts

---

**E — Expected Result**

- Login is denied and the user remains on the login page
- An error message is displayed such as: *"Incorrect password"* or *"Invalid credentials"*
- The password field may clear itself automatically after the failed attempt
- No session cookie or authentication token is created
- The system must not indicate whether the email exists or not (to prevent user enumeration attacks)

---

**P — Pre-conditions**

- The user account `valid.user@example.com` must exist and be active in the VWO system
- The password `WrongPassword999!` must be confirmed as incorrect for this account
- The account must not be locked out from prior test executions — reset lock status if needed
- Browser cookies must be cleared before test execution

---

**O — Output / Actual Result**

> *(To be filled during execution)*
> Example: Error message "Incorrect password" displayed. User remained on login page. Password field cleared. No session created.

---

**T — Test Steps**

1. Open the browser and navigate to `https://app.vwo.com/`
2. Verify the login page has loaded successfully
3. Click on the **Email** input field and enter `valid.user@example.com`
4. Click on the **Password** input field and enter `WrongPassword999!`
5. Click the **"Sign In"** button
6. Observe the page response — assert no redirect to the dashboard occurs
7. Assert that an error message is visible on the UI
8. Assert the error message content matches expected text (e.g., *"Incorrect password"*)
9. Check whether the password field has been automatically cleared
10. Verify the current URL is still `https://app.vwo.com/`
11. Open browser DevTools → Application → Cookies → Confirm no session cookie was created

---

---

## TC-004: Invalid Login with Invalid Email Format

**Priority:** Medium
**Test Type:** Negative / Client-Side Validation

---

**R — Requirement / Reference**

The system must validate the format of the email input on the client side before any server request is made. Malformed email strings must be rejected with an inline validation message, preventing unnecessary API calls to the authentication server.

---

**I — Input Data**

| Field | Value |
|-------|-------|
| Email | `invalid-email-format` *(missing `@` and domain)* |
| Password | `ValidPassword123!` |

---

**C — Conditions**

- Browser: Chrome (latest stable) with JavaScript enabled
- Client-side HTML5 or custom JavaScript form validation must be active
- Network requests to the authentication API should NOT be triggered for this scenario

---

**E — Expected Result**

- The form submission is blocked entirely — no API request is sent to the server
- An inline validation error message appears directly under the Email field
- The message reads something like: *"Please enter a valid email address"*
- The Password field is unaffected and retains its entered value
- The user remains on the login page

---

**P — Pre-conditions**

- No pre-conditions required — this test validates front-end behaviour only
- JavaScript must be enabled in the browser
- No prior session or cached login data should be present

---

**O — Output / Actual Result**

> *(To be filled during execution)*
> Example: Inline validation error "Please enter a valid email address" appeared below the Email field. Form did not submit. Network tab in DevTools showed no API call was made.

---

**T — Test Steps**

1. Open the browser and navigate to `https://app.vwo.com/`
2. Verify the login page has loaded with all fields visible
3. Click on the **Email** input field and type `invalid-email-format` (no `@` symbol, no domain)
4. Click on the **Password** input field and enter `ValidPassword123!`
5. Click the **"Sign In"** button
6. Observe the Email field for an inline validation error message
7. Assert that the validation message is visible and reads *"Please enter a valid email address"* or equivalent
8. Assert that the page has NOT redirected or reloaded
9. Open browser DevTools → Network tab → Confirm that no POST request was sent to the authentication endpoint
10. Verify the current URL remains `https://app.vwo.com/`

---

---

## TC-005: Invalid Login with Empty Credentials (Both Fields Blank)

**Priority:** High
**Test Type:** Negative / Boundary / Mandatory Field Validation

---

**R — Requirement / Reference**

Both Email and Password are mandatory fields. The system must prevent form submission when either or both fields are left blank and must display clear, field-level validation messages to guide the user.

---

**I — Input Data**

| Field | Value |
|-------|-------|
| Email | *(Empty — no input)* |
| Password | *(Empty — no input)* |

---

**C — Conditions**

- Browser: Chrome (latest stable) with JavaScript enabled
- HTML5 `required` attribute and/or custom JavaScript validation must be active
- No autofill or browser-remembered credentials should be present

---

**E — Expected Result**

- Form submission is blocked — no server request is made
- Both the Email and Password fields are visually highlighted (e.g., red border or outline)
- Field-level error messages are displayed beneath each field:
  - Email field: *"Email is required"* or *"Please enter your email"*
  - Password field: *"Password is required"* or *"Please enter your password"*
- The page does not reload, redirect, or navigate away from the login screen
- No session or token is generated

---

**P — Pre-conditions**

- No pre-conditions required — this is a pure front-end boundary test
- Ensure browser autofill is disabled to prevent auto-population of credentials
- Clear all cookies, cache, and saved form data before execution

---

**O — Output / Actual Result**

> *(To be filled during execution)*
> Example: Both Email and Password fields turned red with messages "Email is required" and "Password is required" displayed respectively. Page did not reload. No API call made.

---

**T — Test Steps**

1. Open the browser and navigate to `https://app.vwo.com/`
2. Verify the login page has loaded with all fields and the Sign In button visible
3. Do NOT enter any value in the **Email** field — leave it completely blank
4. Do NOT enter any value in the **Password** field — leave it completely blank
5. Click the **"Sign In"** button
6. Observe both input fields for visual error indicators (red border, highlight)
7. Assert that the Email field displays an error message such as *"Email is required"*
8. Assert that the Password field displays an error message such as *"Password is required"*
9. Assert that the page has NOT reloaded or redirected (URL remains `https://app.vwo.com/`)
10. Open browser DevTools → Network tab → Confirm no POST or API request was triggered
11. Assert that no session cookie or authentication token is present in DevTools → Application → Cookies

---

## Summary Table

| TC ID | Test Scenario | Type | Priority | Expected Outcome |
|-------|--------------|------|----------|-----------------|
| TC-001 | Valid login with correct credentials | Positive | Critical | Dashboard redirect, session created |
| TC-002 | Invalid login — unregistered email | Negative | High | Error message, no session |
| TC-003 | Invalid login — correct email, wrong password | Negative | High | Error message, no session |
| TC-004 | Invalid login — malformed email format | Negative | Medium | Client-side inline validation error |
| TC-005 | Invalid login — both fields empty | Negative | High | Mandatory field errors on both fields |
