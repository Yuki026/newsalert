import time
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from scraper import reformat_scraped_data
from config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP

def parse_data(driver):

    table = driver.find_element(By.CLASS_NAME, "calendar__table")
    data = []

    # Scroll down to the end of the page
    while True:
        # Record the current scroll position
        before_scroll = driver.execute_script("return window.pageYOffset;")

        # Scroll down a fixed amount
        driver.execute_script("window.scrollTo(0, window.pageYOffset + 500);")

        # Wait for a short moment to allow content to load
        time.sleep(1)

        # Record the new scroll position
        after_scroll = driver.execute_script("return window.pageYOffset;")

        # If the scroll position hasn't changed, we've reached the end of the page
        if before_scroll == after_scroll:
            break

    # Now that we've scrolled to the end, collect the data
    for row in table.find_elements(By.TAG_NAME, "tr"):
        row_data = []
        for element in row.find_elements(By.TAG_NAME, "td"):
            class_name = element.get_attribute('class')
            if class_name in ALLOWED_ELEMENT_TYPES:
                if element.text:
                    row_data.append(element.text)
                    if class_name == "calendar__cell calendar__event event":
                        row_class_name = row.get_attribute('class')
                        if "calendar__row--grey" in row_class_name:
                            row_data.append("True")
                        else:
                            row_data.append("False")
                elif "calendar__impact" in class_name:
                    impact_elements = element.find_elements(By.TAG_NAME, "span")
                    for impact in impact_elements:
                        impact_class = impact.get_attribute("class")
                        color = ICON_COLOR_MAP[impact_class]
                    if color:
                        row_data.append(color)
                    else:
                        row_data.append("impact")

        if len(row_data):
            data.append(row_data)


    return data

def set_timezone(driver):
    driver.find_element('xpath', '/html/body/div[4]/div/header[1]/div/div[1]/ul[2]/li[5]/a/span').click()
    time.sleep(1)
    
    timezone = driver.find_element('xpath', '//*[@id="time_zone_modal"]')
    select = Select(timezone)
    select.select_by_index(99)
    time.sleep(1)
    
    timezone_format = driver.find_element('xpath', '//*[@id="time_format_modal"]')
    select = Select(timezone_format)
    select.select_by_index(1)
    time.sleep(1)
    
    driver.find_element('xpath', '/html/body/div[4]/div/div[1]/div/div/form/div/div[3]/input[1]').click()
    time.sleep(2)

def get_news():
    driver = Driver(uc=True, incognito=True)
    driver.get("https://www.forexfactory.com/calendar?week=this")

    set_timezone(driver)
    data = parse_data(driver)

    reformat_scraped_data(data)
    
    driver.quit()
