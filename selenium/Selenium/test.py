from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

driver=webdriver.Edge()

driver.get("https://youtube.com")
time.sleep(5)
search=driver.find_element(By.NAME,"q")
search.clear()
search.send_keys("Drake Family matters")
search.send_keys(Keys.RETURN)
time.sleep(30)
#driver.close()