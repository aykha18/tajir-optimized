from selenium.webdriver.common.by import By


def test_login_page_loads(driver, go):
    go("/login")
    # Title text
    header = driver.find_element(By.CSS_SELECTOR, "h1.login-title")
    assert "Welcome" in header.text

    # Sign in form present
    email = driver.find_element(By.ID, "signin-email")
    password = driver.find_element(By.ID, "signin-password")
    assert email.is_displayed() and password.is_displayed()


def test_app_shell_loads(driver, go):
    # App shell should be reachable, anonymous load shows page shell
    go("/app")
    # Check a known section selector exists in DOM
    nav_buttons = driver.find_elements(By.CSS_SELECTOR, "[data-go]")
    assert len(nav_buttons) > 0


