import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException


def _nav_to_employees(driver):
    """Navigate to employees section."""
    # Click Employees nav button
    employees_btn = None
    for el in driver.find_elements(By.CSS_SELECTOR, "[data-go]"):
        if el.get_attribute("data-go") == "employeeSec":
            employees_btn = el
            break
    assert employees_btn is not None, "Employees nav button not found"
    employees_btn.click()
    time.sleep(0.3)


def _click_with_retry(driver, locator, attempts: int = 3, wait_s: int = 5):
    """Click element with retry logic for stability."""
    last_exc = None
    for _ in range(attempts):
        try:
            el = WebDriverWait(driver, wait_s).until(EC.element_to_be_clickable(locator))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
            return
        except (StaleElementReferenceException, ElementClickInterceptedException) as exc:
            last_exc = exc
            time.sleep(0.5)
    if last_exc:
        raise last_exc


def _find_row_by_text(driver, text: str):
    """Find table row containing specific text."""
    rows = driver.find_elements(By.CSS_SELECTOR, "#employeeTableBody tr")
    for r in rows:
        try:
            if text in r.text:
                return r
        except StaleElementReferenceException:
            continue
    return None


def _wait_for_loading_overlay(driver):
    """Wait for loading overlay to disappear."""
    try:
        WebDriverWait(driver, 5).until(
            lambda d: (lambda el: (el is None) or ("hidden" in el.get_attribute("class") or not el.is_displayed()))(
                next(iter(d.find_elements(By.ID, "employeeLoadingOverlay")), None)
            )
        )
    except Exception:
        pass  # Overlay might not exist or already be hidden


def test_employees_crud(driver, go):
    """Test employee CRUD operations."""
    go("/app")
    _nav_to_employees(driver)

    # Get form elements
    name_input = driver.find_element(By.ID, "employeeName")
    mobile_input = driver.find_element(By.ID, "employeeMobile")
    address_input = driver.find_element(By.ID, "employeeAddress")

    # Create employee
    unique_name = f"Selenium Tester {random.randint(1000,9999)}"
    unique_phone = f"05{random.randint(100000000, 999999999)}"
    
    name_input.clear()
    name_input.send_keys(unique_name)
    mobile_input.clear()
    mobile_input.send_keys(unique_phone)
    address_input.clear()
    address_input.send_keys("Selenium City")
    
    submit = driver.find_element(By.CSS_SELECTOR, "#employeeForm button[type='submit']")
    submit.click()
    
    # Wait for new row to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//tbody[@id='employeeTableBody']//tr[contains(., '{unique_name}')]"
        ))
    )

    # Wait for loading overlay to disappear
    _wait_for_loading_overlay(driver)

    # Edit employee
    def _attempt_edit_click():
        row = _find_row_by_text(driver, unique_name)
        assert row is not None, f"Row with name '{unique_name}' not found"
        btn = row.find_element(By.CSS_SELECTOR, ".edit-employee-btn")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        driver.execute_script("arguments[0].click();", btn)

    # Retry edit click
    success = False
    for _ in range(3):
        try:
            _attempt_edit_click()
            success = True
            break
        except (StaleElementReferenceException, ElementClickInterceptedException):
            time.sleep(0.5)
    assert success, "Failed to click edit button after retries"

    # Update employee name
    name_input = driver.find_element(By.ID, "employeeName")
    name_input.send_keys(Keys.END)
    name_input.send_keys(" Updated")
    
    submit = driver.find_element(By.CSS_SELECTOR, "#employeeForm button[type='submit']")
    submit.click()
    
    # Verify update
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//tbody[@id='employeeTableBody']//tr[contains(., '{unique_name} Updated')]"
        ))
    )

    # Verify final row count
    rows = driver.find_elements(By.CSS_SELECTOR, "#employeeTableBody tr")
    assert len(rows) > 0, "No employee rows found after CRUD operations"


