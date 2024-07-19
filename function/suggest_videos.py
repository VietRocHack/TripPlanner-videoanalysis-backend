
from dotenv import load_dotenv
import requests
import os

load_dotenv()

TIKTOK_CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET")

def get_tiktok_access_token():
	url = 'https://open.tiktokapis.com/v2/oauth/token/'

	headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'Cache-Control': 'no-cache'
	}

	data = {
			'client_key': TIKTOK_CLIENT_KEY,
			'client_secret': TIKTOK_CLIENT_SECRET,
			'grant_type': 'client_credentials'
	}

	response = requests.post(url, headers=headers, data=data)

	response_json = response.json()

	if "error" in response_json:
		return False, response_json

	return True, response_json