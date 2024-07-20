import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from function import utils
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--silent")

logger = utils.setup_logger(__name__, f"../logs/analyze_videos_logger_{int(time.time())}.log")

def suggest(query: str, num_videos: int) -> tuple[bool, dict[str, str]]:
	# Replace all types of whitespace with a single space
	cleaned_query = re.sub(r"\s+", "-", query)
	# Remove all non-alphabetic characters
	cleaned_query = re.sub(r"[^a-zA-Z-]", "", cleaned_query)

	driver = webdriver.Chrome(options=options)
	logger.info(f"Accessing https://www.tiktok.com/discover/{cleaned_query}")
	driver.get(f"https://www.tiktok.com/discover/{cleaned_query}")

	matching_links = []

	try:
		element_present = EC.presence_of_element_located((By.ID, 'bottom'))
		WebDriverWait(driver, 20).until(element_present)

		# Filter <a> tags with href attributes that match the regex pattern
		a_tags = driver.find_elements(By.TAG_NAME, 'a')
		vid_count = 0

		for a_tag in a_tags:
			if vid_count == num_videos:
				break
			href = a_tag.get_attribute('href')
			# Find all links with path /@<user>/video/<video_id>
			if href and re.search(r'/@[^/]+/video/\d+', href):
				matching_links.append(href)
				vid_count += 1

	except Exception as e:
		logger.info(f"An error has happened when fetching links: {e}")
		driver.quit()
		return False, {"error": "An error has happened"}
	finally:
		driver.quit()
		return True, {"result": matching_links}

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
