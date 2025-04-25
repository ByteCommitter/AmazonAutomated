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
    print("WebDriver Manager not installed!")


class AmazonLowestPriceSearch(unittest.TestCase):
    
    def setUp(self):
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.filter_start_time = None
    
    def get_first_product_details(self):
        try:
            print("Finding product information...")
            start_time = time.time()
            
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
            
            first_product = self.driver.find_element(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            
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
                            print(f"Found product name: {product_name}")
                            
                            if hasattr(self, 'filter_start_time') and self.filter_start_time:
                                filter_to_name_time = time.time() - self.filter_start_time
                            
                            break
                except Exception:
                    continue
            
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
                            print(f"Found price: {product_price}")
                            break
                except Exception:
                    continue
            
            print(f"\nProduct: {product_name}")
            print(f"Price: {product_price}")
            print(f"Data retrieved in {data_retrieval_time:.2f} seconds")
            
        except Exception as e:
            print(f"Error finding product information: {e}")
            self.driver.save_screenshot("error_state.png")
    
    def test_lowest_priced_wireless_headphone(self):
        driver = self.driver
        
        print("Opening Amazon website...")
        driver.get("https://www.amazon.in")
        
        print("Searching for wireless headphones...")
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys("wireless headphones")
        search_box.send_keys(Keys.RETURN)
        
        self.wait.until(EC.title_contains("wireless headphones"))
        
        print("Sorting by lowest price...")
        
        try:
            sort_dropdown = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[aria-label='Sort by:']")))
            
            if sort_dropdown:
                driver.execute_script("arguments[0].click();", sort_dropdown)
                
                #time.sleep(1)
                
                start_time = time.time()
                self.filter_start_time = time.time()
                
                price_option = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(@id, 's-result-sort-select') and contains(text(), 'Price: Low to High')]")))
                driver.execute_script("arguments[0].click();", price_option)
                
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
                
                end_time = time.time()
                load_time = end_time - start_time
                print(f"Filter applied in {load_time:.2f} seconds")
                
                #time.sleep(2)
                
        except Exception as e:
            print(f"Error during sorting: {e}")
        
        self.get_first_product_details()
        self.assertIn("wireless headphones", driver.title.lower())
    
    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()