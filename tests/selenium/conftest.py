import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions


def _build_chrome(headless: bool = True) -> webdriver.Chrome:
    chrome_options = ChromeOptions()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1400,900")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def driver() -> webdriver.Chrome:
    drv = _build_chrome(headless=True)
    yield drv
    drv.quit()


@pytest.fixture
def go(driver, base_url):
    def _go(path: str = "/"):
        url = base_url.rstrip("/") + path
        driver.get(url)
    return _go


