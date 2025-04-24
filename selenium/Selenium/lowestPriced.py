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

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("WebDriver Manager not installed. Please run: pip install webdriver-manager")


class AmazonLowestPriceSearch(unittest.TestCase):
    
    def setUp(self):
        # Set Chrome options
        options = ChromeOptions()
        # options.headless = True  # Uncomment if you want headless mode
        options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation
        options.add_argument("--start-maximized")  # Start maximized
        
        # Initialize the Chrome WebDriver with WebDriver Manager
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.filter_start_time = None
    
    def get_first_product_details(self):
        """
        Extract the name and price of the first product from search results.
        """
        try:
            print("Attempting to extract first product information...")
            start_time = time.time()
            
            # Wait for product grid to load and add additional time for stability
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
            #time.sleep(1)  # Additional time for page to stabilize
            
            # Get the first product element
            first_product = self.driver.find_element(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            
            # Extract product name using multiple possible selectors
            product_name = "Name not found"
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
                            
                            # time for filter page to  finding product name
                            if hasattr(self, 'filter_start_time') and self.filter_start_time:
                                filter_to_name_time = time.time() - self.filter_start_time
                                #print(f"Time from applying filter to getting product name: {filter_to_name_time:.2f} seconds")
                            
                            break
                except Exception:
                    continue
            
            # Extract product price using multiple possible selectors
            product_price = "Price not found"
            price_selectors = [
                ".a-price .a-offscreen",
                "span.a-price span.a-offscreen",
                ".a-price-whole",
                ".a-color-price",
                ".a-price"
            ]
            
            end_time = time.time()
            data_retrieval_time = end_time - start_time

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
            
            # Print the results
            print("\n----- FIRST PRODUCT DETAILS -----")
            print(f"Product Name: {product_name}")
            print(f"Product Price: {product_price}")
            
            # Calculate and display time taken to retrieve data
            
            print(f"Time taken to retrieve product data: {data_retrieval_time:.2f} seconds")
            print("--------------------------------\n")
            
        except Exception as e:
            print(f"Error extracting product information: {e}")
            self.driver.save_screenshot("error_state.png")
            print("Error state screenshot saved as 'error_state.png'")
    
    def test_lowest_priced_wireless_headphone(self):
        """Test to find the lowest priced wireless headphone on Amazon"""
        driver = self.driver
        
        print("Navigating to Amazon.in...")
        driver.get("https://www.amazon.in")
        print(f"Page Title: {driver.title}")
        
        # Wait for search box to be available and then search for wireless headphones
        print("Searching for wireless headphones...")
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys("wireless headphones")
        search_box.send_keys(Keys.RETURN)
        
        # Wait for search results to load
        self.wait.until(EC.title_contains("wireless headphones"))
        print(f"Search results page title: {driver.title}")
        
        # Sort by price: Low to High
        print("Sorting by price: Low to High...")
        
        try:
            sort_dropdown = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[aria-label='Sort by:']")))
            
            if sort_dropdown:
                # Use JavaScript to safely click the element
                driver.execute_script("arguments[0].click();", sort_dropdown)
                print("Clicked sort dropdown using JavaScript")
                
                # Wait for dropdown options to appear
                time.sleep(1)
                
                # Start timing
                start_time = time.time()
                
                # Start timing for filter-to-name measurement
                self.filter_start_time = time.time()
                
                # Try to find and click the "Price: Low to High" option
                price_option = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(@id, 's-result-sort-select') and contains(text(), 'Price: Low to High')]")))
                driver.execute_script("arguments[0].click();", price_option)
                print("Clicked price option using JavaScript")
                
                # Wait for sorting to complete and page to load
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
                
                end_time = time.time()
                load_time = end_time - start_time
                print(f"Page load time after applying filter: {load_time:.2f} seconds")
                
                time.sleep(2)
                
        except Exception as e:
            print(f"Error during sorting: {e}")
        
        self.get_first_product_details()
        self.assertIn("wireless headphones", driver.title.lower(), "Search term not found in page title")
    
    def tearDown(self):
        print("Test completed")


if __name__ == "__main__":
    unittest.main()






