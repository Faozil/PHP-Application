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
        self.wait = WebDriverWait(self.driver, 15)
    
    def test_app_health_check(self, app_url):
        """Test that the application responds to HTTP requests"""
        try:
            response = requests.get(app_url, timeout=30)
            assert response.status_code == 200
            assert response.headers.get('content-type', '').startswith('text/html')
        except requests.RequestException as e:
            pytest.fail(f"Health check failed: {e}")
    
    def test_page_loads_successfully(self):
        """Test that the main page loads with expected content"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to fully load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check for title
            title = self.driver.find_element(By.TAG_NAME, "title")
            assert "Simple PHP MySQL App" in title.get_attribute("innerHTML")
            
            # Check that container exists
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
            
        except TimeoutException:
            pytest.fail("Page did not load successfully within timeout")
    
    def test_database_connection_success(self):
        """Test that database connection is successful"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to fully load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Look for success status (should be present when DB connection works)
            success_elements = self.driver.find_elements(By.CLASS_NAME, "success")
            
            # If no success elements, check if we have error elements to understand why
            if len(success_elements) == 0:
                error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
                if len(error_elements) > 0:
                    error_text = " ".join([elem.text for elem in error_elements])
                    pytest.fail(f"Database connection failed: {error_text}")
                else:
                    pytest.fail("No database connection status found")
            
            # Verify success message content
            success_text = " ".join([elem.text for elem in success_elements])
            assert "connection successful" in success_text.lower() or "✓" in success_text, \
                f"Expected success message not found. Got: {success_text}"
            
        except TimeoutException:
            pytest.fail("Database connection test timed out")
    
    def test_table_displays_when_db_connected(self):
        """Test that table displays when database connection is successful"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check if we have a successful database connection
            success_elements = self.driver.find_elements(By.CLASS_NAME, "success")
            
            if len(success_elements) > 0:
                # If DB connection is successful, table should be present
                table = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                assert table.is_displayed(), "Table should be visible when database is connected"
                
                # Check for table headers
                headers = self.driver.find_elements(By.CSS_SELECTOR, "th")
                assert len(headers) > 0, "Table should have headers"
                
            else:
                # If DB connection failed, table might not be present - this is OK
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                if len(tables) == 0:
                    pytest.skip("Database connection failed - table not displayed (expected)")
                
        except TimeoutException:
            # Check if this is due to database connection failure
            error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
            if len(error_elements) > 0:
                pytest.skip("Database connection failed - table test skipped")
            else:
                pytest.fail("Table test failed for unknown reason")
    
    def test_css_styling_loaded(self):
        """Test that CSS styles are properly loaded"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check that styles are applied
            body = self.driver.find_element(By.TAG_NAME, "body")
            font_family = body.value_of_css_property("font-family")
            assert "arial" in font_family.lower() or "sans-serif" in font_family.lower(), \
                "Expected font family not applied"
            
            # Check container max-width
            container = self.driver.find_element(By.CLASS_NAME, "container")
            max_width = container.value_of_css_property("max-width")
            assert max_width == "800px", f"Expected max-width 800px, got {max_width}"
            
        except (TimeoutException, NoSuchElementException) as e:
            pytest.fail(f"CSS styling test failed: {e}")
    
    def test_environment_info_display(self):
        """Test that some environment information is displayed"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for body to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Allow time for PHP info to render
            time.sleep(2)
            
            page_text = self.driver.page_source.lower()
            
            # Look for any environment or system information
            info_indicators = ["php", "version", "server", "time", "environment", "config"]
            has_env_info = any(indicator in page_text for indicator in info_indicators)
            
            assert has_env_info, "No environment information displayed"
            
        except TimeoutException:
            pytest.fail("Environment info test failed due to timeout")
    
    def test_page_load_performance(self):
        """Test page load performance"""
        start_time = time.time()
        self.driver.get(self.app_url)
        
        try:
            # Wait for basic page structure to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
            
            load_time = time.time() - start_time
            # Reasonable timeout for CI environments
            assert load_time < 30, f"Page load time too slow: {load_time:.2f} seconds"
            
        except TimeoutException:
            load_time = time.time() - start_time
            pytest.fail(f"Page failed to load within timeout. Load time: {load_time:.2f} seconds")
    
    def test_responsive_design_basic(self):
        """Test basic responsive design elements"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to load first
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
            
            viewports = [(1920, 1080), (768, 1024), (375, 667)]
            
            for width, height in viewports:
                self.driver.set_window_size(width, height)
                
                # Wait for resize to complete
                time.sleep(1)
                
                # Check that container is still visible and properly sized
                container = self.driver.find_element(By.CLASS_NAME, "container")
                assert container.is_displayed(), f"Container not visible at {width}x{height}"
                
                # Check that body is visible
                body = self.driver.find_element(By.TAG_NAME, "body")
                assert body.is_displayed(), f"Body not visible at {width}x{height}"
                
        except (TimeoutException, NoSuchElementException) as e:
            pytest.fail(f"Responsive design test failed: {e}")
    
    def test_status_message_styling(self):
        """Test that status messages have proper styling"""
        self.driver.get(self.app_url)
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check for status elements
            status_elements = self.driver.find_elements(By.CLASS_NAME, "status")
            if len(status_elements) > 0:
                # Check that status elements have proper padding
                first_status = status_elements[0]
                padding = first_status.value_of_css_property("padding")
                assert "10px" in padding, f"Expected padding 10px, got {padding}"
                
                # Check for success or error styling
                success_elements = self.driver.find_elements(By.CLASS_NAME, "success")
                error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
                
                if len(success_elements) > 0:
                    bg_color = success_elements[0].value_of_css_property("background-color")
                    # Should have greenish background
                    assert "212, 237, 218" in bg_color or "rgb(212, 237, 218)" in bg_color, \
                        f"Success background color not as expected: {bg_color}"
                
                if len(error_elements) > 0:
                    bg_color = error_elements[0].value_of_css_property("background-color")
                    # Should have reddish background
                    assert "248, 215, 218" in bg_color or "rgb(248, 215, 218)" in bg_color, \
                        f"Error background color not as expected: {bg_color}"
            
        except TimeoutException:
            pytest.fail("Status message styling test failed")

if __name__ == "__main__":
    pytest.main(["-v", __file__])