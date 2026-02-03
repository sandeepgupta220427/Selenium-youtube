from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Step 1: Initialize WebDriver (using Chrome here)
driver = webdriver.Chrome()

# Step 2: Open YouTube directly
driver.get("https://www.youtube.com")

# Optional: Wait for the page to load
time.sleep(5)

# Step 3: Close the browser
driver.quit()