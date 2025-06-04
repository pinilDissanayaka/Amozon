import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random



options = uc.ChromeOptions()

driver = uc.Chrome(options=options)

driver.get("https://www.kogan.com/au/")

time.sleep(5)  


try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='home-page']"))
    )
    print("Page loaded successfully without bot detection.")
except Exception as e:
    print(f"Page load failed or detected as bot. Error: {e}")

time.sleep(5)
driver.quit()

