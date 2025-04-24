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
        # Set up Chrome options
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            # Use WebDriver Manager to handle ChromeDriver
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except ImportError:
            print("WebDriver Manager not installed. Installing with pip install webdriver-manager")
            import subprocess
            subprocess.call(['pip', 'install', 'webdriver-manager'])
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

    def test_amazon_homepage_load_time(self):
        """Test to measure the load time of Amazon.in homepage"""
        driver = self.driver
        wait = WebDriverWait(driver, 30)
        
        print("\n--- Starting Amazon.in Homepage Load Time Test ---")
        
        # Start time measurement
        start_time = time.time()
        
        # Navigate to Amazon.in
        print("Navigating to Amazon.in...")
        driver.get("https://www.amazon.in")
        
        # Wait for page to be fully loaded (logo is a good indicator)
        wait.until(EC.presence_of_element_located((By.ID, "nav-logo-sprites")))
        
        # Additional check for search box to ensure page is interactive
        wait.until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
        
        # Calculate load time
        end_time = time.time()
        load_time = end_time - start_time
        
        # Print the single load time measurement
        print(f"\nAmazon.in Load time:")
        print(f"Load Time: {load_time:.2f} seconds")
        print("---------------------------------------")
        
        # Take a screenshot for verification
        # driver.save_screenshot("amazon_homepage.png")
        # print("Screenshot saved as 'amazon_homepage.png'")

    def tearDown(self):
        print("Closing browser...")
        self.driver.quit()
        print("Test completed")

if __name__ == "__main__":
    unittest.main()
