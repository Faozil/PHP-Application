import pytest
import requests
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TestPhpApp:
    """Test suite for PHP application"""
    
    @pytest.fixture(autouse=True)
    def setup_test(self, chrome_driver, app_url):
        """Setup for each test"""
        self.driver = chrome_driver
        self.app_url = app_url
        self.wait = WebDriverWait(self.driver, 15)  # Increased timeout
    
    def test_app_health_check(self, app_url):
        """Test that the application responds to HTTP requests"""
        try:
            response = requests.get(app_url, timeout=30)
            assert response.status_code == 200
            assert response.headers.get('content-type', '').startswith('text/html')
        except requests.RequestException as e:
            pytest.fail(f"Health check failed: {e}")
    
    def test_database_connection_success(self):
        """Test that the application successfully connects to database"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to fully load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # More specific wait for success elements
            success_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".status.success"))
            )
            
            assert len(success_elements) > 0, "No success status messages found"
            
            # Check for database connection message
            connection_success = any("Database connection successful" in elem.text 
                                    for elem in success_elements)
            assert connection_success, "Database connection success message not found"
            
        except TimeoutException:
            # Capture page source for debugging
            page_source = self.driver.page_source
            pytest.fail(f"Database connection test failed. Page source: {page_source[:500]}...")
    
    def test_test_table_display(self):
        """Test that test table data is displayed correctly"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for table to be present and visible
            table = self.wait.until(
                EC.visibility_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Check title
            title = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            assert "PHP Application" in title.text
            
            # Verify table headers
            headers = self.driver.find_elements(By.CSS_SELECTOR, "th")
            expected_headers = ["ID", "Name", "Value", "Created At"]
            actual_headers = [header.text.strip() for header in headers]
            
            for expected_header in expected_headers:
                assert expected_header in actual_headers, \
                    f"Header '{expected_header}' not found. Found: {actual_headers}"
                    
        except TimeoutException:
            pytest.fail("Table or required elements not found within timeout")
    
    def test_sample_data_presence(self):
        """Test that sample data is present in the table"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for table body to load
            tbody = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "tbody"))
            )
            
            # Wait for at least one row to be present
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
            )
            
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            assert len(table_rows) >= 1, f"Expected at least 1 data row, found {len(table_rows)}"
            
            # More flexible data checking
            table_text = self.driver.find_element(By.TAG_NAME, "table").text.lower()
            has_data = any(keyword in table_text for keyword in ["sample", "test", "data"])
            assert has_data, f"No recognizable sample data found. Table content: {table_text[:200]}..."
            
        except TimeoutException:
            pytest.fail("Table data not loaded within timeout")
    
    def test_record_count_display(self):
        """Test that total record count is displayed"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to load completely
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            # Allow time for dynamic content to load
            time.sleep(2)
            
            page_text = self.driver.page_source.lower()
            record_indicators = ["total records", "record count", "rows found"]
            
            has_record_count = any(indicator in page_text for indicator in record_indicators)
            assert has_record_count, "Record count information not displayed"
            
        except TimeoutException:
            pytest.fail("Page did not load properly for record count test")
    
    def test_environment_info_display(self):
        """Test that environment information is displayed"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for body to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Allow time for PHP info to render
            time.sleep(2)
            
            page_text = self.driver.page_source.lower()
            
            # More flexible checks
            php_info_present = any(keyword in page_text for keyword in 
                                 ["php version", "server time", "environment"])
            
            assert php_info_present, "Environment information not displayed"
            
        except TimeoutException:
            pytest.fail("Page did not load for environment info test")
    
    def test_page_load_performance(self):
        """Test page load performance"""
        start_time = time.time()
        self.driver.get(self.app_url)
        
        try:
            # Wait for critical elements to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            load_time = time.time() - start_time
            # More reasonable timeout for CI environments
            assert load_time < 30, f"Page load time too slow: {load_time:.2f} seconds"
            
        except TimeoutException:
            load_time = time.time() - start_time
            pytest.fail(f"Page failed to load within timeout. Load time: {load_time:.2f} seconds")
    
    def test_responsive_design(self):
        """Test basic responsive design elements"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to load first
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            viewports = [(1920, 1080), (768, 1024), (375, 667)]
            
            for width, height in viewports:
                self.driver.set_window_size(width, height)
                
                # Wait for resize to complete instead of arbitrary sleep
                WebDriverWait(self.driver, 5).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                # More robust element checking
                try:
                    container = self.driver.find_element(By.CSS_SELECTOR, ".container")
                    assert container.is_displayed(), f"Container not visible at {width}x{height}"
                except NoSuchElementException:
                    # Fallback if no .container class exists
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    assert body.is_displayed(), f"Body not visible at {width}x{height}"
                
                table = self.driver.find_element(By.TAG_NAME, "table")
                assert table.is_displayed(), f"Table not visible at {width}x{height}"
                
        except TimeoutException:
            pytest.fail("Responsive design test failed due to timeout")

if __name__ == "__main__":
    pytest.main(["-v", __file__])