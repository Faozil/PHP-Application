import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

@pytest.fixture(scope="session")
def chrome_driver():
    """Setup Chrome driver with headless configuration"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    yield driver
    
    driver.quit()

@pytest.fixture
def app_url():
    """Get application URL from environment or use default"""
    return os.getenv('APP_URL', 'http://localhost:8080')
