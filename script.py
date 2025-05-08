from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import re
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("output.log", mode='w'),
        logging.StreamHandler()
    ]
)

with open ("config.txt", "r") as file:
    lines = file.readlines()
    chromedriver_path = lines[0].strip()
    login_url = lines[1].strip()
    post_login_url = lines[2].strip()
    scroll_count = int(lines[3].strip())
    comment_limit = int(lines[4].strip())

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)
driver.get(login_url)
driver.maximize_window()

with open("cookies.json", "r") as file:
    cookies = json.load(file)

for cookie in cookies:
    if "sameSite" in cookie:
        if cookie["sameSite"] not in ["Strict", "Lax", "None"]:
            cookie["sameSite"] = "Lax"

    try:
        driver.add_cookie(cookie)
    except Exception as e:
        logging.warning(f"Error adding cookie {cookie.get('name')}: {e}")

driver.refresh()

logging.info("LinkedIn profile loaded with saved cookies.")
time.sleep(10)

driver.get(post_login_url)
time.sleep(5)
logging.info(f"Navigated to {post_login_url}")
time.sleep(5)

def scroll_down(times):
    for _ in range(times):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(5)
    logging.info(f"Scrolled down {times} times.")

def scroll_up(times):
    for _ in range(times):
        driver.execute_script("window.scrollBy(0, -500);")
        time.sleep(5)
    logging.info(f"Scrolled up {times} times.")

scroll_down(scroll_count)
scroll_up(scroll_count)

def function_a(index):
    logging.info(f"Child XPath found in parent [{index}]. Running Function A...")
    try:
        parent_xpath = f"(//div[@class='fie-impression-container'])[{index}]"
        parent_element = driver.find_element("xpath", parent_xpath)

        child_element = parent_element.find_element("xpath", ".//span[@class='update-components-header__text-view']")
        full_text = child_element.text

        match = re.search(r"(.+?)\s(?:and\s\d+\sother\sconnections\s)?(likes|commented|follow|supports|celebrate|love|reposted|job)", full_text)
        if match:
            names = match.group(1)
            names_list = names.replace(" and ", ", ")
            name_tags = [f"@{name.strip()}" for name in names_list.split(",") if not re.search(r"^\d+\sother\sconnection", name.strip())]
            logging.info(f"Text found: {name_tags}")
            # use name_tags here (e.g., to comment or process)
        else:
            logging.warning(f"No name_tags found in text: {full_text}")
            name_tags = []  # fallback empty list or handle as needed

        try:
            comment_btn = driver.find_element(By.XPATH, f"(//span[@class='artdeco-button__text'][normalize-space()='Comment'])[{index}]")
            time.sleep(3)
            comment_btn.click()
            logging.info(f"Comment button clicked in parent [{index}].")
            time.sleep(3)
        except Exception:
            logging.warning(f"Comment button NOT found in parent [{index}].")
            return 

        try:
            text_editor = driver.find_element(By.XPATH, f"(//div[@aria-label='Text editor for creating content'])[{index}]")
            text_editor.click()
            time.sleep(3)
            logging.info(f"Text editor clicked for parent [{index}].")
        except NoSuchElementException:
            logging.error(f"Text editor not found for parent [{index}].")
            return 

        for tag in name_tags:
            text_editor.send_keys(tag)  
            time.sleep(3)  

            try:
                dropdown_item = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "(//span[@class='search-typeahead-v2__hit-info display-flex flex-column'])[1]")
                    )
                )
                dropdown_item.click() 
                time.sleep(3)
                logging.info(f"Dropdown clicked for {tag}")
            except:
                logging.warning(f"Dropdown not found for {tag}.")

            text_editor.send_keys(" ") 

        with open("comments.txt", "r") as comment_file:
            first_line = comment_file.readline().strip()

        text_editor.send_keys(first_line)
        logging.info(f"Typed comment text: {first_line}")
        time.sleep(3)

        text_editor.send_keys(" @kge t")
        time.sleep(3)

        try:
            dropdown_item = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "(//span[@class='search-typeahead-v2__hit-info display-flex flex-column'])[1]")
                )
            )
            dropdown_item.click() 
            time.sleep(3)
            logging.info("Dropdown clicked for @kge t")
        except:
            logging.warning("Dropdown not found for @kge t.")

        try:
            submit_btn = driver.find_element(By.XPATH, f"(//span[@class='artdeco-button__text'][normalize-space()='Comment'])[{index + 1}]")
            submit_btn.click()
            time.sleep(2)
            logging.info("Comment posted successfully!")
        except NoSuchElementException:
            logging.error("Submit button not found. Comment not posted.")

    except NoSuchElementException:
        logging.error(f" Child element missing in parent [{index}].")
    except Exception as e:
        logging.error(f" An error occurred in Function A (parent {index}): {str(e)}")

def function_b(index):
    logging.info(f"Child XPath NOT found in parent [{index}]! Running Function B...")
    try:
        comment_btn = driver.find_element(By.XPATH, f"(//span[@class='artdeco-button__text'][normalize-space()='Comment'])[{index}]")
        comment_btn.click()
        time.sleep(3)
        logging.info(f"Comment button clicked in parent [{index}].")

        text_editor = driver.find_element(By.XPATH, f"(//div[@aria-label='Text editor for creating content'])[{index}]")
        text_editor.click()
        time.sleep(3)
        logging.info(f"Text editor clicked for parent [{index}].")

        with open("comments.txt", "r") as comment_file:
            first_line = comment_file.readline().strip()
        text_editor.send_keys(first_line)
        logging.info(f"Typed comment text: {first_line}")
        time.sleep(3)

        text_editor.send_keys(" @kge t")
        time.sleep(3)

        try:
            dropdown_item = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "(//span[@class='search-typeahead-v2__hit-info display-flex flex-column'])[1]")
                )
            )
            dropdown_item.click()
            time.sleep(3)
            logging.info("Dropdown clicked for @kge t")
        except:
            logging.warning("Dropdown not found for @kge t.")

        try:
            submit_btn = driver.find_element(By.XPATH, f"(//span[@class='artdeco-button__text'][normalize-space()='Comment'])[{index + 1}]")
            submit_btn.click()
            time.sleep(3)
            logging.info("Comment posted successfully!")
        except NoSuchElementException:
            logging.error("Submit button not found. Comment not posted.")

    except NoSuchElementException:
        logging.error(f" Comment button or text editor NOT found in parent [{index + 1}].")
    except Exception as e:
        logging.error(f" An error occurred in Function B (parent {index + 1}): {str(e)}")

def check_child_xpath():
    for i in range(1, comment_limit + 1):  
        try:
            parent_xpath = f"(//div[@class='fie-impression-container'])[{i}]"
            parent_element = driver.find_element("xpath", parent_xpath)

            child_element = parent_element.find_element("xpath", ".//span[@class='update-components-header__text-view']")

            function_a(i)  # If child is found
        except NoSuchElementException:
            function_b(i)  # If child is NOT found

check_child_xpath()

driver.quit()
logging.info("Browser closed. Task completed.")