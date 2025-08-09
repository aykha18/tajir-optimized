import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


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


def test_employees_crud(driver, go):
    go("/app")
    _nav_to_employees(driver)

    name_input = driver.find_element(By.ID, "employeeName")
    mobile_input = driver.find_element(By.ID, "employeeMobile")
    address_input = driver.find_element(By.ID, "employeeAddress")

    # Create
    name_input.clear(); name_input.send_keys("Selenium Tester")
    mobile_input.clear(); mobile_input.send_keys("0501234123")
    address_input.clear(); address_input.send_keys("Selenium City")
    submit = driver.find_element(By.CSS_SELECTOR, "#employeeForm button[type='submit']")
    submit.click()
    time.sleep(0.8)

    # Verify row appears
    rows = driver.find_elements(By.CSS_SELECTOR, "#employeeTableBody tr")
    assert any("Selenium Tester" in r.text for r in rows)

    # Edit first match
    edit_btn = None
    for r in rows:
        if "Selenium Tester" in r.text:
            edit_btn = r.find_element(By.CSS_SELECTOR, ".edit-employee-btn")
            break
    assert edit_btn is not None
    edit_btn.click()

    # Update name
    name_input = driver.find_element(By.ID, "employeeName")
    name_input.send_keys(Keys.END)
    name_input.send_keys(" Updated")
    submit = driver.find_element(By.CSS_SELECTOR, "#employeeForm button[type='submit']")
    submit.click()
    time.sleep(0.8)

    rows = driver.find_elements(By.CSS_SELECTOR, "#employeeTableBody tr")
    assert any("Selenium Tester Updated" in r.text for r in rows)


