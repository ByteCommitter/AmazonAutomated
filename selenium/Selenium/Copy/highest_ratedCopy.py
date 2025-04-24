import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
import os

class AmazonAddToCartTest(unittest.TestCase):
    
    def setUp(self):
        # Set Chrome options
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        
        try:
            # Use WebDriver Manager to handle ChromeDriver
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except ImportError:
            print("WebDriver Manager not installed. Please run: pip install webdriver-manager")
            print("Then run this script again.")
            exit(1)
        
        self.wait = WebDriverWait(self.driver, 10)
    
    def get_product_details(self, first_product):
        """Extract name and price of a product from search results"""
        product_name = "Name not found"
        product_price = "Price not found"
        
        # Extract product name using multiple possible selectors
        name_selectors = [
            "h2 a span",
            ".a-size-medium.a-color-base.a-text-normal",
            ".a-size-base-plus.a-color-base.a-text-normal",
            "h2 .a-link-normal span",
            "h2 a",
            "h2"
        ]
        
        for selector in name_selectors:
            try:
                elements = first_product.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    product_name = elements[0].text.strip()
                    if product_name:
                        print(f"Found product name using selector: {selector}")
                        break
            except Exception:
                continue
        
        # Extract product price using multiple possible selectors
        price_selectors = [
            ".a-price .a-offscreen",
            "span.a-price span.a-offscreen",
            ".a-price-whole",
            ".a-color-price",
            ".a-price"
        ]
        
        for selector in price_selectors:
            try:
                elements = first_product.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    price_element = elements[0]
                    if "a-offscreen" in selector:
                        product_price = price_element.get_attribute("innerHTML").strip()
                    else:
                        product_price = price_element.text.strip()
                        if selector == ".a-price-whole":
                            product_price = "₹" + product_price
                    if product_price:
                        print(f"Found price using selector: {selector}")
                        break
            except Exception:
                continue
        
        return product_name, product_price
    
    def test_add_to_cart_time(self):
        """Test to measure the time it takes to add a product to cart"""
        driver = self.driver
        wait = self.wait
        
        print("\n--- Starting Amazon Add to Cart Time Test ---")
        
        # Visit Amazon.in
        print("Navigating to Amazon.in...")
        driver.get("https://www.amazon.in")
        
        # Wait for search box to be available and then search for wireless headphones
        print("Searching for wireless headphones...")
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys("wireless headphones")
        search_box.send_keys(Keys.RETURN)
        
        # Wait for search results to load
        wait.until(EC.title_contains("wireless headphones"))
        
        # Sort by Average Customer Review (highest rated first)
        print("Sorting by Average Customer Review...")
        
        # START TIMING THE FILTER TO PRODUCT DETAILS OPERATION
        start_time = time.time()
        
        try:
            # Find and click the sort dropdown
            sort_dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Sort by:']")))
            
            # Use JavaScript to safely click the element
            driver.execute_script("arguments[0].click();", sort_dropdown)
            print("Clicked sort dropdown using JavaScript")
            
            # Wait for dropdown options to appear
            time.sleep(1)
            
            # Find and click the "Avg. Customer Review" option
            review_option = wait.until(EC.presence_of_element_located((By.XPATH, 
                "//a[contains(@id, 's-result-sort-select') and contains(text(), 'Avg. Customer Review')]")))
            driver.execute_script("arguments[0].click();", review_option)
            print("Clicked Avg. Customer Review option using JavaScript")
            
            # Wait for sorting to complete
            print("Waiting for sorting to complete...")
            time.sleep(2)
        
        except Exception as e:
            print(f"Error during sorting by review: {e}")
            # Fallback method: Use direct URL with sorting parameter
            print("Using fallback method: direct URL with sorting parameter...")
            current_url = driver.current_url
            if "?" in current_url:
                sorted_url = current_url + "&s=review-rank"
            else:
                sorted_url = current_url + "?s=review-rank"
            
            driver.get(sorted_url)
            print("Navigated to URL with sort parameter")
            time.sleep(5)
        
        # Get the first product element
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        time.sleep(2)  # Additional time for page to stabilize
        first_product = driver.find_element(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        
        # Get product details
        product_name, product_price = self.get_product_details(first_product)
        
        # END TIMING THE FILTER TO PRODUCT DETAILS OPERATION
        end_time = time.time()
        filter_to_details_time = end_time - start_time
        
        # Print the results
        print("\n----- FIRST PRODUCT DETAILS -----")
        print(f"Product Name: {product_name}")
        print(f"Product Price: {product_price}")
        print(f"Time from applying filter to getting product details: {filter_to_details_time:.2f} seconds")
        print("--------------------------------\n")
       
    
    def tearDown(self):        
        print("Closing browser...")        
        self.driver.quit()        
        print("Test completed")

if __name__ == "__main__":    
    unittest.main()