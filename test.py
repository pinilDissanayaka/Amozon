import undetected_chromedriver as uc
import time

options = uc.ChromeOptions()

# Replace with your proxy: format is IP:PORT or IP:PORT:USER:PASS
proxy = "34.102.48.89:8080"

# Add proxy argument
options.add_argument(f'--proxy-server=http://{proxy}')

# Start the browser with options
driver = uc.Chrome(options=options)

driver.get("https://httpbin.org/ip")  # To test if the IP is the proxy

time.sleep(5)  # Wait for the page to load

print(driver.page_source)  # Print the page source to verify the proxy is working
