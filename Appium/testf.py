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

    def tearDown(self):
        # if self.driver:
        #     self.driver.quit()
        print("tear down")

    # Add to the top of your file to help with element identification
    # def identify_element(self, element_description):
    #     """
    #     Utility function to help identify elements with Appium Inspector.
    #     Prints useful information about how to find elements.
    #     """
    #     print(f"Looking for: {element_description}")
    #     print("Tips for Appium Inspector:")
    #     print("1. Use the 'Refresh Source' button to get the latest UI")
    #     print("2. Try searching for text with the search box")
    #     print("3. Check element attributes like 'resource-id', 'text', or 'content-desc'")
    #     print("4. For complex elements, try using XPath with multiple attributes")
    #     return

    # Rename from test_open to open_app so it won't run as a separate test
    def open_app(self):
        """Open the app, select English language, and skip sign in"""
        # Wait for initial screen to load
        #time.sleep(3)
        
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
            #time.sleep(2)
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
                    #time.sleep(2)
                    try:
                        skip_button = self.driver.find_element(AppiumBy.XPATH, 
                            '//android.widget.Button[contains(@text, "Continue as guest") or contains(@text, "Skip")]')
                        skip_button.click()
                    except:
                        print("Continuing without explicit skip")
        
        # Wait for home page to load after skipping sign-in
        #time.sleep(3)
        print("App successfully opened with English language and sign-in skipped")
        
        # Verify we're on the home page
        try:
            search_hint = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/chrome_search_hint_view')
            print("Successfully verified we're on the home page")
            return True
        except:
            print("Could not verify home page")
            return False
    '''
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
        #time.sleep(3)
        
        # Verify we're on the search results page (optional)
        try:
            results_element = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/rs_results_count')
            print(f"Search results found: {results_element.text}")
        except:
            print("Continued to search results page")
    '''
    
    def test_app_loading_time(self):
        """Measure the time taken to open app, select language, and skip sign in"""
        # Phase 1: App startup time
        start_time = time.time()
        print("Starting app loading measurement...")
        
        #time.sleep(3)  # Wait for initial screen
        phase1_end_time = time.time()
        phase1_duration = phase1_end_time - start_time
        print(f"Phase 1 - App startup time: {phase1_duration:.2f} seconds")
        
        # Phase 2: Language selection and sign-in skipping process
        phase2_start_time = time.time()
        
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
            #time.sleep(2)
            print("Clicked continue after selecting language")
        except:
            print("Could not find continue button after language selection")
        
        # Skip sign in instead of signing in
        try:
            # Look for skip sign-in button
            skip_button = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/skip_sign_in_button')
            skip_button.click()
            print("Skipped sign-in using skip button")
        except:
            try:
                # Try by text if ID doesn't work
                skip_button = self.driver.find_element(AppiumBy.XPATH, '//android.widget.Button[contains(@text, "Skip sign in")]')
                skip_button.click()
                print("Skipped sign-in using text button")
            except:
                try:
                    # Look for "Sign in" button's sibling element that allows skipping
                    skip_link = self.driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "Skip")]')
                    skip_link.click()
                    print("Skipped sign-in using Skip text link")
                except:
                    print("Could not find skip option, trying to continue as guest...")
                    # If we can't find a skip button, we may need to click continue first
                    continue_button = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/sso_continue')
                    continue_button.click()
                    # Then look for skip options on the next screen
                    #time.sleep(2)
                    try:
                        skip_button = self.driver.find_element(AppiumBy.XPATH, 
                            '//android.widget.Button[contains(@text, "Continue as guest") or contains(@text, "Skip")]')
                        skip_button.click()
                        print("Continued as guest after clicking continue")
                    except:
                        print("Continuing without explicit skip")
        
        phase2_end_time = time.time()
        phase2_duration = phase2_end_time - phase2_start_time
        print(f"Phase 2 - Language selection and sign-in skipping process: {phase2_duration:.2f} seconds")
        
        # Phase 3: Home page loading
        phase3_start_time = time.time()
        
        # Wait for home page to load
        #time.sleep(5)
        
        # Verify we're on the home page
        try:
            search_hint = self.driver.find_element(AppiumBy.ID, 'in.amazon.mShop.android.shopping:id/chrome_search_hint_view')
            print("Successfully verified we're on the home page")
            home_page_loaded = True
        except:
            print("Could not verify home page loading")
            home_page_loaded = False
            
        phase3_end_time = time.time()
        phase3_duration = phase3_end_time - phase3_start_time
        print(f"Phase 3 - Home page loading time: {phase3_duration:.2f} seconds")
        
        # Calculate and display total time
        total_duration = phase3_end_time - start_time
        print(f"Total app loading time: {total_duration:.2f} seconds")
        print(f"  - Phase 1 (App startup): {phase1_duration:.2f} seconds ({(phase1_duration/total_duration*100):.1f}%)")
        print(f"  - Phase 2 (Language & sign-in): {phase2_duration:.2f} seconds ({(phase2_duration/total_duration*100):.1f}%)")
        print(f"  - Phase 3 (Home page loading): {phase3_duration:.2f} seconds ({(phase3_duration/total_duration*100):.1f}%)")
        
        return home_page_loaded


if __name__ == '__main__':
    unittest.main()



'''
Results of loading the app:
Total app loading time: 11.55 seconds
  - Phase 1 (App startup): 3.00 seconds (26.0%)
  - Phase 2 (Language & sign-in): 3.46 seconds (30.0%)
  - Phase 3 (Home page loading): 5.08 seconds (44.0%)
  
'''