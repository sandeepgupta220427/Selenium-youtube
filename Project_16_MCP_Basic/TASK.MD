What you need to do, you need to basically add the MCP of Playwright as well as JIRA. 



First of all, you will create a test case by using the RICE POT method for the Login to app.vwo.com .here you need to write five test cases for the valid login and invalid logins



You need to ask the AI to create an MD file. Okay? Not an MD file, or you can create this into an Excel file as well. After the RICE POT method, you export everything into the Excel file. Ask the AI to read the steps to reproduce of a test case and step by step execute all the test cases into the same Excel file. What it is going to do is for invalid login, it is going to use dummy username and password. It is going to try, right? Login can be in Arabic, Chinese, normal login, dummy login, invalid email, all this one. It will log in and it will use a Playwright MCP and basically run the test cases one by one. 



Mark pass or fail based on your expected or actual result. So out of five test cases, just fail one test case automatically. For failed test case, it should always take a screenshot. 



Tell him to create an HTML file in a tabular format for all the test cases, their execution, and the result (pass or fail). The screenshot, the prompt, and the conversation history need to be put into one of the MCP Playwright projects. 



After doing this, for the failed test case, you need to create a bug. we need to add a JIRA ticket and make sure JIRA ticket is added with the test report 