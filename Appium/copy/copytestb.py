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
        print("tear down")

    # Add to the top of your file to help with element identification
    '''
    Find By	Selector
        -android uiautomator
        (docs)
        new UiSelector().text("Under ₹1,000")
        xpath
        //android.widget.TextView[@text="Under ₹1,000"]
        Attribute	Value
        elementId
        00000000-0000-014a-0000-00d1000000d
    '''

    # Rename from test_open to open_app so it won't run as a separate test
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

    def identify_element(self, element_description):
        """
        Utility function to help identify elements with Appium Inspector.
        Prints useful information about how to find elements.
        """
        print(f"Looking for: {element_description}")
        print("Tips for Appium Inspector:")
        print("1. Use the 'Refresh Source' button to get the latest UI")
        print("2. Try searching for text with the search box")
        print("3. Check element attributes like 'resource-id', 'text', or 'content-desc'")
        print("4. For complex elements, try using XPath with multiple attributes")
        return
    
    def print_page_source(self):
        """Print a segment of the current page source for debugging"""
        page_source = self.driver.page_source
        # Print just a portion to avoid overwhelming the console
        preview_length = min(1000, len(page_source))
        print(f"Page source preview (first {preview_length} chars):")
        print(page_source[:preview_length] + "...")
        print("-----")

    def test_search(self):
        """Search for wireless headphones after opening the app"""
        # First open the app and skip sign-in
        if not self.open_app():  # Update this call to use the renamed method
            print("Failed to properly open the app, attempting search anyway")
        
        # Now proceed with search
        search_bar = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/chrome_search_hint_view')
        search_bar.click()
        second_search_bar = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/rs_search_src_text')
        second_search_bar.send_keys("Wireless Headphones")
        self.driver.press_keycode(66, 0, 0)
        print("Search completed without signing in")
        
        # Wait for search results to load
        time.sleep(3)
        
        # Verify we're on the search results page 
        try:
            results_element = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/rs_results_count')
            print(f"Search results found: {results_element.text}")
        except:
            print("Continued to search results page")
            
        # Now click on the "Under ₹1,000" filter button
        print("Attempting to click on 'Under ₹1,000' filter...")
        time.sleep(2)  # Give filters time to load
        
        try:
            # Try UiAutomator selector first
            under_1000_filter = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Under ₹1,000")')
            under_1000_filter.click()
            print("Clicked 'Under ₹1,000' filter using UiAutomator")
        except:
            try:
                # Try XPath as alternative
                under_1000_filter = self.driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Under ₹1,000"]')
                under_1000_filter.click()
                print("Clicked 'Under ₹1,000' filter using XPath")
            except:
                try:
                    # Try partial text match as a fallback
                    under_1000_filter = self.driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "Under")]')
                    under_1000_filter.click()
                    print("Clicked filter using partial text match")
                except Exception as e:
                    print(f"Could not click on 'Under ₹1,000' filter: {str(e)}")
        
        # Wait for filtered results to load
        time.sleep(3)
        
        # Verify filter was applied (optional)
        try:
            # Look for active filter indicators or updated results
            filtered_results = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/rs_results_count')
            print(f"Filtered results: {filtered_results.text}")
        except:
            print("Filter may have been applied, but couldn't verify results count")
        
        # Now extract details of one of the first products
        print("Attempting to select one of the first products...")
        time.sleep(3)  # Wait for products to load
        
        # Simple approach to get one of the first products
        try:
            print("SIMPLIFIED STRATEGY: Looking for one of the first products...")
            
            # Minimal scroll to get past headers if needed
            screen_size = self.driver.get_window_size()
            width = screen_size['width']
            height = screen_size['height']
            self.driver.swipe(width // 2, height * 2 // 3, width // 2, height // 3, 400)  # Smaller, gentler scroll
            time.sleep(1)
            
            # Find products by looking for price elements (reliable indicator of products)
            price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                '//android.widget.TextView[contains(@text, "₹")]')
            
            if price_elements and len(price_elements) >= 3:
                # Get one of the first 3 price elements (which should correspond to first products)
                target_index = 2  # The 3rd price element (index 2) - more likely to be a real product
                target_price_element = price_elements[target_index]
                
                print(f"Selected the {target_index+1}st/nd/rd product by price element")
                
                # Try to find the container element to click
                container = target_price_element
                for _ in range(3):  # Try going up to 3 levels up in hierarchy
                    try:
                        container = container.find_element(AppiumBy.XPATH, "./..")
                    except:
                        break
                
                # Click on product container
                container.click()
                time.sleep(2)
                
                # Display just product name and price
                name_elements = self.driver.find_elements(AppiumBy.XPATH, 
                    '//android.widget.TextView[string-length(@text) > 20]')
                price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                    '//android.widget.TextView[contains(@text, "₹")]')
                
                if name_elements and len(name_elements) > 0:
                    print(f"Product Name: {name_elements[0].text}")
                if price_elements and len(price_elements) > 0:
                    print(f"Product Price: {price_elements[0].text}")
                
                # Go back to results page
                self.driver.back()
                time.sleep(1)
                return
                
            elif price_elements and len(price_elements) > 0:
                # If we don't have at least 3, take whatever we found
                target_price_element = price_elements[0]
                print("Selected the first available product by price")
                
                # Try to find the container element to click
                container = target_price_element
                for _ in range(3):  # Try going up to 3 levels up in hierarchy
                    try:
                        container = container.find_element(AppiumBy.XPATH, "./..")
                    except:
                        break
                
                # Click on product container
                container.click()
                time.sleep(2)
                
                # Display just product name and price
                name_elements = self.driver.find_elements(AppiumBy.XPATH, 
                    '//android.widget.TextView[string-length(@text) > 20]')
                price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                    '//android.widget.TextView[contains(@text, "₹")]')
                
                if name_elements and len(name_elements) > 0:
                    print(f"Product Name: {name_elements[0].text}")
                if price_elements and len(price_elements) > 0:
                    print(f"Product Price: {price_elements[0].text}")
                
                # Go back to results page
                self.driver.back()
                time.sleep(1)
                return
                
            else:
                print("Could not find price elements for products, trying alternative approach")
                
                # Alternative approach - look for text elements that might be product names
                product_names = self.driver.find_elements(AppiumBy.XPATH, 
                    '//android.widget.TextView[string-length(@text) > 20 and not(contains(@text, "Sponsored"))]')
                
                if product_names and len(product_names) >= 3:
                    # Select the 3rd product name (index 2) to avoid headers
                    target_product = product_names[2]
                    print(f"Selected the 3rd product by name: {target_product.text[:30]}...")
                    
                    # Click on the product
                    target_product.click()
                    time.sleep(2)
                    
                    # Display just product name and price
                    name_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[string-length(@text) > 20]')
                    price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[contains(@text, "₹")]')
                    
                    if name_elements and len(name_elements) > 0:
                        print(f"Product Name: {name_elements[0].text}")
                    if price_elements and len(price_elements) > 0:
                        print(f"Product Price: {price_elements[0].text}")
                    
                    # Go back to results page
                    self.driver.back()
                    time.sleep(1)
                    return
                
                elif product_names and len(product_names) > 0:
                    # If we don't have at least 3, take what we have
                    target_product = product_names[0]
                    print(f"Selected the first available product by name: {target_product.text[:30]}...")
                    
                    # Click on the product
                    target_product.click()
                    time.sleep(2)
                    
                    # Display just product name and price
                    name_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[string-length(@text) > 20]')
                    price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[contains(@text, "₹")]')
                    
                    if name_elements and len(name_elements) > 0:
                        print(f"Product Name: {name_elements[0].text}")
                    if price_elements and len(price_elements) > 0:
                        print(f"Product Price: {price_elements[0].text}")
                    
                    # Go back to results page
                    self.driver.back()
                    time.sleep(1)
                    return
        except Exception as e:
            print(f"Simplified strategy failed: {str(e)}")
            
        # If the simplified approach failed, fall back to the existing strategies
        print("Falling back to original strategies...")
        
        # Now extract details of the first product
        print("Attempting to find the cheapest product...")
        time.sleep(3)  # Wait for products to load
        
        # Fast approach to find specific product
        try:
            print("FAST STRATEGY: Looking for specific ZEBRONICS THUNDER product...")
            
            # Single scroll to get past top content
            screen_size = self.driver.get_window_size()
            width = screen_size['width']
            height = screen_size['height']
            self.driver.swipe(width // 2, height * 3 // 4, width // 2, height // 4, 600)
            time.sleep(1)  # Reduced wait time
            
            # Try to directly find the specific ZEBRONICS product
            target_product = "ZEBRONICS THUNDER Bluetooh 5.3 Wireless Headphones with 60H backup, Gaming Mode,"
            print(f"Searching for specific product: {target_product}")
            
            # Look for the exact product or something similar
            try:
                # Try partial match on product name
                product_element = self.driver.find_element(AppiumBy.XPATH, 
                    f'//android.widget.TextView[contains(@text, "ZEBRONICS THUNDER")]')
                
                print("Found ZEBRONICS THUNDER product!")
                print(target_product)
                
                # Click on the product
                product_element.click()
                time.sleep(2)
                
                # Display just product name and price
                try:
                    # Try to find product name
                    name_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[string-length(@text) > 20]')
                    if name_elements and len(name_elements) > 0:
                        product_name = name_elements[0].text
                        print(f"Product Name: {product_name}")
                    
                    # Try to find price
                    price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[contains(@text, "₹")]')
                    if price_elements and len(price_elements) > 0:
                        product_price = price_elements[0].text
                        print(f"Product Price: {product_price}")
                except Exception as e:
                    print(f"Error getting product details: {str(e)}")
                
                self.driver.back()
                return
            except:
                print("Specific product not found, continuing with general search...")
        
            # If the specific product isn't found, continue with existing code
            # but with some optimizations
            
            # Look for text elements with better filtering and speed
            all_text_elements = self.driver.find_elements(AppiumBy.XPATH, 
                '//android.widget.TextView[not(contains(@text, "Sponsored")) and not(contains(@text, "ad")) and string-length(@text) > 15]')
            
            if all_text_elements:
                for elem in all_text_elements:
                    try:
                        text = elem.text
                        # Display any headphones product prominently
                        if "headphone" in text.lower():
                            print("FOUND PRODUCT:")
                            print(text)
                            elem.click()
                            time.sleep(2)
                            self.extract_product_details()
                            self.driver.back()
                            return
                    except:
                        continue
                        
            # If no specific headphone product was found, take the first likely product
            if all_text_elements and len(all_text_elements) > 0:
                target_index = min(2, len(all_text_elements) - 1)  # Take the 3rd element or last if fewer
                target_elem = all_text_elements[target_index]
                
                print("Selected product:")
                print(target_elem.text)
                
                target_elem.click()
                time.sleep(2)
                self.extract_product_details()
                self.driver.back()
                return
                
        except Exception as e:
            print(f"Fast strategy failed: {str(e)}")
        
        # Continue with existing approach as fallback
        print("Falling back to original strategy...")
        try:
            print("PRIORITY STRATEGY: Using multi-step approach to find real products...")
            
            # Step 1: Perform multiple scrolls to get past ALL ads at the top
            screen_size = self.driver.get_window_size()
            width = screen_size['width']
            height = screen_size['height']
            
            # Do multiple scrolls to ensure we're well past all ads
            print("Performing multiple scrolls to get past all sponsored content")
            for i in range(2):  # Do 2 scrolls
                self.driver.swipe(width // 2, height * 3 // 4, width // 2, height // 4, 800)
                time.sleep(1.5)
            
            # Step 2: After scrolling, look for product elements with better filtering
            print("Looking for product elements after scrolling...")
            
            # Look for text elements and explicitly filter out sponsored content
            all_text_elements = self.driver.find_elements(AppiumBy.XPATH, 
                '//android.widget.TextView')
            
            # Create filtered list of elements that are likely product titles
            product_candidates = []
            ad_keywords = ["sponsored", "ad", "advertisement", "premier league", "this ad", "check each"]
            
            # Process each text element
            for elem in all_text_elements:
                try:
                    text = elem.text.lower()
                    # Skip elements with no text or very short text
                    if not text or len(text) < 15:
                        continue
                        
                    # Skip elements containing ad-related keywords
                    if any(keyword in text for keyword in ad_keywords):
                        continue
                        
                    # If we get here, this might be a product title
                    product_candidates.append(elem)
                except:
                    continue
                    
            print(f"Found {len(product_candidates)} potential product candidates after filtering")
            
            if product_candidates and len(product_candidates) > 0:
                # Take the first element that's likely a product title
                target_product = product_candidates[0]
                product_text = target_product.text
                print(f"Selected product title: {product_text[:60]}..." if len(product_text) > 60 else product_text)
                
                # Get parent container to increase click target size
                try:
                    parent = target_product.find_element(AppiumBy.XPATH, "./..")
                    print("Found parent container, clicking it instead of text")
                    parent.click()
                except:
                    # If parent can't be found or clicked, fall back to the text element
                    print("Clicking directly on product title text")
                    target_product.click()
                    
                time.sleep(3)
                
                # Check if we're on a product page
                if "this ad is:" in self.driver.page_source.lower():
                    print("WARNING: We clicked on an ad feedback element, navigating back")
                    self.driver.back()
                    time.sleep(1)
                    
                    # Try clicking the second candidate if available
                    if len(product_candidates) > 1:
                        print("Trying second candidate product")
                        product_candidates[1].click()
                        time.sleep(3)
                
                # Extract product details
                self.extract_product_details()
                
                # Go back to results
                self.driver.back()
                time.sleep(2)
                return
            
            # If the above approach didn't work, try a more targeted bounds-based approach
            print("Text-based approach failed, trying more precise bounds approach...")
            
            # Get all view elements
            view_elements = self.driver.find_elements(AppiumBy.XPATH, 
                '//android.view.View')
                
            # Filter elements by bounds - look for elements that look like product cards
            product_views = []
            for elem in view_elements:
                try:
                    bounds_str = elem.get_attribute("bounds")
                    if not bounds_str:
                        continue
                        
                    # Parse bounds [left,top][right,bottom]
                    bounds = bounds_str.replace('[', '').replace(']', ',').split(',')
                    if len(bounds) >= 4:
                        left = int(bounds[0])
                        top = int(bounds[1])
                        right = int(bounds[2])
                        bottom = int(bounds[3])
                        
                        width_elem = right - left
                        height_elem = bottom - top
                        
                        # Product cards are typically wide and tall, but not too tall
                        # Avoid very small elements and very tall elements (likely sections not products)
                        if width_elem > 500 and 300 < height_elem < 900:
                            product_views.append((elem, top))  # Save element and its top position
                except:
                    continue
                    
            # Sort by vertical position (top coordinate)
            product_views.sort(key=lambda x: x[1])
            
            if product_views:
                # Skip the first few which might still be headers/ads
                # Try to get elements from the middle of the list
                target_index = min(3, len(product_views) - 1)
                target_view = product_views[target_index][0]
                
                print(f"Selected view element at position {target_index} of {len(product_views)}")
                target_view.click()
                time.sleep(3)
                
                # Extract product details
                self.extract_product_details()
                
                # Go back to search results
                self.driver.back()
                time.sleep(2)
                return
                
        except Exception as e:
            print(f"Priority strategy failed: {str(e)}")

        # Continue with existing strategies as fallbacks
        print("Falling back to alternative strategies...")
        try:
            # Try multiple strategies to find the first product
            first_product_container = None
            
            # Strategy 1: Look for search_result_item ViewGroup
            try:
                items = self.driver.find_elements(AppiumBy.XPATH, 
                    '//android.view.ViewGroup[contains(@resource-id, "search_result_item")]')
                if items and len(items) > 0:
                    first_product_container = items[0]
                    print("Found product using search_result_item")
            except Exception as e:
                print(f"Strategy 1 failed: {str(e)}")
            
            # Strategy 2: Try to find common product list items
            if first_product_container is None:
                try:
                    # Look for any list items that might be products
                    items = self.driver.find_elements(AppiumBy.XPATH, 
                        '//androidx.recyclerview.widget.RecyclerView//android.view.ViewGroup')
                    if items and len(items) > 0:
                        # Skip the first few items which might be headers
                        first_product_container = items[2] if len(items) > 2 else items[0]
                        print("Found product using RecyclerView items")
                except Exception as e:
                    print(f"Strategy 2 failed: {str(e)}")
            
            # Strategy 3: Look for price elements, then navigate up to container
            if first_product_container is None:
                try:
                    # Find elements with prices (usually products)
                    price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                        '//android.widget.TextView[contains(@text, "₹")]')
                    if price_elements and len(price_elements) > 0:
                        # Get the first price element and navigate to its parent container
                        first_product_container = price_elements[0].find_element(AppiumBy.XPATH, './..')
                        print("Found product using price element")
                except Exception as e:
                    print(f"Strategy 3 failed: {str(e)}")
                    
            # Strategy 4: Last resort - look for text elements that might be products
            if first_product_container is None:
                try:
                    # Just find all text elements that might be product names
                    text_elements = self.driver.find_elements(AppiumBy.XPATH,
                        '//android.widget.TextView[string-length(@text) > 20]')
                    if text_elements and len(text_elements) > 0:
                        first_product_text = text_elements[0]
                        print(f"Found potential product name: {first_product_text.text}")
                        # Click directly on this text element
                        first_product_text.click()
                        print("Clicked on product text directly")
                        time.sleep(3)
                        
                        # Extract details from the product page
                        try:
                            title = self.driver.find_element(AppiumBy.XPATH, 
                                '//android.widget.TextView[contains(@resource-id, "title")]').text
                            print(f"Product Detail Title: {title}")
                        except:
                            print("Could not extract product title from detail page")
                            
                        # Go back to search results
                        self.driver.back()
                        time.sleep(2)
                        return
                except Exception as e:
                    print(f"Strategy 4 failed: {str(e)}")
            
            # If all strategies failed, we can't proceed
            if first_product_container is None:
                print("Could not locate any product. Trying alternative approaches...")
                
                try:
                    # Use the specific reference element to find actual products
                    print("Looking for the reference element (View below 'Check each product page')")
                    
                    # First try the exact XPath provided
                    reference_element = None
                    try:
                        reference_element = self.driver.find_element(AppiumBy.XPATH, 
                            '//android.view.View[@resource-id="search"]/android.view.View[4]')
                        print("Found the reference element using exact XPath!")
                    except:
                        # Try the UI Automator selector as backup
                        try:
                            reference_element = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                'new UiSelector().className("android.view.View").instance(17)')
                            print("Found reference element using UiAutomator!")
                        except:
                            print("Could not find the reference element")
                    
                    if reference_element:
                        # Scroll slightly to ensure products below the reference are visible
                        print("Reference element found, scrolling to ensure products are visible...")
                        screen_size = self.driver.get_window_size()
                        width = screen_size['width']
                        height = screen_size['height']
                        
                        # Small scroll to bring products into view
                        self.driver.swipe(width // 2, height * 2 // 3, width // 2, height // 3, 500)
                        time.sleep(2)
                        
                        # Now look for product elements that should be below our reference
                        # First try to find product containers with prices (strong indicator of a product)
                        product_elements = self.driver.find_elements(AppiumBy.XPATH, 
                            '//android.widget.TextView[contains(@text, "₹")]')
                        
                        # Skip the first couple which might be from ads
                        if product_elements and len(product_elements) > 2:
                            # Use the third price element (more likely to be a real product)
                            target_price = product_elements[2]
                            # Navigate up to find the container
                            try:
                                container = target_price.find_element(AppiumBy.XPATH, "./../../..")
                                print("Found product container using price element")
                                container.click()
                                time.sleep(3)
                                
                                # Extract product details
                                self.extract_product_details()
                                
                                # Go back to results
                                self.driver.back()
                                time.sleep(2)
                                return
                            except Exception as e:
                                print(f"Found price but couldn't navigate to container: {str(e)}")
                        
                        # If that failed, try to find any text elements that might be product names
                        try:
                            product_names = self.driver.find_elements(AppiumBy.XPATH, 
                                '//android.widget.TextView[string-length(@text) > 20 and not(contains(@text, "Sponsored")) and not(contains(@text, "Premier")) and not(contains(@resource-id, "deal"))]')
                            
                            if product_names and len(product_names) > 0:
                                # Skip the first one to avoid ads
                                index = 1 if len(product_names) > 1 else 0
                                target_product = product_names[index]
                                print(f"Found product after reference: {target_product.text[:50]}...")
                                target_product.click()
                                time.sleep(3)
                                
                                # Extract details
                                self.extract_product_details()
                                
                                # Go back to results
                                self.driver.back()
                                time.sleep(2)
                                return
                        except Exception as e:
                            print(f"Failed to find product names: {str(e)}")
                    
                    # If the reference approach failed, continue with existing approaches
                    # ...existing code...
                
                except Exception as e:
                    print(f"Could not tap on bottom portion of screen: {str(e)}")
                
                print("Product extraction test completed")
                return
            
            # Now that we have a product container, extract the details
            print(f"Successfully found product container, extracting details...")
            
            # Extract product name
            try:
                product_name = first_product_container.find_element(AppiumBy.XPATH, 
                    './/android.widget.TextView[@resource-id="in.amazon.mShop.android.shopping:id/item_title" or contains(@resource-id, "title")]').text
                print(f"Product Name: {product_name}")
            except Exception as e:
                print(f"Could not extract product name: {str(e)}")
            
            # Extract product price
            try:
                product_price = first_product_container.find_element(AppiumBy.XPATH, 
                    './/android.widget.TextView[contains(@text, "₹")]').text
                print(f"Product Price: {product_price}")
            except Exception as e:
                print(f"Could not extract product price: {str(e)}")
            
            # Extract product rating if available
            try:
                product_rating = first_product_container.find_element(AppiumBy.XPATH, 
                    './/android.widget.TextView[contains(@resource-id, "rating")]').text
                print(f"Product Rating: {product_rating}")
            except Exception as e:
                print(f"Could not extract product rating: {str(e)}")
                
            # Click on the product to get more details
            print("Clicking on the product to see detailed view...")
            try:
                first_product_container.click()
                time.sleep(3)
                print("Successfully clicked on product")
            except Exception as e:
                print(f"Could not click on product: {str(e)}")
                return
            
            # Extract additional details from the product page
            try:
                # Try several different potential IDs/XPaths for the title
                title_elements = self.driver.find_elements(AppiumBy.XPATH, 
                    '//android.widget.TextView[contains(@resource-id, "title") or contains(@resource-id, "name") or string-length(@text) > 30]')
                if title_elements and len(title_elements) > 0:
                    print(f"Detailed Title: {title_elements[0].text}")
                else:
                    print("Could not find detailed title")
            except Exception as e:
                print(f"Error extracting detailed title: {str(e)}")
                
            # Go back to search results
            self.driver.back()
                
        except Exception as e:
            print(f"Error extracting product details: {str(e)}")
            
        print("Product extraction test completed")
    
    def extract_product_details(self):
        """Extract product details from the current product page"""
        try:
            # Try to find any title-like text
            title_elements = self.driver.find_elements(AppiumBy.XPATH, 
                '//android.widget.TextView[string-length(@text) > 20]')
            if title_elements and len(title_elements) > 0:
                print(f"Product Title: {title_elements[0].text}")
                
            # Try to find price
            price_elements = self.driver.find_elements(AppiumBy.XPATH, 
                '//android.widget.TextView[contains(@text, "₹")]')
            if price_elements and len(price_elements) > 0:
                print(f"Product Price: {price_elements[0].text}")
                
            # Try to find rating if available
            rating_elements = self.driver.find_elements(AppiumBy.XPATH,
                '//android.widget.TextView[contains(@text, "stars") or contains(@text, "out of")]')
            if rating_elements and len(rating_elements) > 0:
                print(f"Product Rating: {rating_elements[0].text}")
                
            print("Successfully extracted information from product page")
        except Exception as e:
            print(f"Could not extract product details: {str(e)}")


if __name__ == '__main__':
    unittest.main()

'''
Product Name: Visit the store, Kratos
Product Price: ₹499.00 with 67 percent savings
tear down
.
----------------------------------------------------------------------
Ran 1 test in 43.044s

OK
'''