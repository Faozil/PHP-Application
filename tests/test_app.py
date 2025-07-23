import pytest
import requests
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestPhpMysqlApp:
    """Test suite for PHP application"""
    
    def test_app_health_check(self, app_url):
        """Test that the application responds to HTTP requests"""
        response = requests.get(app_url, timeout=30)
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('text/html')
    
    def test_database_connection_success(self, chrome_driver, app_url):
        """Test that the application successfully connects to database"""
        chrome_driver.get(app_url)
        
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        
        success_elements = chrome_driver.find_elements(By.CSS_SELECTOR, ".status.success")
        assert len(success_elements) > 0, "No success status messages found"
        
        
        connection_success = any("Database connection successful" in elem.text 
                                for elem in success_elements)
        assert connection_success, "Database connection success message not found"
    
    def test_test_table_display(self, chrome_driver, app_url):
        """Test that test table data is displayed correctly"""
        chrome_driver.get(app_url)
        
        
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        
        title = chrome_driver.find_element(By.TAG_NAME, "h1")
        assert "PHP Application" in title.text
        
        
        table = chrome_driver.find_element(By.TAG_NAME, "table")
        assert table is not None, "Test table not found"
        
        
        headers = chrome_driver.find_elements(By.CSS_SELECTOR, "th")
        expected_headers = ["ID", "Name", "Value", "Created At"]
        actual_headers = [header.text for header in headers]
        
        for expected_header in expected_headers:
            assert expected_header in actual_headers, f"Header '{expected_header}' not found"
    
    def test_sample_data_presence(self, chrome_driver, app_url):
        """Test that sample data is present in the table"""
        chrome_driver.get(app_url)
        
        
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        
        table_rows = chrome_driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        assert len(table_rows) >= 3, f"Expected at least 3 data rows, found {len(table_rows)}"
        
        
        table_text = chrome_driver.find_element(By.TAG_NAME, "table").text
        assert "Sample Item" in table_text, "Sample data not found in table"
        assert "test value" in table_text, "Test values not found in table"
    
    def test_record_count_display(self, chrome_driver, app_url):
        """Test that total record count is displayed"""
        chrome_driver.get(app_url)
        
        
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        
        page_text = chrome_driver.page_source
        assert "Total records:" in page_text, "Total records count not displayed"
    
    def test_environment_info_display(self, chrome_driver, app_url):
        """Test that environment information is displayed"""
        chrome_driver.get(app_url)
        
        
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        
        page_text = chrome_driver.page_source
        assert "PHP Version:" in page_text, "PHP version not displayed"
        assert "Server Time:" in page_text, "Server time not displayed"
    
    def test_page_load_performance(self, chrome_driver, app_url):
        """Test page load performance"""
        start_time = time.time()
        chrome_driver.get(app_url)
        
        
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        load_time = time.time() - start_time
        assert load_time < 10, f"Page load time too slow: {load_time:.2f} seconds"
    
    def test_responsive_design(self, chrome_driver, app_url):
        """Test basic responsive design elements"""
        chrome_driver.get(app_url)
        
        
        viewports = [(1920, 1080), (768, 1024), (375, 667)]
        
        for width, height in viewports:
            chrome_driver.set_window_size(width, height)
            time.sleep(1)  
            
            
            container = chrome_driver.find_element(By.CSS_SELECTOR, ".container")
            assert container.is_displayed(), f"Container not visible at {width}x{height}"
            
            table = chrome_driver.find_element(By.TAG_NAME, "table")
            assert table.is_displayed(), f"Table not visible at {width}x{height}"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
