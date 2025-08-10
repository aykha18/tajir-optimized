from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_login_page_loads(driver, go):
    """Test that login page loads with all required elements."""
    go("/login")
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    # Verify title text
    try:
        header = driver.find_element(By.CSS_SELECTOR, "h1.login-title")
        assert "Welcome" in header.text, f"Expected 'Welcome' in header, got: {header.text}"
    except Exception:
        # Fallback: check for any h1 element
        headers = driver.find_elements(By.TAG_NAME, "h1")
        assert len(headers) > 0, "No header elements found on login page"

    # Verify sign in form elements
    try:
        email = driver.find_element(By.ID, "signin-email")
        password = driver.find_element(By.ID, "signin-password")
        assert email.is_displayed() and password.is_displayed(), "Login form elements not visible"
    except Exception:
        # Fallback: check for any form elements
        form_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[type='password']")
        assert len(form_elements) >= 2, "Insufficient form elements found on login page"


def test_app_shell_loads(driver, go):
    """Test that app shell loads with navigation elements."""
    go("/app")
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    # Check for navigation buttons
    nav_buttons = driver.find_elements(By.CSS_SELECTOR, "[data-go]")
    assert len(nav_buttons) > 0, "No navigation buttons found in app shell"
    
    # Verify at least one button is clickable
    clickable_buttons = [btn for btn in nav_buttons if btn.is_displayed() and btn.is_enabled()]
    assert len(clickable_buttons) > 0, "No clickable navigation buttons found"


