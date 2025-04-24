import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("WebDriver Manager not installed. Please run: pip install webdriver-manager")


class SearchLoadTime(unittest.TestCase):
    
    def setUp(self):
        # Set Chrome options
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        
        # Initialize the Chrome WebDriver
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def test_amazon_search_load_time(self):
        """Measure load time from Amazon homepage to search results"""
        driver = self.driver
        
        # Start timing from navigating to Amazon
        print("Navigating to Amazon.in...")
        
        
        # Navigate to Amazon
        driver.get("https://www.amazon.in")
        
        # Wait for search box to be available
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        start_time = time.time()
        # Perform search
        print("Searching for wireless headphones...Started time")
        search_box.clear()
        search_box.send_keys("wireless headphones")
        search_box.send_keys(Keys.RETURN)
        
        # Wait for search results to load completely
        self.wait.until(EC.title_contains("wireless headphones"))
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        
        # End timing after search results are loaded
        end_time = time.time()
        total_load_time = end_time - start_time
        
        # Print the timing results
        print("\n----- AMAZON SEARCH LOAD TIME -----")
        print(f"Time from Amazon homepage to search results: {total_load_time:.2f} seconds")
        print("-----------------------------------\n")
        
        # Verify search was successful
        self.assertIn("wireless headphones", driver.title.lower())
    
    def tearDown(self):
        self.driver.quit()
        print("Test completed")


if __name__ == "__main__":
    unittest.main()
