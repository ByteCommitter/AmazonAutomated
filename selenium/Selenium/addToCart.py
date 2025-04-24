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
                        print(f"Found product name: {product_name}")
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
                        print(f"Found price: {product_price}")
                        break
            except Exception:
                continue
        
        return product_name, product_price
    
    def test_add_to_cart_time(self):
        driver = self.driver
        wait = self.wait
        
        print("Starting Amazon shopping test...")
        
        print("Opening Amazon website...")
        driver.get("https://www.amazon.in")
        
        print("Searching for wireless headphones...")
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys("wireless headphones")
        search_box.send_keys(Keys.RETURN)
        
        wait.until(EC.title_contains("wireless headphones"))
        
        print("Sorting by highest customer rating...")
        
        try:
            sort_dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Sort by:']")))
            driver.execute_script("arguments[0].click();", sort_dropdown)
            
            time.sleep(1)
            
            review_option = wait.until(EC.presence_of_element_located((By.XPATH, 
                "//a[contains(@id, 's-result-sort-select') and contains(text(), 'Avg. Customer Review')]")))
            driver.execute_script("arguments[0].click();", review_option)
            
            time.sleep(2)
        
        except Exception as e:
            print("Couldn't use dropdown, using direct sort URL instead")
            current_url = driver.current_url
            sorted_url = current_url + ("&" if "?" in current_url else "?") + "s=review-rank"
            driver.get(sorted_url)
            time.sleep(5)
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        time.sleep(2)
        first_product = driver.find_element(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        
        product_name, product_price = self.get_product_details(first_product)
        
        print(f"\nProduct: {product_name}")
        print(f"Price: {product_price}")
        
        print("Attempting to add product to cart...")
        start_time = time.time()
        
        add_to_cart_selectors = [
            "button[name='submit.addToCart']",
            "button[aria-label='Add to cart']",
            "input[name='submit.add-to-cart']",
            ".a-button-text[type='button']",
            "[id*='add-to-cart']",
            ".a-button-input[value*='Add to Cart']"
        ]
        
        add_to_cart_button = None
        for selector in add_to_cart_selectors:
            try:
                elements = first_product.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        add_to_cart_button = element
                        print(f"Found Add to Cart button")
                        break
                if add_to_cart_button:
                    break
            except Exception:
                continue
        
        if not add_to_cart_button:
            print("Looking for Add to Cart button on page...")
            for selector in add_to_cart_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            add_to_cart_button = element
                            break
                    if add_to_cart_button:
                        break
                except Exception:
                    continue
        
        success = False
        if add_to_cart_button:
            driver.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_button)
            time.sleep(1)
            
            driver.execute_script("arguments[0].click();", add_to_cart_button)
            print("Clicked Add to Cart button")
            
            try:
                cart_count_before = "0"
                try:
                    cart_count_element = driver.find_element(By.ID, "nav-cart-count")
                    if cart_count_element.is_displayed():
                        cart_count_before = cart_count_element.text
                except:
                    pass
                
                try:
                    def cart_count_changed(driver):
                        try:
                            new_count = driver.find_element(By.ID, "nav-cart-count").text
                            return new_count != cart_count_before
                        except:
                            return False
                    
                    wait.until(cart_count_changed)
                    
                    new_cart_count = driver.find_element(By.ID, "nav-cart-count").text
                    print(f"Cart updated from {cart_count_before} to {new_cart_count} items")
                    success = True
                    
                except TimeoutException:
                    print("Cart count didn't update, looking for confirmation message...")
                    confirmation_selectors = [
                        "#huc-v2-order-row-confirm-text",
                        "#NATC_SMART_WAGON_CONF_MSG_SUCCESS", 
                        "#sw-atc-confirmation",
                        "#attachDisplayAddBaseAlert"
                    ]
                    
                    for conf_selector in confirmation_selectors:
                        try:
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, conf_selector)))
                            success = True
                            print("Product added to cart successfully")
                            break
                        except:
                            continue
                
            except Exception as e:
                print(f"Error checking cart status: {e}")
        
        end_time = time.time()
        add_cart_time = end_time - start_time
        
        print(f"\nAdd to cart operation took {add_cart_time:.2f} seconds")
        if success:
            print("Product successfully added to cart!")
        else:
            print("Could not confirm if product was added to cart")
        
        self.assertLess(add_cart_time, 30, "Add to cart took too long")
    
    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":    
    unittest.main()