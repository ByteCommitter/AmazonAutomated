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
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except ImportError:
            print("WebDriver Manager not installed! Install it with pip install webdriver-manager")
            exit(1)
        
        self.wait = WebDriverWait(self.driver, 10)
    
    def get_product_details(self, first_product):
        product_name = "Name not found"
        product_price = "Price not found"
        
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
                        #print(f"Found product name: {product_name}")
                        break
            except Exception:
                continue
        
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
                        #print(f"Found price: {product_price}")
                        break
            except Exception:
                continue
        
        return product_name, product_price
    
    def test_add_to_cart_time(self):
        driver = self.driver
        wait = self.wait
        
        print("Starting Amazon highest rated product test...")
        
        print("Opening Amazon website...")
        driver.get("https://www.amazon.in")
        
        print("Searching for wireless headphones...")
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys("wireless headphones")
        search_box.send_keys(Keys.RETURN)
        
        wait.until(EC.title_contains("wireless headphones"))
        
        print("Sorting by highest customer ratings...")
        
        start_time = time.time()
        
        try:
            sort_dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Sort by:']")))
            driver.execute_script("arguments[0].click();", sort_dropdown)
            
            #time.sleep(1)
            
            review_option = wait.until(EC.presence_of_element_located((By.XPATH, 
                "//a[contains(@id, 's-result-sort-select') and contains(text(), 'Avg. Customer Review')]")))
            driver.execute_script("arguments[0].click();", review_option)
            
            #time.sleep(2)
        
        except Exception as e:
            print("Couldn't use dropdown")
            
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        #time.sleep(2)
        first_product = driver.find_element(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        
        product_name, product_price = self.get_product_details(first_product)
        
        end_time = time.time()
        filter_to_details_time = end_time - start_time
        
        print(f"\nProduct: {product_name}")
        print(f"Price: {product_price}")
        print(f"Time from applying filter to getting product details: {filter_to_details_time:.2f} seconds")
    
    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":    
    unittest.main()