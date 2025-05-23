import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AmazonLoadTimeTest(unittest.TestCase):

    def setUp(self):
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except ImportError:
            print("WebDriver Manager not installed.")

    def test_amazon_homepage_load_time(self):
        driver = self.driver
        wait = WebDriverWait(driver, 30)
        
        print("Starting Amazon homepage test")
        
        start_time = time.time()
        
        print("Opening Amazon website...")
        driver.get("https://www.amazon.in")
        
        wait.until(EC.presence_of_element_located((By.ID, "nav-logo-sprites")))
        wait.until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
        
        end_time = time.time()
        load_time = end_time - start_time
        
        print(f"Amazon.in loaded in {load_time:.2f} seconds")

    def tearDown(self):
        self.driver.quit()
        print("Test finished")

if __name__ == "__main__":
    unittest.main()
