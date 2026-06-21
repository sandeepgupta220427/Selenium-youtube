# Master Test Plan for app.vwo.com

## 1. Introduction
- **Purpose**: This document outlines the testing strategy, scope, environment, deliverables, and execution plan for the core functionalities of the VWO application (app.vwo.com).
- **Scope**: Includes functional, UI/UX, and automated regression testing of the primary modules: User Authentication, Dashboard Analytics, A/B Testing Campaign Creation, and Visual Editor.

## 2. Test Items
- VWO Web Application (https://app.vwo.com)
- User Authentication Module
- A/B Testing Campaign Builder
- Settings and Account Management Workspace
- Reporting & Dashboard UI

## 3. Features to be Tested
- **Authentication**: Login with valid/invalid credentials, password reset, and SSO integration.
- **Campaign Management**: Creation, editing, pausing, and archiving of A/B tests.
- **Visual Editor**: Loading the target URL into the editor, modifying DOM elements (text, color, layout), and saving variants successfully.
- **Goal Tracking**: Setting up tracking logic for page visits, button clicks, and form submissions.
- **Reporting**: Verification of data rendering accuracy on the campaign dashboard.

## 4. Features NOT to be Tested
- Pre-release Beta features currently under active development.
- Underlying VWO REST APIs (Covered entirely by a separate backend API Test Plan).
- Enterprise billing and invoicing payment gateways.
- Advanced third-party integrations (e.g., Salesforce, Google Analytics) beyond basic connection toggles.

## 5. Approach
- **Manual Exploratory Testing**: Used for new features, complex edge cases, and UX validation specifically within the Visual Editor iframe.
- **Automated UI Testing**: A Playwright (Node.js/TypeScript) framework will be used for rapid reliability/regression testing of critical user paths (e.g., Login, Campaign Creation, Goal Tracking).
- **Cross-Browser Verification**: Ensure compatibility across the latest versions of Chromium, Firefox, WebKit (Safari), and Edge.

## 6. Item Pass/Fail Criteria
- **Pass**: The assigned feature functions exactly as defined in the Product Requirement Document (PRD), with zero Critical or High severity defects. The UI renders correctly without console errors across supported browsers.
- **Fail**: Main functionality is blocked, unexpected crashes occur, data loss/corruption is observed, or core tracking snippets fail to generate.

## 7. Suspension Criteria and Resumption Requirements
- **Suspension Criteria**: Testing will halt immediately if the QA/Staging environment becomes inaccessible or if 3 or more 'Blocker' level defects are found in the core campaign creation flow.
- **Resumption Requirements**: Testing will resume once the environment is stabilized, or a hotfix is deployed and sanity-checked by an assigned developer.

## 8. Test Deliverables
- Master Test Plan (This document)
- Automated Playwright Test Suite repository
- Manual Test Cases (Linked in Jira/TestRail)
- Defect Reports (Jira)
- Final Test Execution Summary / QA Sign-off Report

## 9. Testing Tasks
- **Preparation Phase**: Review PRDs, identify test scenarios, map dependencies, setup Playwright framework configuration.
- **Execution Phase**: Run automated suites, perform manual exploratory testing, log defects with detailed replication steps.
- **Reporting Phase**: Conduct triages, verify bug fixes, execute final regression, and generate release reports.

## 10. Environmental Needs
- **Hardware**: Standard QA workstations (Mac/Windows).
- **Software**: Modern web browsers for execution.
- **Network**: Stable internet connection to access the internal VWO Staging URLs.
- **Data**: Pre-configured test accounts with various simulated subscription tiers (Pro, Enterprise).

## 11. Responsibilities
- **QA Lead**: Test strategy definition, planning, and final launch sign-off.
- **Automation Engineer**: Developing, stabilizing, and maintaining Playwright scripts.
- **QA Analyst**: Manual exploratory testing, bug reporting, and triage validation.
- **Product Manager**: Requirement clarification and UAT sign-off.

## 12. Staffing and Training Needs
- Two (2) Automation Engineers proficient in Playwright & TypeScript.
- One (1) Manual QA Analyst familiar with A/B testing concepts and basic DOM manipulation skills.
- **Training**: 1-hour Knowledge Transfer (KT) session on the new VWO Visual Editor structure before testing begins to ensure familiarity.

## 13. Schedule
- **Week 1**: Test planning, scenario design, and environment setup.
- **Week 2**: Automation script creation and initial manual feature testing.
- **Week 3**: Full regression execution, bug fixing cycles, and re-testing.
- **Week 4**: Hard code freeze, final sanity checks, deployment sign-off.

## 14. Risks and Contingencies
- **Risk**: The VWO Visual Editor relies heavily on nested iframes, which can historically cause automation flakiness.
  - **Contingency**: Allocate extra capacity for Playwright `frameLocator` stabilization and rely on manual exploratory testing if automated checks remain brittle.
- **Risk**: QA/Test environments might experience unexpected downtime during peak loads.
  - **Contingency**: DevOps to provision an isolated, dedicated QA cluster to reduce dependency on shared staging servers during Week 3 & 4.

## 15. Approvals
- **QA Manager**: _______________ (Pending)
- **Product Owner**: _______________ (Pending)
- **Engineering Lead**: _______________ (Pending)
