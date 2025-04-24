from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
import time

# Function to get first product details
def get_first_product_details(driver, wait):
    """
    Extract the name and price of the first product from search results.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        None, prints product details to console
    """
    try:
        print("Attempting to extract first product information...")
        
        # Wait for product grid to load and add additional time for stability
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        time.sleep(2)  # Additional time for page to stabilize
        
        # Get the first product element
        first_product = driver.find_element(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        
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
        print("--------------------------------\n")
        
        # For debugging: save screenshot
        driver.save_screenshot("highest_rated_product.png")
        print("Screenshot saved as 'highest_rated_product.png'")
        
    except Exception as e:
        print(f"Error extracting product information: {e}")
        driver.save_screenshot("error_state.png")
        print("Error state screenshot saved as 'error_state.png'")

# Set Chrome options
options = ChromeOptions()
# options.headless = True  # Uncomment if you want headless mode

# Set chromedriver path explicitly
service = ChromeService("/usr/bin/chromedriver")

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Main execution
try:
    # Visit Amazon.in
    print("Navigating to Amazon.in...")
    driver.get("https://www.amazon.in")
    print(f"Page Title: {driver.title}")
    
    # Wait for search box to be available and then search for wireless headphones
    print("Searching for wireless headphones...")
    wait = WebDriverWait(driver, 10)
    search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
    search_box.clear()
    search_box.send_keys("wireless headphones")
    search_box.send_keys(Keys.RETURN)
    
    # Wait for search results to load
    wait.until(EC.title_contains("wireless headphones"))
    print(f"Search results page title: {driver.title}")
    
    # Filter by star rating first (highest rated items)
    print("Filtering by 4 Stars & Up...")
    
    try:
        # Wait for the filters to be visible
        time.sleep(2)
        
        # Look for the 4 Stars & Up filter option
        star_filter_selectors = [
            "//span[contains(text(), '4 Stars & Up')]",
            "//i[contains(@class, 'a-star-medium-4')]/span[contains(@class, 'a-icon-alt')]",
            "//span[contains(text(), '4 Stars') and contains(text(), 'Up')]",
            "//i[contains(@class, 'a-icon-star')]/..//span[contains(text(), '4 Stars')]"
        ]
        
        star_filter = None
        for selector in star_filter_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    for element in elements:
                        try:
                            # Check if this element is clickable (visible and in viewport)
                            if element.is_displayed():
                                star_filter = element
                                print(f"Found star filter using selector: {selector}")
                                break
                        except:
                            continue
                if star_filter:
                    break
            except:
                continue
        
        if star_filter:
            # Use JavaScript to safely click the element
            driver.execute_script("arguments[0].click();", star_filter)
            print("Clicked 4 Stars & Up filter using JavaScript")
            
            # Wait for filtering to complete
            print("Waiting for filtering to complete...")
            time.sleep(5)
        else:
            print("Could not find 4 Stars & Up filter, trying alternative selectors...")
            
            # Try clicking on a star rating element in the left sidebar
            try:
                # Click on the star rating section in the left sidebar (might need to scroll into view)
                sidebar_star_selectors = [
                    "//div[contains(@id, 'reviewsRefinements')]//i[contains(@class, 'a-icon-star')]",
                    "//div[contains(@id, 'filters')]//span[contains(text(), 'Customer Reviews')]",
                    "//span[contains(text(), 'Customer Reviews')]/parent::*"
                ]
                
                for selector in sidebar_star_selectors:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        if elements:
                            for element in elements:
                                if element.is_displayed():
                                    # Scroll to the element
                                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    time.sleep(1)
                                    # Click it
                                    driver.execute_script("arguments[0].click();", element)
                                    print(f"Clicked star rating section using selector: {selector}")
                                    
                                    # Now try to find and click specifically on 4 Stars & Up
                                    time.sleep(1)
                                    four_star_elements = driver.find_elements(By.XPATH, "//span[contains(text(), '4 Stars & Up')]")
                                    if four_star_elements:
                                        for four_star in four_star_elements:
                                            if four_star.is_displayed():
                                                driver.execute_script("arguments[0].click();", four_star)
                                                print("Clicked 4 Stars & Up option")
                                                time.sleep(3)
                                                break
                                    break
                        if element.is_displayed():
                            break
                    except:
                        continue
            except Exception as sidebar_error:
                print(f"Error clicking sidebar star filter: {sidebar_error}")
    
    except Exception as e:
        print(f"Error during star filtering: {e}")
    
    # Now sort by price (lowest to highest)
    print("Now sorting by price: Low to High...")
    
    try:
        # Find and click the sort dropdown
        sort_dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Sort by:']")))
        
        # Use JavaScript to safely click the element
        driver.execute_script("arguments[0].click();", sort_dropdown)
        print("Clicked sort dropdown using JavaScript")
        
        # Wait for dropdown options to appear
        time.sleep(1)
        
        # Find and click the "Price: Low to High" option
        price_option = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@id, 's-result-sort-select') and contains(text(), 'Price: Low to High')]")))
        driver.execute_script("arguments[0].click();", price_option)
        print("Clicked price option using JavaScript")
        
        # Wait for sorting to complete
        print("Waiting for sorting to complete...")
        time.sleep(5)
    
    except Exception as e:
        print(f"Error during price sorting: {e}")
        # Fallback method: Use direct URL with sorting parameter
        print("Using fallback method: direct URL with sorting parameter...")
        current_url = driver.current_url
        if "?" in current_url:
            sorted_url = current_url + "&s=price-asc-rank"
        else:
            sorted_url = current_url + "?s=price-asc-rank"
        
        driver.get(sorted_url)
        print("Navigated to URL with sort parameter")
        time.sleep(5)
    
    # Get the first product (lowest priced) details
    get_first_product_details(driver, wait)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Keep the browser open for a few more seconds to see results
    time.sleep(5)
    
    # Close the browser
    print("Closing browser...")
    driver.quit()
    print("Script execution completed")