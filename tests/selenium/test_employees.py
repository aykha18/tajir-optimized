import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException


def _nav_to_employees(driver):
    # Click Employees nav button
    employees_btn = None
    for el in driver.find_elements(By.CSS_SELECTOR, "[data-go]"):
        if el.get_attribute("data-go") == "employeeSec":
            employees_btn = el
            break
    assert employees_btn is not None, "Employees nav button not found"
    employees_btn.click()
    time.sleep(0.2)


def _click_with_retry(driver, locator, attempts: int = 3, wait_s: int = 7):
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
    rows = driver.find_elements(By.CSS_SELECTOR, "#employeeTableBody tr")
    for r in rows:
        try:
            if text in r.text:
                return r
        except StaleElementReferenceException:
            continue
    return None


def test_employees_crud(driver, go):
    go("/app")
    _nav_to_employees(driver)

    name_input = driver.find_element(By.ID, "employeeName")
    mobile_input = driver.find_element(By.ID, "employeeMobile")
    address_input = driver.find_element(By.ID, "employeeAddress")

    # Create
    unique_name = f"Selenium Tester {random.randint(1000,9999)}"
    name_input.clear(); name_input.send_keys(unique_name)
    # Use a unique phone to avoid duplicate constraint
    unique_phone = f"05{random.randint(100000000, 999999999)}"
    mobile_input.clear(); mobile_input.send_keys(unique_phone)
    address_input.clear(); address_input.send_keys("Selenium City")
    submit = driver.find_element(By.CSS_SELECTOR, "#employeeForm button[type='submit']")
    submit.click()
    # Wait until the row with the new name appears
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//tbody[@id='employeeTableBody']//tr[contains(., '{unique_name}')]"
        ))
    )
    rows = driver.find_elements(By.CSS_SELECTOR, "#employeeTableBody tr")

    # Ensure loading overlay is gone before clicking
    try:
        WebDriverWait(driver, 7).until(
            lambda d: (lambda el: (el is None) or ("hidden" in el.get_attribute("class") or not el.is_displayed()))(
                next(iter(d.find_elements(By.ID, "employeeLoadingOverlay")), None)
            )
        )
    except Exception:
        pass

    # Edit first match (refetch with XPath and wait to avoid stale elements)
    # Click edit on that specific row with robust retry
    def _attempt_click():
        row = _find_row_by_text(driver, unique_name)
        assert row is not None
        btn = row.find_element(By.CSS_SELECTOR, ".edit-employee-btn")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        driver.execute_script("arguments[0].click();", btn)

    success = False
    for _ in range(4):
        try:
            _attempt_click()
            success = True
            break
        except (StaleElementReferenceException, ElementClickInterceptedException):
            time.sleep(0.5)
    assert success, "Failed to click edit button after retries"

    # Update name
    name_input = driver.find_element(By.ID, "employeeName")
    name_input.send_keys(Keys.END)
    name_input.send_keys(" Updated")
    submit = driver.find_element(By.CSS_SELECTOR, "#employeeForm button[type='submit']")
    submit.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//tbody[@id='employeeTableBody']//tr[contains(., '{unique_name} Updated')]"
        ))
    )
    rows = driver.find_elements(By.CSS_SELECTOR, "#employeeTableBody tr")


