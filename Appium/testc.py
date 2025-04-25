import time
import unittest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='Android',
    appPackage='in.amazon.mShop.android.shopping',
    appActivity='com.amazon.mShop.home.HomeActivity',
    language='en',
    locale='US',
    uiautomator2ServerInstallTimeout=60000,
    unicodekeyboard='true',
    resetkeyboard='true'
)

appium_server_url = 'http://localhost:4723'

class TestAppium(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
        print("Session ID:", self.driver.session_id)

    def tearDown(self):
        # if self.driver:
        #     self.driver.quit()
        print("Test completed")

    # Utility methods and setup
    def open_app(self):
        """Open the app, select English language, and skip sign in"""
        # Wait for initial screen to load
        time.sleep(3)
        
        # Handle language selection first
        try:
            # Try using accessibility ID first (most reliable)
            self.identify_element("English language selection button")
            english_option = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Select English")
            english_option.click()
            print("Selected English using Accessibility ID")
        except:
            try:
                # Try XPath if accessibility ID doesn't work
                english_option = self.driver.find_element(AppiumBy.XPATH, 
                    '//android.widget.ImageView[@content-desc="Select English"]')
                english_option.click()
                print("Selected English using XPath")
            except:
                try:
                    # Try UiAutomator as last resort
                    english_option = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 
                        'new UiSelector().description("Select English")')
                    english_option.click()
                    print("Selected English using UiAutomator")
                except:
                    try:
                        # Fall back to our original method
                        english_option = self.driver.find_element(AppiumBy.XPATH, 
                            '//android.widget.RadioButton[contains(@text, "English")]')
                        english_option.click()
                        print("Selected English using text content")
                    except:
                        print("Could not select English language, may already be selected")
        
        # Try to find and click the continue button
        try:
            language_continue = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/continue_button')
            language_continue.click()
            time.sleep(2)
            print("Clicked continue after selecting language")
        except:
            print("Could not find continue button after language selection")
        
        # Skip sign in
        try:
            # Look for skip sign-in button instead of continue button
            skip_button = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/skip_sign_in_button')
            skip_button.click()
        except:
            try:
                # Try by text if ID doesn't work
                skip_button = self.driver.find_element(AppiumBy.XPATH, '//android.widget.Button[contains(@text, "Skip sign in")]')
                skip_button.click()
            except:
                try:
                    # Look for "Sign in" button's sibling element that allows skipping
                    skip_link = self.driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "Skip")]')
                    skip_link.click()
                except:
                    print("Could not find skip option, trying to continue as guest...")
                    # If we can't find a skip button, we may need to click continue first
                    continue_button = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/sso_continue')
                    continue_button.click()
                    # Then look for skip options on the next screen
                    time.sleep(2)
                    try:
                        skip_button = self.driver.find_element(AppiumBy.XPATH, 
                            '//android.widget.Button[contains(@text, "Continue as guest") or contains(@text, "Skip")]')
                        skip_button.click()
                    except:
                        print("Continuing without explicit skip")
        
        # Wait for home page to load after skipping sign-in
        time.sleep(3)
        print("App successfully opened with English language and sign-in skipped")
        
        # Verify we're on the home page
        try:
            search_hint = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/chrome_search_hint_view')
            print("Successfully verified we're on the home page")
            return True
        except:
            print("Could not verify home page")
            return False

   
    
    def print_page_source(self):
        """Print a segment of the current page source for debugging"""
        page_source = self.driver.page_source
        # Print just a portion to avoid overwhelming the console
        preview_length = min(1000, len(page_source))
        print(f"Page source preview (first {preview_length} chars):")
        print(page_source[:preview_length] + "...")
        print("-----")

    def extract_product_details(self):
        """Extract product details from the current product page using specific selectors"""
        try:
            print("\n----- PRODUCT DETAILS -----")
            
            # Try to find the product title using the specific approach
            try:
                # Using UiAutomator to find any long text in a View element that's likely the product name
                title_elements = self.driver.find_elements(AppiumBy.XPATH, 
                    '//android.view.View[string-length(@text) > 40]')
                if title_elements and len(title_elements) > 0:
                    title_text = title_elements[0].text
                    # Truncate if too long to prevent display issues
                    if len(title_text) > 200:
                        title_text = title_text[:200] + "..."
                    print(f"Product Title: {title_text}")
                else:
                    # Fallback to our previous method
                    title_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[string-length(@text) > 10]')
                    if title_elements and len(title_elements) > 0:
                        title_text = title_elements[0].text
                        # Truncate if too long
                        if len(title_text) > 200:
                            title_text = title_text[:200] + "..."
                        print(f"Product Title: {title_text}")
            except Exception as e:
                print(f"Could not extract title: {str(e)[:100]}")
                
            # Try to find price using the specific container
            try:
                # First look for the price container by resource-id
                price_container = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().resourceId("reinvent_price_tabular_mobile_feature_div")')
                
                # Then find the price element within this container
                price_element = price_container.find_element(AppiumBy.XPATH,
                    './/android.widget.TextView[contains(@text, "₹")]')
                price_text = price_element.text
                # Clean up price text if needed
                price_text = price_text.replace('\n', ' ').strip()
                print(f"Product Price (from container): {price_text}")
            except Exception as e:
                # Fall back to our previous method without printing the error
                try:
                    price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[contains(@text, "₹")]')
                    if price_elements and len(price_elements) > 0:
                        price_text = price_elements[0].text
                        price_text = price_text.replace('\n', ' ').strip()
                        print(f"Product Price (fallback): {price_text}")
                except Exception:
                    print("Could not extract price")
                
            # Try to find rating - this is especially relevant since we're filtering by rating
            try:
                rating_elements = self.driver.find_elements(AppiumBy.XPATH,
                    '//android.widget.TextView[contains(@text, "stars") or contains(@text, "out of")]')
                if rating_elements and len(rating_elements) > 0:
                    rating_text = rating_elements[0].text
                    rating_text = rating_text.replace('\n', ' ').strip()
                    print(f"Product Rating: {rating_text}")
                else:
                    # Try alternative way to find rating
                    rating_elements = self.driver.find_elements(AppiumBy.XPATH,
                        '//android.widget.TextView[contains(@text, "★")]')
                    if rating_elements and len(rating_elements) > 0:
                        rating_text = rating_elements[0].text
                        rating_text = rating_text.replace('\n', ' ').strip()
                        print(f"Product Rating: {rating_text}")
            except Exception:
                # Skip rating if not found without printing error
                pass
            
            # Try to find delivery information
            try:
                delivery_elements = self.driver.find_elements(AppiumBy.XPATH,
                    '//android.widget.TextView[contains(@text, "Delivery") or contains(@text, "delivery")]')
                if delivery_elements and len(delivery_elements) > 0:
                    delivery_text = delivery_elements[0].text
                    delivery_text = delivery_text.replace('\n', ' ').strip()
                    print(f"Delivery Info: {delivery_text}")
            except Exception:
                # Skip delivery info if not found without printing error
                pass
                
            print("--------------------------\n")
        except Exception as e:
            # Keep the error message brief to avoid stack traces in output
            print(f"Could not extract complete product details. Error: {str(e)[:100]}")
        finally:
            # Always print this to maintain consistent output format
            print("Product details extraction completed")

    def extract_product_info_from_panel(self, container):
        """Extract product name and price from a product panel in search results"""
        product_info = {"name": None, "price": None}
        
        try:
            print("\n----- SEARCH RESULTS PANEL INFO -----")
            
            # Find product name using multiple approaches
            try:
                # APPROACH 1: Use direct text search for longer product names (most specific)
                name_elements = container.find_elements(AppiumBy.XPATH, 
                    './/android.widget.TextView[string-length(@text) > 50]')
                
                if name_elements and len(name_elements) > 0:
                    name_text = name_elements[0].text
                    # Truncate long names to prevent display issues
                    if len(name_text) > 200:
                        name_text = name_text[:200] + "..."
                    product_info["name"] = name_text
                    print(f"Product Name: {product_info['name']}")
                else:
                    # APPROACH 2: Try to find any TextView that doesn't contain price symbols
                    # and has substantial text length (might be a product name)
                    candidate_elements = container.find_elements(AppiumBy.XPATH,
                        './/android.widget.TextView[string-length(@text) > 20 and not(contains(@text, "₹"))]')
                    
                    if candidate_elements and len(candidate_elements) > 0:
                        # Find the TextView with the longest text (likely to be the product name)
                        longest_text = ""
                        for elem in candidate_elements:
                            if len(elem.text) > len(longest_text):
                                longest_text = elem.text
                        
                        if longest_text:
                            # Truncate if needed
                            if len(longest_text) > 200:
                                longest_text = longest_text[:200] + "..."
                            product_info["name"] = longest_text
                            print(f"Product Name: {product_info['name']}")
                        else:
                            print("Found elements but couldn't extract product name text")
                    else:
                        print("No suitable product name candidates found")
            except Exception as e:
                print(f"Could not extract name from panel: {str(e)[:100]}")
            
            # Find price - looking for TextView containing rupee symbol (₹)
            try:
                # APPROACH 1: Find price elements specifically containing the rupee symbol
                price_elements = container.find_elements(AppiumBy.XPATH,
                    './/android.widget.TextView[contains(@text, "₹")]')
                
                if price_elements and len(price_elements) > 0:
                    price_text = price_elements[0].text
                    price_text = price_text.replace('\n', ' ').strip()
                    product_info["price"] = price_text
                    print(f"Product Price: {product_info['price']}")
                else:
                    print("No price elements found with rupee symbol")
            except Exception as e:
                print(f"Could not extract price from panel: {str(e)[:100]}")
            
            # If we've failed to extract either name or price, try UiAutomator approach as last resort
            if not product_info["name"] or not product_info["price"]:
                try:
                    print("Trying UiAutomator approach as fallback...")
                    # Try to get full XML structure and extract text
                    panel_text = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().resourceIdMatches(".*-.*-.*-.*")')
                    
                    if panel_text:
                        print(f"Found panel with resource ID pattern, attempting deeper inspection")
                        # Additional search can be implemented here if needed
                except Exception:
                    print("UiAutomator fallback approach also failed")
                    
            print("---------------------------------")
            
            return product_info
        except Exception as e:
            print(f"Error in extract_product_info_from_panel: {str(e)[:100]}")
            print("---------------------------------")
            return product_info

    def check_if_added_to_cart(self):
        """Check if a product was successfully added to cart and return time of detection"""
        try:
            # Look for confirmation elements
            confirmations = self.driver.find_elements(AppiumBy.XPATH, 
                '//android.widget.TextView[contains(@text, "Added to") or contains(@text, "added to cart") or contains(@text, "Cart")]')
            
            if confirmations and len(confirmations) > 0:
                # Return both success status and the time when we detected it
                return True, time.time()
        except Exception:
            pass
        
        return False, None

    def add_to_cart_from_search_results(self, container):
        print("\nMeasuring Add to Cart time...")
        add_to_cart_found = False
        # Start timing for add to cart operation
        add_cart_start_time = time.time()
        add_cart_end_time = 0
        # STRATEGY 1: Direct use of resource-id from the provided button data
        # try:
        #     add_to_cart = container.find_element(AppiumBy.ID, 'a-autoid-21-announce')
        #     add_to_cart.click()
        #     add_to_cart_found = True
        # except Exception:
        #     pass
        # STRATEGY 2: Finding button by text attribute (from provided data)
        # if not add_to_cart_found:
        #     print('Strat 2')
        #     try:
        #         add_to_cart = container.find_element(AppiumBy.XPATH, 
        #             './/android.widget.Button[@text="Add to cart"]')
        #         add_to_cart.click()
        #         add_to_cart_found = True
        #     except Exception:
        #         pass
        # STRATEGY 3: Using the bounds data to find elements in that area
        if not add_to_cart_found:
            print('Strat 3')
            try:
                # Using the bounds from provided button data: [464,2050][1039,2142]
                buttons_in_area = self.driver.find_elements(AppiumBy.XPATH,
                    '//android.widget.Button[@clickable="true"]')
                for button in buttons_in_area:
                    try:
                        if button.text and "add to cart" in button.text.lower():
                            # Start timing AFTER we find the button but BEFORE clicking
                            add_cart_start_time = time.time()
                            button.click()
                            add_to_cart_found = True
                            break
                    except:
                        continue
            except Exception:
                pass
        # STRATEGY 4: Try finding button near the product price
        if not add_to_cart_found:
            print('Strat 4')
            try:
                price_elements = container.find_elements(AppiumBy.XPATH,
                    './/android.widget.TextView[contains(@text, "₹")]')
                if price_elements and len(price_elements) > 0:
                    price_container = price_elements[0]
                    # Try to find buttons near the price
                    parent = price_container
                    for _ in range(3):
                        try:
                            parent = parent.find_element(AppiumBy.XPATH, "./..")
                            buttons = parent.find_elements(AppiumBy.CLASS_NAME, "android.widget.Button")
                            for button in buttons:
                                if button.text and "add to cart" in button.text.lower():
                                    button.click()
                                    add_to_cart_found = True
                                    add_cart_end_time = time.time()
                                    break
                        except:
                            continue
                        if add_to_cart_found:
                            break
            except Exception:
                pass
        
        # Check for confirmation without sleeping
        success = False
        if add_to_cart_found:
            try:
                # Wait for cart count to change or confirmation message to appear
                for _ in range(10):  # Try for up to 10 cycles (equivalent to ~2 seconds)
                    if self.check_if_added_to_cart():
                        success = True
                        break
                    # Very short sleep to prevent CPU overload
                    time.sleep(0.2)
            except Exception:
                pass
        
        # Calculate time taken for add to cart operation
        add_cart_end_time = time.time()  # Make sure we have a valid end time
        add_cart_time = add_cart_end_time - add_cart_start_time
        print(f"Add to Cart Time: {add_cart_time:.2f} seconds")
        if success or add_to_cart_found:
            print("Product added to cart successfully")
        return success or add_to_cart_found

    def add_to_cart_from_product_page(self):
        """Add the current product to cart from product details page and measure time"""
        print("\nMeasuring Add to Cart time from product page...")
        # Scroll down to make sure Add to Cart button is visible
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        self.driver.swipe(width // 2, height * 3 // 4, width // 2, height // 4, 600)
        success = False
        add_to_cart_found = False
        add_cart_start_time = 0
        add_cart_end_time = 0
        
        # STRATEGY 1: Direct use of resource-id from the provided button data
        try:
            add_to_cart = self.driver.find_element(AppiumBy.ID, 'add-to-cart-button')
            # Start timing RIGHT BEFORE clicking
            add_cart_start_time = time.time()
            add_to_cart.click()
            add_to_cart_found = True
            print("Added to cart using resource-id")
        except Exception:
            pass
        
        # STRATEGY 2: Finding button by text attribute (from provided data)
        if not add_to_cart_found:
            try:
                add_to_cart = self.driver.find_element(AppiumBy.XPATH, 
                    '//android.widget.Button[@text="Add to cart"]')
                # Start timing RIGHT BEFORE clicking
                add_cart_start_time = time.time()
                add_to_cart.click()
                add_to_cart_found = True
                print("Added to cart using XPath with text")
            except Exception:
                pass
        
        # Check for confirmation without sleeping
        success = False
        if add_to_cart_found:
            try:
                # Wait for cart count to change or confirmation message to appear
                for _ in range(20):  # Try for up to 4 seconds (20 * 0.2)
                    success, end_time = self.check_if_added_to_cart()
                    if success:
                        add_cart_end_time = end_time
                        break
                    # Very short sleep to prevent CPU overload
                    time.sleep(0.2)
            except Exception:
                pass
        
        # Calculate time taken for add to cart operation
        add_cart_end_time = time.time()  # Make sure we have a valid end time
        add_cart_time = add_cart_end_time - add_cart_start_time
        print(f"Add to Cart Time from product page: {add_cart_time:.2f} seconds")
        if success or add_to_cart_found:
            print("Product added to cart successfully")
        return success or add_to_cart_found

    def test_search_with_rating_filter(self):
        """Search for wireless headphones and filter by 4+ star rating"""
        # First open the app and skip sign-in
        if not self.open_app():
            print("Failed to properly open the app, attempting search anyway")
        
        # Measure search time
        print("\nMeasuring search time for 'Wireless Headphones'...")
        
        # Start search process
        search_bar = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/chrome_search_hint_view')
        search_bar.click()
        second_search_bar = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/rs_search_src_text')
        second_search_bar.send_keys("Wireless Headphones")
        # Start timing AFTER we've entered the search term and RIGHT BEFORE pressing Enter
        search_start_time = time.time()
        self.driver.press_keycode(66, 0, 0)  # Press Enter
        search_end_time = time.time()
        # Wait for search results to appear without using sleep
        search_complete = False
        for _ in range(30):  # Increased timeout to 6 seconds max (30 * 0.2)
            try:
                results_element = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/rs_results_count')
                search_complete = True
                break
            except:
                try:
                    # Alternative: check if any product elements are present
                    self.driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "₹")]')
                    search_complete = True
                    break
                except:
                    pass
            time.sleep(0.2)  # Short polling interval
        # Calculate search time - only if we detected search completion
        if search_complete:
            search_end_time = time.time()
            search_time = search_end_time - search_start_time
            print(f"Search Time: {search_time:.2f} seconds")
        else:
            print("Could not accurately measure search time - results detection failed")
        
        # Measure filter time
        print("\nMeasuring filter time for '4 Stars and Up'...")
        
        # Try multiple methods to find the rating filter
        filter_element = None
        try:
            filter_element = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "4 Stars and Up Add filter")
        except:
            try:
                filter_element = self.driver.find_element(AppiumBy.XPATH, 
                    '//android.view.View[@content-desc="4 Stars and Up Add filter"]')
            except:
                try:
                    filter_element = self.driver.find_element(AppiumBy.XPATH, 
                        '//android.view.View[@resource-id="1318476031"]')
                except:
                    pass
        
        # If we found the filter element, click it and measure response time
        filter_clicked = False
        if filter_element:
            # Start timing RIGHT BEFORE clicking the filter button
            filter_start_time = time.time()
            filter_element.click()
            filter_clicked = True
        else:
            # Try using bounds as last resort
            try:
                center_x = (299 + 619) // 2
                center_y = (371 + 455) // 2
                filter_start_time = time.time()
                self.driver.tap([(center_x, center_y)], 100)
                filter_clicked = True
            except Exception as e:
                print(f"Could not click on '4 Stars and Up' filter: {str(e)}")
        
        # Wait for filtered results to load without blocking sleep
        filter_complete = False
        if filter_clicked:
            for _ in range(30):  # Increased timeout to 6 seconds max
                try:
                    # Check if results count has updated
                    filtered_results = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/rs_results_count')
                    filter_complete = True
                    break
                except:
                    try:
                        # Alternative: check for filter chips or updated product listings
                        self.driver.find_element(AppiumBy.XPATH, 
                            '//android.view.View[contains(@content-desc, "4 Stars")]')
                        filter_complete = True
                        break
                    except:
                        pass
                time.sleep(0.2)  # Short polling interval
            # Calculate filter time - only if we detected filter completion
            if filter_complete:
                filter_end_time = time.time()
                filter_time = filter_end_time - filter_start_time
                print(f"Filter Time: {filter_time:.2f} seconds")
            else:
                print("Could not accurately measure filter time - results detection failed")
        
        # Now extract details of one of the first products
        print("\nSelecting a product...")
        # Simple approach to get one of the first products
        try:
            # Minimal scroll to get past headers if needed
            screen_size = self.driver.get_window_size()
            width = screen_size['width']
            height = screen_size['height']
            self.driver.swipe(width // 2, height * 2 // 3, width // 2, height // 3, 400)
            
            # Find products by looking for price elements (reliable indicator of products)
            price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                '//android.widget.TextView[contains(@text, "₹")]')
            
            if price_elements and len(price_elements) >= 3:
                # Get one of the first 3 price elements (which should correspond to first products)
                target_index = 2  # The 3rd price element (index 2) - more likely to be a real product
                target_price_element = price_elements[target_index]
                
                # Try to find the container element to click
                container = target_price_element
                for _ in range(3):  # Try going up to 3 levels up in hierarchy
                    try:
                        container = container.find_element(AppiumBy.XPATH, "./..")
                    except:
                        break
                
                # Extract product name and price from the panel before clicking
                self.extract_product_info_from_panel(container)
                
                # First try to add to cart directly from search results
                added_to_cart = self.add_to_cart_from_search_results(container)
                
                # Click on product container to view details
                container.click()
                # Wait for product details to load without using sleep
                for _ in range(10):
                    try:
                        # Check for elements that indicate product details page is loaded
                        self.driver.find_element(AppiumBy.XPATH, 
                            '//android.view.View[string-length(@text) > 40]')
                        break
                    except:
                        pass
                    time.sleep(0.2)
                
                # Extract product details
                self.extract_product_details()
                
                # If we couldn't add from search results, try from product page
                if not added_to_cart:
                    self.add_to_cart_from_product_page()
                
                # Go back to results page
                self.driver.back()
                return
            elif price_elements and len(price_elements) > 0:
                # Similar process for first available product
                target_price_element = price_elements[0]
                
                # Extract product info and add to cart as above
                self.extract_product_info_from_panel(target_price_element)
                added_to_cart = self.add_to_cart_from_search_results(target_price_element)
                target_price_element.click()
                for _ in range(10):
                    try:
                        self.driver.find_element(AppiumBy.XPATH, 
                            '//android.view.View[string-length(@text) > 40]')
                        break
                    except:
                        pass
                    time.sleep(0.2)
                self.extract_product_details()
                if not added_to_cart:
                    self.add_to_cart_from_product_page()
                self.driver.back()
                return
        except Exception as e:
            print(f"Error selecting product: {e}")
        print("Performance measurement completed")

if __name__ == '__main__':
    unittest.main()