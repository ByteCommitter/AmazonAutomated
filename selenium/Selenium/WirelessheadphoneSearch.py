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
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def test_amazon_search_load_time(self):
        driver = self.driver
        
        print("Opening Amazon website...")
        driver.get("https://www.amazon.in")
        
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        start_time = time.time()
        
        print("Searching for wireless headphones...")
        search_box.clear()
        search_box.send_keys("wireless headphones")
        search_box.send_keys(Keys.RETURN)
        
        self.wait.until(EC.title_contains("wireless headphones"))
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        
        end_time = time.time()
        total_load_time = end_time - start_time
        
        print(f"\nSearch completed in {total_load_time:.2f} seconds")
        
        self.assertIn("wireless headphones", driver.title.lower())
    
    def tearDown(self):
        self.driver.quit()
        print("Browser closed")


if __name__ == "__main__":
    unittest.main()
