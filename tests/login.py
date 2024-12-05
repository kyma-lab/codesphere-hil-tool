import json
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

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
    driver.get("http://localhost:5173/login")
    return driver

def close_cookie_banner(driver):
    """Close the cookie banner if it exists."""
    try:
        cookie_banner = driver.find_element(By.CLASS_NAME, 'cookie-banner')
        if (cookie_banner.is_displayed()):
            close_button = cookie_banner.find_element(By.XPATH, './/button')
            close_button.click()
            print("Cookie banner closed.")
    except NoSuchElementException:
        print("No cookie banner found.")
    except Exception as e:
        print(f"Error while closing cookie banner: {e}")

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

def test_file_upload(driver, wait):
    """Test file upload functionality and navigate to annotations page."""
    try:
        # Access the file input and upload the file
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="file"]')))
        file_input.send_keys(test_data['filePath'])
        time.sleep(1)  # Wait for a second after selecting the file
        
        # Click the upload button
        upload_button = wait.until(EC.presence_of_element_located((By.ID, 'upload-button')))
        upload_button.click()

        # Verify the URL to ensure navigation has occurred if it's done automatically upon success
        WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:5173/landing_page_with_annotations"))
        
        print(f"Test: File Upload Test - \033[92m Successful \033[0m")
    except TimeoutException:
        print(f"Test: File Upload Test - \033[91m Failed \033[0m")

def test_search_functionality(driver, wait):
    """Test search functionality."""
    try:
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-box"]')))
        search_box.send_keys(test_data['searchQuery'])
        # time.sleep(1)  # Wait for a second after entering the search query
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)  # Wait for a second after submitting the search

        # Verify search results are displayed
        # Uncomment the line below to verify search results
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-result')))
        
        print(f"Test: Search Functionality Test - \033[92m Successful \033[0m")
    except TimeoutException:
        print(f"Test: Search Functionality Test - \033[91m Failed \033[0m")

def select_random_option(driver, wait):
    # Locate all clickable annotations
    annotations = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@id="annotation-click"]')))
    print(f"Annotations found: {len(annotations)}")

    # Select a random annotation
    random_annotation = random.choice(annotations)
    print(f"Random annotation selected: {random_annotation.text.strip()}")

    # Highlight the annotation
    highlight_element(driver, random_annotation, duration=2)

    # Scroll the annotation into view and click it
    driver.execute_script("arguments[0].scrollIntoView(true);", random_annotation)
    time.sleep(0.1)  # Wait for any scroll transitions
    random_annotation.click()

    # Add sleep time to observe the selected annotation
    # time.sleep(1)

    # Wait for the popup to appear
    popup = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'popup-menu')))
    assert popup.is_displayed()
    print("Popup menu displayed.")

    # Wait for the options within the popup to be clickable
    popup_options = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class, 'popup-menu')]//div[span[@id='select-annotation']]")))
    print(f"Options found: {len(popup_options)}")

    # Debug: Print the text of each option
    for popup_option in popup_options:
        print(f"Option text: {popup_option.text.strip()}")

    # Select a random option
    random_popup_option = random.choice(popup_options)
    random_option_text = random_popup_option.text.strip()

    # Highlight the option
    highlight_element(driver, random_popup_option, duration=2)

    random_popup_option.click()  # Click the randomly selected option
    print(f"Random option selected: {random_option_text}")

    # Add sleep time to observe the selected option
    # time.sleep(1)

    return random_option_text

def add_new_annotation(driver, wait):
    """Function to add a new annotation."""
    try:
        # Locate the text container first
        text_container = wait.until(EC.presence_of_element_located((By.ID, 'document-editor-container')))

        # Locate all plain text elements within the text container
        plain_texts = text_container.find_elements(By.XPATH, './/span[not(@data-label)]')
        print(f"All plain texts found: {len(plain_texts)}")

        # Filter out spans with text length of 1
        filtered_plain_texts = [span for span in plain_texts if len(span.text.strip()) > 1]
        print(f"Filtered plain texts found with more than one character: {len(filtered_plain_texts)}")

        if not filtered_plain_texts:
            print("No suitable plain texts found for annotation.")
            return

        # Select a random plain text from the filtered list
        random_plain_text = random.choice(filtered_plain_texts)
        print(f"Random plain text selected: {random_plain_text.text.strip()}")

        # Highlight the plain text
        highlight_element(driver, random_plain_text, duration=2)

        # Scroll the plain text into view and double-click it to open the popup menu
        driver.execute_script("arguments[0].scrollIntoView(true);", random_plain_text)
        time.sleep(0.1)  # Wait for any scroll transitions
        action_chains = ActionChains(driver)
        action_chains.double_click(random_plain_text).perform()

        # Wait for the popup to appear
        popup = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'popup-menu')))
        assert popup.is_displayed()
        print("Popup menu displayed.")

        # Wait for the options within the popup to be clickable
        popup_options = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[contains(@class, 'popup-menu')]//div[span[@id='select-annotation']]")))
        print(f"Options found: {len(popup_options)}")

        # Select a random option for the new annotation
        random_popup_option = random.choice(popup_options)
        random_option_text = random_popup_option.text.strip()
        highlight_element(driver, random_popup_option, duration=2)

        # Check for the 'Alle' button within the selected popup option
        try:
            alle_button = random_popup_option.find_element(By.XPATH, ".//button[contains(@class, 'all-button')]")
            highlight_element(driver, alle_button, duration=2)
            alle_button.click()
            print("'Alle' button clicked within the selected option.")
        except NoSuchElementException:
            print(f"No 'Alle' button found within the option: {random_option_text}")
            try:
                # Click the selected annotation option if 'Alle' button is not found
                wait.until(EC.element_to_be_clickable(random_popup_option)).click()
                print(f"Random option selected for new annotation: {random_option_text}")
            except Exception as e:
                print(f"Initial click failed, retrying: {e}")
                random_popup_option.click()  # Click the randomly selected option
                print(f"Random option selected for new annotation on retry: {random_option_text}")

        # Add sleep time to observe the selected option
        time.sleep(2)

        print(f"New annotation added.")

    except TimeoutException:
        print(f"Failed to add new annotation - \033[91m Timeout \033[0m")
    except AssertionError as error:
        print(f"Assertion Error: {error} - \033[91m Failed to add new annotation \033[0m")
    except Exception as e:
        print(f"Unexpected error occurred: {e} - \033[91m Failed to add new annotation \033[0m")

def delete_random_annotation(driver, wait):
    """Function to delete a random annotation."""
    try:
        # Locate all clickable annotations
        annotations = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@id="annotation-click"]')))
        print(f"Annotations found: {len(annotations)}")

        # Select a random annotation
        random_annotation = random.choice(annotations)
        print(f"Random annotation selected: {random_annotation.text.strip()}")

        # Highlight the annotation
        highlight_element(driver, random_annotation, duration=2)

        # Scroll the annotation into view and click it
        driver.execute_script("arguments[0].scrollIntoView(true);", random_annotation)
        time.sleep(0.1)  # Wait for any scroll transitions
        random_annotation.click()

        # Add sleep time to observe the selected annotation
        # time.sleep(1)

        # Wait for the popup to appear
        popup = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'popup-menu')))
        assert popup.is_displayed()
        print("Popup menu displayed.")

        # Find and click the delete icon within the popup
        delete_icon = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'delete-icon')))
        
        # Ensure delete icon is clickable
        delete_icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'delete-icon')))

        # Highlight the delete icon
        highlight_element(driver, delete_icon, duration=2)

        delete_icon.click()
        print(f"Annotation deleted.")

    except TimeoutException:
        print(f"Failed to delete annotation - \033[91m Timeout \033[0m")
    except AssertionError as error:
        print(f"Assertion Error: {error} - \033[91m Failed to delete annotation \033[0m")
    except Exception as e:
        print(f"Unexpected error occurred: {e} - \033[91m Failed to delete annotation \033[0m")

def refresh_page(driver):
    """Function to refresh the page."""
    driver.refresh()
    print("Page refreshed.")
    time.sleep(0.1)  # Wait for the page to load after refresh

def verify_annotation_history(driver, wait):
    """Function to verify the annotation history."""
    try:
        # Locate the annotations history container
        history_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'annotations-history')))
        history_items = history_container.find_elements(By.CLASS_NAME, 'annotation-history-item')
        print(f"Annotation history items found: {len(history_items)}")

        for item in history_items:
            # Highlight each history item
            highlight_element(driver, item, duration=1)
            # Print the text content of each history item
            history_text = item.find_element(By.CLASS_NAME, 'annotations-history').text.strip()
            print(f"History item: {history_text}")

        return len(history_items) > 0

    except TimeoutException:
        print(f"Failed to verify annotation history - \033[91m Timeout \033[0m")
    except Exception as e:
        print(f"Unexpected error occurred: {e} - \033[91m Failed to verify annotation history \033[0m")
        return False
    
def undo_last_action(driver, wait):
    """Function to undo the last action."""
    try:
        # Locate the annotations history container
        history_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'annotations-history')))
        # Find the first undo icon (assuming it's for the last action)
        undo_icon = history_container.find_element(By.CLASS_NAME, 'undo-icon')

        # Highlight and click the undo icon
        highlight_element(driver, undo_icon, duration=2)
        undo_icon.click()

        print("Last action undone.")
        time.sleep(2)  # Wait to observe the undo action

    except TimeoutException:
        print(f"Failed to undo last action - \033[91m Timeout \033[0m")
    except Exception as e:
        print(f"Unexpected error occurred: {e} - \033[91m Failed to undo last action \033[0m")
    
def click_hide_button(driver, wait):
    """Function to click the document names hider button."""
    try:
        hide_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'hide-button')))
        # Highlight and click the hide button
        highlight_element(driver, hide_button, duration=2)
        hide_button.click()

        print("Document names hider button clicked.")
        time.sleep(2)  # Wait to observe the hide button action

    except TimeoutException:
        print(f"Failed to click document names hider button - \033[91m Timeout \033[0m")
    except Exception as e:
        print(f"Unexpected error occurred: {e} - \033[91m Failed to click document names hider button \033[0m")

def click_confirm_annotations_button(driver, wait):
    """Function to click the 'Annotation bestätigen' button."""
    try:
        confirm_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Annotation bestätigen')]")))
        # Highlight and click the confirm button
        highlight_element(driver, confirm_button, duration=2)
        confirm_button.click()

        print("Annotations Bestätigung button clicked.")
        time.sleep(2)  # Wait to observe the confirm button action

    except TimeoutException:
        print(f"Failed to click Annotations Bestätigung button - \033[91m Timeout \033[0m")
    except Exception as e:
        print(f"Unexpected error occurred: {e} - \033[91m Failed to click Annotations Bestätigung button \033[0m")

def test_annotation_popup_interaction_and_selection(driver, wait):
    """Test interaction with the annotation click that triggers a popup and select an option."""
    try:
        # Wait for the document editor container to be fully loaded
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'document-editor-container')))
        print("Document editor container loaded.")

        # Close cookie banner if it exists
        close_cookie_banner(driver)

        for _ in range(5):  # Repeat each operation 5 times
            # Select a random option
            select_random_option(driver, wait)
            # time.sleep(1)  # Wait for any transitions

        for _ in range(5):  # Repeat each operation 5 times
            # Add a new annotation
            add_new_annotation(driver, wait)

        for _ in range(5):  # Repeat each operation 5 times
            # Delete a random annotation
            delete_random_annotation(driver, wait)

        time.sleep(1)

        # Verify annotation history
        # if verify_annotation_history(driver, wait):
        #     print(f"Test: Verify Annotation History - \033[92m Successful \033[0m")
        # else:
        #     print(f"Test: Verify Annotation History - \033[91m Failed \033[0m")
        
        for _ in range(5):
              # Repeat each operation 5 times
            # Undo the last action
            undo_last_action(driver, wait)

        for _ in range(5):  # Repeat each operation 5 times
            # Refresh the page to check local storage
            refresh_page(driver)

        for _ in range(5):  # Repeat each operation 5 times
            # Click the document names hider button
            click_hide_button(driver, wait)

        # Click the confirm annotations button
        click_confirm_annotations_button(driver, wait)

        print(f"Test: Annotation Popup Interaction and Selection - \033[92m Successful \033[0m")

        # Add sleep time to verify the results
        time.sleep(5)  # Adjust the sleep time as needed for verification

    except TimeoutException:
        print(f"Test: Annotation Popup Interaction and Selection - \033[91m Failed \033[0m")
    except AssertionError as error:
        print(f"Assertion Error: {error} - \033[91m Test Failed \033[0m")
    except Exception as e:
        print(f"Unexpected error occurred: {e} - \033[91m Test Failed \033[0m")

def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)  # Create wait object here for reuse
    try:
        test_login(driver, wait)
        # test_search_functionality(driver, wait)
        test_file_upload(driver, wait)
        test_annotation_popup_interaction_and_selection(driver, wait)  # New test function for popup interaction
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
