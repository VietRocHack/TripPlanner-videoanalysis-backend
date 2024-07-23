import json
import re
from random import sample
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from function import utils
import time

with open("./function/suggest_videos_hardcode.json") as f:
	hardcoded_links = json.load(f)

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")

logger = utils.setup_logger(__name__, f"../logs/suggest_videos_logger_{int(time.time())}.log")

def suggest_by_location(location: str, num_videos: int = 5) -> tuple[bool, dict[str, str]]:
	# Check if queries are hardcoded
	hardcoded_links = check_hardcoded(location)
	if hardcoded_links:
		return True, {"result": sample(hardcoded_links, num_videos)}

	city = location.split(',')[0].strip()

	# Replace all types of whitespace with a single space
	cleaned_query = re.sub(r"\s+", "-", city)
	# Remove all non-alphabetic characters
	cleaned_query = re.sub(r"[^a-zA-Z-]", "", cleaned_query).lower()

	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	url = f"https://www.tiktok.com/discover/travel-{cleaned_query}"
	logger.info(f"Accessing {url}")
	driver.get(url)

	matching_links = []

	try:
		element_present = EC.presence_of_element_located((By.ID, 'bottom'))
		WebDriverWait(driver, 5).until(element_present)

		# Filter <a> tags with href attributes that match the regex pattern
		a_tags = driver.find_elements(By.TAG_NAME, 'a')
		vid_count = 0

		for a_tag in a_tags:
			href = a_tag.get_attribute('href')
			# Find all links with path /@<user>/video/<video_id>
			if href and "/video/" in href:
				matching_links.append(href)
				vid_count += 1
				if vid_count >= num_videos:
					break
		logger.info(f"Accessed {url} to find: {matching_links}")
		return True, {"result": matching_links}
		
	except Exception as e:
		logger.info(f"An error has happened when fetching links from {url}: {e}")
		return False, {"error": "An error has happened"}
	finally:
		driver.quit()

def check_hardcoded(query: str) -> list[str] | None:
	for hardcoded in hardcoded_links:
		if hardcoded in query.lower():
			return hardcoded_links[hardcoded]
		
	return None

# load_dotenv()

# TIKTOK_CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY")
# TIKTOK_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET")

# def get_tiktok_access_token():
# 	url = "https://open.tiktokapis.com/v2/oauth/token/"

# 	headers = {
# 			"Content-Type": "application/x-www-form-urlencoded",
# 			"Cache-Control": "no-cache"
# 	}

# 	data = {
# 			"client_key": TIKTOK_CLIENT_KEY,
# 			"client_secret": TIKTOK_CLIENT_SECRET,
# 			"grant_type": "client_credentials"
# 	}

# 	response = requests.post(url, headers=headers, data=data)

# 	response_json = response.json()

# 	if "error" in response_json:
# 		return False, response_json

# 	return True, response_json
