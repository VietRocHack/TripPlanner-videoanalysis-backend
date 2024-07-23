import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

options = Options()

options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://www.tiktok.com/discover/what-to-do-in-rochester')	# Replace with the actual URL

try:
	element_present = EC.presence_of_element_located((By.ID, 'bottom'))
	element = WebDriverWait(driver, 50).until(element_present)
	a_tags = driver.find_elements(By.TAG_NAME, 'a')

	# Filter <a> tags with href attributes that match the regex pattern
	matching_links = []

	for a_tag in a_tags:
		href = a_tag.get_attribute('href')
		if href and re.search(r'/@[^/]+/video/\d+', href):
			matching_links.append(href)
	
	print(matching_links)

finally:
		driver.quit()
