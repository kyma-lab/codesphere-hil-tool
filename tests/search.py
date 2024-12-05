import json
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Print the current working directory
print(f"Current working directory: {os.getcwd()}")

# Load test data from JSON file
file_path = '/home/paritala/Desktop/Canareno/HIL_prototype/tests/test_data.json'
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file '{file_path}' does not exist. Please check the file path.")

with open(file_path, 'r') as file:
    test_data = json.load(file)
    print(test_data)

def setup_driver():
    """Setup Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    # Uncomment to run Chrome in headless mode.
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get("http://localhost:5173")
    return driver

def highlight_element(driver, element, duration=2):
    """Highlight a Selenium WebDriver element."""
    original_style = element.get_attribute('style')
    highlight_style = (
        "background-color: yellow; "
        "border: 2px solid red; "
        "border-style: dashed; "
        "transition: all 0.3s ease-in-out; "
    )
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, highlight_style)
    time.sleep(duration)
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, original_style)

def test_login(driver, wait):
    """Test login functionality."""
    try:
        username_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
        username_element.send_keys(test_data['login']['username'])
        time.sleep(1)  # Wait for a second after entering username

        password_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
        password_element.send_keys(test_data['login']['password'])
        time.sleep(1)  # Wait for a second after entering password

        driver.find_element(By.XPATH, '//*[@id="login"]').click()
        time.sleep(1)  # Wait for a second after clicking login

        # Verify login success by checking for a specific element that appears after login
        login_success_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="logout"]')))  # Replace with the actual element you expect after login

        if login_success_element.is_displayed():
            print(f"Test: Login Test - \033[92m Successful \033[0m")
        else:
            print(f"Test: Login Test - \033[91m Failed to login \033[0m")
    except TimeoutException:
        print(f"Test: Login Test - \033[91m Failed to login \033[0m")
    except Exception as e:
        print(f"Test: Login Test - \033[91m An error occurred: {e} \033[0m")

def test_search_functionality(driver, wait):
    """Test search functionality."""
    try:
        # Perform the search
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-box"]')))
        search_box.send_keys(test_data['searchQuery'])

        # Locate and click the semantic search toggle
        semantic_search_toggle = wait.until(EC.presence_of_element_located((By.ID, 'flexSwitchCheckDefault')))
        highlight_element(driver, semantic_search_toggle, duration=2)  # Highlight the toggle for visibility
        semantic_search_toggle.click()
        print("Semantic search toggle clicked.")
        time.sleep(1)

        search_box.send_keys(Keys.RETURN)
        time.sleep(1)  # Wait for a second after submitting the search

        # Wait for search results to be displayed
        results_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'results')))
        search_results = results_container.find_elements(By.CSS_SELECTOR, '.results > div')
        print(f"Search results found: {len(search_results)}")

        if not search_results:
            print("No search results found.")
            return

        # Select four random search results
        random_selected_results = random.sample(search_results, min(4, len(search_results)))
        print(f"Selected results: {len(random_selected_results)}")

        # Iterate through the search results and perform actions
        for result in random_selected_results:
            try:
                collapse_button = result.find_element(By.CSS_SELECTOR, 'button[id="collapse-button"]')
                print(f"Collapse button found: {collapse_button}")
                driver.execute_script("arguments[0].scrollIntoView(true);", collapse_button)
                wait.until(EC.element_to_be_clickable(collapse_button))
                highlight_element(driver, collapse_button, duration=1)
                collapse_button.click()  # Expand the collapsible section
                print("Collapse button clicked.")
                time.sleep(1)

                # Wait for the content to be fully expanded and visible
                content = result.find_element(By.CSS_SELECTOR, '.content')
                wait.until(EC.visibility_of(content))

                add_button = content.find_element(By.CSS_SELECTOR, 'button[id="add-result-button"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                wait.until(EC.element_to_be_clickable(add_button))
                highlight_element(driver, add_button, duration=1)
                add_button.click()  # Click the 'Hinzufügen' button
                print("Added search result to the selection.")
                time.sleep(1)

            except NoSuchElementException as e:
                print(f"Element not found: {e}")
                continue

        # Click the upload button after adding the results
        try:
            upload_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.upload-button')))
            highlight_element(driver, upload_button, duration=2)
            upload_button.click()
            print("Upload button clicked.")
            time.sleep(25)  # Wait to observe the action
        except NoSuchElementException as e:
            print(f"Upload button not found: {e}")

        print(f"Test: Search Functionality Test - \033[92m Successful \033[0m")

    except TimeoutException:
        print(f"Test: Search Functionality Test - \033[91m Failed \033[0m")
    except Exception as e:
        print(f"Test: Search Functionality Test - \033[91m An error occurred: {e} \033[0m")

def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)  # Create wait object here for reuse
    try:
        test_login(driver, wait)
        test_search_functionality(driver, wait)
        # test_file_upload(driver, wait)
        # test_annotation_popup_interaction_and_selection(driver, wait)  # New test function for popup interaction
        time.sleep(10)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
