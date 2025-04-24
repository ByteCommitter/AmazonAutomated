from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
import time

# Set Chrome options
options = ChromeOptions()
# options.headless = True  # Uncomment if you want headless mode

# Set chromedriver path explicitly
service = ChromeService("/usr/bin/chromedriver")

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=service, options=options)


#task a for headphones
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
    
    #task b sort by price and on lowest to highest item
    print("Sorting by price: Low to High...")
    
    # Use a longer wait for the sort dropdown to be fully loaded
    #time.sleep(2)
    
    try:
        # First attempt: Try to find the dropdown by any selector that works
        sort_dropdown = None
        
        # Try multiple selectors to find the dropdown
        # selectors = [
        #     (By.CSS_SELECTOR, "[aria-label='Sort by:']"),
        #     (By.CSS_SELECTOR, ".a-dropdown-container .a-button-dropdown"),
        
        sort_dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Sort by:']")))

        if sort_dropdown:
            # Use JavaScript to safely click the element
            driver.execute_script("arguments[0].click();", sort_dropdown)
            print("Clicked sort dropdown using JavaScript")
            
            # Wait for dropdown options to appear
            time.sleep(1)
            
            # Try to find and click the "Price: Low to High" option
            # selectors = [
            #     (By.XPATH, "//a[contains(text(), 'Price: Low to High')]"),
            #     (By.XPATH, "//a[contains(@id, 's-result-sort-select') and contains(text(), 'Price: Low to High')]"),
            #
            price_option = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@id, 's-result-sort-select') and contains(text(), 'Price: Low to High')]")))
            driver.execute_script("arguments[0].click();", price_option)
            print("Clicked price option using JavaScript")

           
                    
            # Wait for sorting to complete
            print("Waiting for sorting to complete...")
            time.sleep(5)
            print("Sorting should be complete now")
            
            # Keep the browser open to see the results
            print("Keeping browser open for 15 seconds...")
            time.sleep(15)
        else:
            # Alternative method: use the direct URL with sorting parameter
            print("Could not find sort dropdown, using direct URL with sorting parameter...")
            current_url = driver.current_url
            if "?" in current_url:
                sorted_url = current_url + "&s=price-asc-rank"
            else:
                sorted_url = current_url + "?s=price-asc-rank"
            
            driver.get(sorted_url)
            print("Navigated to URL with sort parameter")
            time.sleep(15)
    
    except Exception as e:
        print(f"Error during sorting: {e}")
        # Fallback method: Use direct URL with sorting parameter
        print("Using fallback method: direct URL with sorting parameter...")
        current_url = driver.current_url
        if "?" in current_url:
            sorted_url = current_url + "&s=price-asc-rank"
        else:
            sorted_url = current_url + "?s=price-asc-rank"
        
        driver.get(sorted_url)
        print("Navigated to URL with sort parameter")
        time.sleep(15)
    
except Exception as e:
    print(f"An error occurred: {e}")



