from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException
import time
import json
import os
import re


def check_site_connectivity(url, timeout=30):
    """
    Check if the website is available before attempting to load it with Selenium
    
    Args:
        url (str): Website URL to verify
        timeout (int): Maximum wait time in seconds
    
    Returns:
        tuple: (bool, str) - (is_available, message)
    """
    try:
        import requests
        print(f"🌐 Checking connectivity with {url}...")
        
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        if response.status_code == 200:
            print(f"✅ Site available (Status: {response.status_code})")
            return True, f"Site available (Status: {response.status_code})"
        else:
            print(f"❌ Site unavailable (Status: {response.status_code})")
            return False, f"Site unavailable (Status: {response.status_code})"
                
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def extract_row_data(row):
    """
    Extract all visible data from a table row
    """
    row_data = {}
    try:
        cells = row.find_elements(By.CSS_SELECTOR, ".dojoxGridCell")
        
        for i, cell in enumerate(cells):
            try:
                text = cell.text.strip()
                
                if not text:
                    # Look for text in child elements
                    text_elements = cell.find_elements(By.XPATH, ".//*[text()]")
                    if text_elements:
                        text = text_elements[0].text.strip()
                    else:
                        # Look for values in inputs
                        inputs = cell.find_elements(By.CSS_SELECTOR, "input")
                        if inputs:
                            text = inputs[0].get_attribute("value") or ""
                
                if text:
                    row_data[f"column_{i+1}"] = text
                        
            except Exception as e:
                continue
        
        return row_data
        
    except Exception as e:
        print(f"❌ Error extracting row data: {e}")
        return {}


def apply_filters(driver, region, province, commune):
    """
    Apply region, province and commune filters
    
    Args:
        driver: WebDriver instance
        region (str): Region name (e.g., "ABRUZZO")
        province (str): Province name (e.g., "Chieti") 
        commune (str): Commune name (e.g., "LANCIANO")
    
    Returns:
        bool: True if filters were applied successfully
    """
    try:
        print(f"🎯 Applying filters: Region={region}, Province={province}, Commune={commune}")
        
        # Click filter button
        filter_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gwClassListDataGrid_impianti_internet_Toolbar"]/span[2]'))
        )
        filter_button.click()
        print("✅ Filter button clicked successfully")
        
        # Wait for filter popup
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".dojoxFloatingPane"))
        )
        
        # Initial popup setup
        popup_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="widget_sf_value_137603"]'))
        )
        popup_element.click()
        
        choice_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="windowChoice_137603_rowSelector_0"]'))
        )
        choice_element.click()
        
        toolbar_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dijit_Toolbar_3"]/span'))
        )
        toolbar_element.click()

        # REGION FILTER
        print(f"🌍 Applying region filter: {region}")
        region_widget = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="widget_sf_value_137615"]'))
        )
        region_widget.click()
        
        region_field = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="filterColumnTop_ai_regione"]'))
        )
        region_field.clear()
        region_field.send_keys(region)
        time.sleep(3)
        
        # Select first region option
        region_checkbox = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="windowChoice_137615_rowSelector_0"]'))
        )
        region_checkbox.click()
        print(f"✅ Region '{region}' selected")
        
        # Continue to province
        toolbar_4 = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dijit_Toolbar_4"]/span'))
        )
        toolbar_4.click()

        # PROVINCE FILTER
        print(f"🏛️ Applying province filter: {province}")
        province_widget = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="widget_sf_value_137614"]'))
        )
        province_widget.click()
        
        province_field = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="filterColumnTop_nome_pro"]'))
        )
        province_field.clear()
        province_field.send_keys(province)
        time.sleep(3)
        
        # Select first province option
        province_checkbox = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="windowChoice_137614_rowSelector_0"]'))
        )
        province_checkbox.click()
        print(f"✅ Province '{province}' selected")
        
        # Continue to commune
        toolbar_5 = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dijit_Toolbar_5"]/span'))
        )
        toolbar_5.click()

        # COMMUNE FILTER
        print(f"🏘️ Applying commune filter: {commune}")
        commune_widget = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sf_value_137616"]'))
        )
        commune_widget.click()
        
        commune_field = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="filterColumnTop_ai_comune"]'))
        )
        commune_field.clear()
        commune_field.send_keys(commune)
        time.sleep(3)
        
        # Select all available commune options
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id*="windowChoice_137616"] tr'))
        )
        
        commune_rows = driver.find_elements(By.CSS_SELECTOR, '[id*="windowChoice_137616"] tr[class*="dojoxGridRow"]')
        
        selected_count = 0
        for i, row in enumerate(commune_rows):
            if i > 20:  # Limit to prevent overload
                break
            try:
                checkbox = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, f'//*[@id="windowChoice_137616_rowSelector_{i}"]'))
                )
                checkbox.click()
                selected_count += 1
            except:
                continue
        
        print(f"✅ Selected {selected_count} commune options")
        
        # Continue to apply filters
        toolbar_6 = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dijit_Toolbar_6"]/span'))
        )
        toolbar_6.click()
        
        # Apply all filters
        apply_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dijit_Toolbar_2"]/span[3]'))
        )
        apply_button.click()
        print("✅ Filters applied successfully")
        
        # Close filter popup
        close_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gwFP_filter_137591"]/div[1]/span[1]'))
        )
        close_button.click()
        print("✅ Filter popup closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying filters: {e}")
        return False


def extract_popup_data(driver, popup):
    """
    Extract all data from the popup including POINT geometry
    """
    try:
        popup_info = {
            "title": "",
            "table_data": {},
            "geometry_point": "",
            "coordinate_x": None,
            "coordinate_y": None
        }
        
        # Extract title
        try:
            title_element = popup.find_element(By.CSS_SELECTOR, ".dijitTitleNode")
            popup_info["title"] = title_element.text.strip()
        except:
            pass
        
        # Wait for POINT value to load - IMPROVED METHOD
        print("📍 Searching for POINT geometry data...")
        
        def point_is_loaded(driver):
            try:
                inputs = popup.find_elements(By.CSS_SELECTOR, "input")
                for input_elem in inputs:
                    value = input_elem.get_attribute("value") or ""
                    if "POINT(" in value and ")" in value:
                        return input_elem
                return False
            except:
                return False
        
        try:
            point_input = WebDriverWait(driver, 60).until(point_is_loaded)
            value = point_input.get_attribute("value")
            print(f"📍 POINT found: {value[:100]}...")  # Show first 100 chars
            
            # Process POINT value
            point_match = re.search(r'POINT\s*\([^)]+\)', value)
            if point_match:
                point_value = point_match.group()
                popup_info["geometry_point"] = point_value
                print(f"   📍 Geometry: {point_value}")
                
                # Extract coordinates
                coords_match = re.search(r'POINT\s*\(\s*([0-9.-]+)\s+([0-9.-]+)\s*\)', value)
                if coords_match:
                    x, y = coords_match.groups()
                    popup_info["coordinate_x"] = float(x)
                    popup_info["coordinate_y"] = float(y)
                    print(f"   📍 Coordinates: X={x}, Y={y}")
                else:
                    print("   ⚠️ Could not extract coordinates from POINT")
            else:
                print("   ⚠️ Could not parse POINT geometry")
                
        except TimeoutException:
            print("   ⚠️ POINT geometry not found within timeout")
        except Exception as e:
            print(f"   ⚠️ Error extracting POINT: {e}")
        
        # Extract table data from all tabs - IMPROVED METHOD
        table_data = {}
        tab_labels = ["Dati Tecnici", "Ubicazione", "Altri Dati", "Convenzioni"]
        
        print("📋 Extracting data from all tabs...")
        
        for tab_index, label in enumerate(tab_labels):
            try:
                print(f"   🔍 Processing tab: {label}")
                
                # Click on tab
                tab_button = popup.find_element(By.XPATH, f"//span[@class='tabLabel' and text()='{label}']")
                driver.execute_script("arguments[0].click();", tab_button)
                time.sleep(2)  # Wait for tab content to load
                
                # Extract data from this tab using multiple strategies
                tab_data = extract_tab_data(driver, popup, label)
                
                # Merge tab data into main table_data
                for key, value in tab_data.items():
                    # Add tab prefix to avoid key conflicts
                    prefixed_key = f"{label}_{key}" if key not in table_data else f"{label}_{key}"
                    table_data[prefixed_key] = value
                
                print(f"   ✅ Extracted {len(tab_data)} fields from {label}")
                
            except Exception as e:
                print(f"   ⚠️ Error processing tab {label}: {e}")
                continue
        
        popup_info["table_data"] = table_data
        print(f"✅ Total table data extracted: {len(table_data)} fields")
        
        # Close popup - IMPROVED METHOD
        print("🔒 Closing popup...")
        try:
            close_button = popup.find_element(By.CSS_SELECTOR, ".dojoxFloatingCloseIcon")
            driver.execute_script("arguments[0].click();", close_button)
            
            # Wait for popup to close
            WebDriverWait(driver, 30).until(EC.invisibility_of_element(popup))
            print("✅ Popup closed successfully")
            
        except Exception as e:
            print(f"⚠️ Error closing popup with close button: {e}")
            
            # Alternative method: Press Escape key
            try:
                popup.send_keys(Keys.ESCAPE)
                WebDriverWait(driver, 10).until(EC.invisibility_of_element(popup))
                print("✅ Popup closed with Escape key")
            except Exception as e2:
                print(f"⚠️ Error closing popup with Escape: {e2}")
                print("⚠️ Continuing despite popup close error...")
        
        # Final summary
        print(f"📊 POPUP DATA EXTRACTION SUMMARY:")
        print(f"   📋 Title: {popup_info['title']}")
        print(f"   📍 Geometry: {popup_info['geometry_point']}")
        print(f"   📊 Table fields: {len(popup_info['table_data'])}")
        
        return popup_info
        
    except Exception as e:
        print(f"❌ Error extracting popup data: {e}")
        return None


def extract_tab_data(driver, popup, tab_name):
    """
    Extract data from a specific tab within the popup using multiple strategies
    
    Args:
        driver: WebDriver instance
        popup: Popup element
        tab_name (str): Name of the current tab
    
    Returns:
        dict: Extracted data from the tab
    """
    tab_data = {}
    
    try:
        print(f"      🔍 Extracting data from tab: {tab_name}")
        
        # Strategy 1: Try the original fixed XPath
        try:
            table_xpath = '//*[@id="dijit_layout_TabContainer_1"]/div[3]'
            table_element = popup.find_element(By.XPATH, table_xpath)
            
            rows = table_element.find_elements(By.CSS_SELECTOR, "tr")
            strategy1_data = {}
            
            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    if len(cells) >= 2:
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        if key and value:
                            strategy1_data[key] = value
                except:
                    continue
            
            if strategy1_data:
                tab_data.update(strategy1_data)
                print(f"      ✅ Strategy 1 (fixed XPath) extracted {len(strategy1_data)} fields")
            
        except Exception as e:
            print(f"      ⚠️ Strategy 1 failed: {e}")
        
        # Strategy 2: Find all tables within the popup
        try:
            tables = popup.find_elements(By.CSS_SELECTOR, "table")
            strategy2_data = {}
            
            for table_index, table in enumerate(tables):
                rows = table.find_elements(By.CSS_SELECTOR, "tr")
                
                for row in rows:
                    try:
                        cells = row.find_elements(By.CSS_SELECTOR, "td")
                        if len(cells) >= 2:
                            key = cells[0].text.strip()
                            value = cells[1].text.strip()
                            if key and value and len(key) > 1:  # Avoid single character keys
                                # Add table index to avoid conflicts
                                table_key = f"{key}" if table_index == 0 else f"table{table_index}_{key}"
                                strategy2_data[table_key] = value
                    except:
                        continue
            
            if strategy2_data:
                tab_data.update(strategy2_data)
                print(f"      ✅ Strategy 2 (all tables) extracted {len(strategy2_data)} fields")
                
        except Exception as e:
            print(f"      ⚠️ Strategy 2 failed: {e}")
        
        # Strategy 3: Look for input fields and their labels
        try:
            inputs = popup.find_elements(By.CSS_SELECTOR, "input[type='text'], input:not([type]), textarea")
            strategy3_data = {}
            
            for input_elem in inputs:
                try:
                    value = input_elem.get_attribute("value")
                    if value and value.strip():
                        # Try to find associated label
                        input_id = input_elem.get_attribute("id")
                        label_text = ""
                        
                        # Look for label by 'for' attribute
                        if input_id:
                            try:
                                label = popup.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                                label_text = label.text.strip()
                            except:
                                pass
                        
                        # If no label found, try to find nearby text
                        if not label_text:
                            try:
                                parent = input_elem.find_element(By.XPATH, "./..")
                                parent_text = parent.text.strip()
                                if parent_text and len(parent_text) < 100:  # Reasonable label length
                                    label_text = parent_text.replace(value, "").strip()
                            except:
                                pass
                        
                        # Use input id or placeholder as fallback
                        if not label_text:
                            label_text = input_id or input_elem.get_attribute("placeholder") or f"input_field_{len(strategy3_data)}"
                        
                        if label_text:
                            strategy3_data[label_text] = value.strip()
                
                except:
                    continue
            
            if strategy3_data:
                tab_data.update(strategy3_data)
                print(f"      ✅ Strategy 3 (input fields) extracted {len(strategy3_data)} fields")
                
        except Exception as e:
            print(f"      ⚠️ Strategy 3 failed: {e}")
        
        # Strategy 4: Look for div elements with specific patterns (key-value pairs)
        try:
            divs = popup.find_elements(By.CSS_SELECTOR, "div")
            strategy4_data = {}
            
            for div in divs:
                try:
                    div_text = div.text.strip()
                    # Look for patterns like "Label: Value" or "Label Value"
                    if ":" in div_text and len(div_text) < 200:  # Reasonable length
                        parts = div_text.split(":", 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value and len(key) > 1:
                                strategy4_data[key] = value
                except:
                    continue
            
            if strategy4_data:
                tab_data.update(strategy4_data)
                print(f"      ✅ Strategy 4 (div patterns) extracted {len(strategy4_data)} fields")
                
        except Exception as e:
            print(f"      ⚠️ Strategy 4 failed: {e}")
        
        print(f"      📊 Total extracted from {tab_name}: {len(tab_data)} fields")
        return tab_data
        
    except Exception as e:
        print(f"      ❌ Error extracting tab data: {e}")
        return {}


def extract_complete_data(region, province, commune, output_directory):
    """
    Main function that extracts all data from atlaimpianti with specific filters
    
    Args:
        region (str): Region name (e.g., "ABRUZZO")
        province (str): Province name (e.g., "Chieti") 
        commune (str): Commune name (e.g., "LANCIANO")
        output_directory (str): Directory where to save JSON files
    
    Returns:
        tuple: (total_clicks, extracted_data) with number of processed records and data
    """
    
    # Configure Chrome with optimized options
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("detach", True)
    
    service = Service(port=0)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(5)

    print("✅ Google Chrome started successfully")
    
    try:
        print(f"🎯 Starting extraction for: {region} > {province} > {commune}")
        print(f"📁 JSON files will be saved in: {output_directory}")
        
        url = "https://atla.gse.it/atlaimpianti/project/Atlaimpianti_Internet.html"
        
        # Check connectivity
        site_available, message = check_site_connectivity(url)
        if not site_available:
            print(f"❌ {message}")
            print("🔄 Attempting to continue anyway...")
        
        # Load page
        print("🌐 Loading page...")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        WebDriverWait(driver, 45).until(
            EC.any_of(
                EC.presence_of_element_located((By.CLASS_NAME, "dijitDialog")),
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'dijitDialog') or @role='dialog']")),
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
        )
        
        print("✅ Page loaded successfully")
        
        # Handle initial dialog
        try:
            dialog = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "dijitDialog"))
            )
            
            ok_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'dijitButtonContents') and .//span[contains(@class,'dijitButtonText') and contains(normalize-space(text()), 'Ok')]]"))
            )
            ok_button.click()
            
            WebDriverWait(driver, 30).until(EC.invisibility_of_element(dialog))
            print("✅ Initial dialog handled successfully")
        except:
            print("⚠️ No initial dialog found, continuing...")
        
        # Initial navigation
        full_xpath = "/html/body/div[8]/div[2]/div[2]/div/div[2]/div[1]/div/div/div[1]/div[2]/div/div/div/div/div[2]"
        target = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, full_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", target)
        print("✅ Initial navigation completed")
        
        # Apply filters
        filters_successful = apply_filters(driver, region, province, commune)
        
        if not filters_successful:
            print("❌ Error applying filters, terminating execution")
            return 0, []
        
        # Wait for table to update after applying filters
        time.sleep(10)
        scroll_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dojoxGridScrollbox"))
        )
        
        # Extract data from all rows
        total_clicks = 0
        extracted_data = []
        
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        print("🚀 STARTING COMPLETE TABLE TRAVERSAL")
        
        while True:
            try:
                time.sleep(2)
                rows = driver.find_elements(By.CSS_SELECTOR, "div.dojoxGridRow")
            except (NoSuchWindowException, WebDriverException):
                break
            
            if not rows:
                print("❌ No visible rows")
                break
            
            print(f"📋 {len(rows)} rows on screen")
            
            # Process all visible rows
            for i in range(len(rows)):
                try:
                    # Re-get rows to avoid stale element reference
                    updated_rows = driver.find_elements(By.CSS_SELECTOR, "div.dojoxGridRow")
                    if i >= len(updated_rows):
                        break
                    row = updated_rows[i]
                    
                    if not row.is_displayed():
                        continue
                    
                    # Extract row data first
                    row_data = extract_row_data(row)
                    
                    # Check if it's BIOGAS (filter condition)
                    if row_data.get('column_6') != "BIOGAS":
                        continue
                    
                    # Click on row
                    try:
                        row.click()
                    except:
                        try:
                            driver.execute_script("arguments[0].click();", row)
                        except:
                            continue
                    
                    # Wait for popup
                    try:
                        popup = WebDriverWait(driver, 30).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, "dojoxFloatingPane"))
                        )
                    except:
                        continue
                    
                    total_clicks += 1
                    print(f"✅ Click #{total_clicks}")
                    
                    # Extract popup information
                    popup_info = extract_popup_data(driver, popup)
                    
                    # Combine all information
                    if popup_info:
                        complete_record = {
                            "click_number": total_clicks,
                            "row_data": row_data,
                            "popup_data": popup_info,
                            "filters_applied": {
                                "region": region,
                                "province": province,
                                "commune": commune
                            }
                        }
                        
                        extracted_data.append(complete_record)
                        
                        # Save individual JSON file
                        filename = f"record_{total_clicks:04d}.json"
                        filepath = os.path.join(output_directory, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(complete_record, f, ensure_ascii=False, indent=2)
                        
                        print(f"💾 Saved: {filename}")
                    
                except Exception as e:
                    print(f"⚠️ Error processing row {i}: {e}")
                    continue
            
            # Try to scroll down to get more rows
            try:
                driver.execute_script("arguments[0].scrollTop += 500;", scroll_element)
                time.sleep(2)
                
                # Check if we have new rows
                new_rows = driver.find_elements(By.CSS_SELECTOR, "div.dojoxGridRow")
                if len(new_rows) <= len(rows):
                    print("📋 No more rows found, extraction complete")
                    break
                    
            except:
                break
        
        print(f"🎯 EXTRACTION COMPLETED")
        print(f"   📋 Filters: {region} > {province} > {commune}")
        print(f"   ✅ Total records extracted: {total_clicks}")
        print(f"   📁 Files saved in: {output_directory}")
        
        return total_clicks, extracted_data
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return 0, []
        
    finally:
        try:
            driver.quit()
            print("🔒 Browser closed successfully")
        except:
            pass


if __name__ == "__main__":
    # Example usage
    region = "ABRUZZO"
    province = "Chieti"
    commune = "LANCIANO"
    output_dir = "output_data"
    
    total_records, data = extract_complete_data(region, province, commune, output_dir)
    print(f"Extraction finished: {total_records} records extracted")
