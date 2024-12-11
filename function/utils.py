import logging
from logging.handlers import RotatingFileHandler
import os
from urllib.parse import urlparse

def setup_logger(name, filename, level=logging.DEBUG):
	# Ensure the logs directory exists
	log_dir = '../logs'
	if not os.path.exists(log_dir):
			os.makedirs(log_dir)

	# Set up the rotating file handler
	log_file = os.path.join(log_dir, filename)
	print(f"{name} log file is at { os.path.abspath(log_file)}")

	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")        
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	logger.addHandler(handler)

	return logger

def verify_tiktok_url(video_url: str) -> tuple[bool, str, list[str]]:
	parsed_url = urlparse(video_url)
	if "tiktok.com" not in parsed_url.hostname:
		return False, "Invalid TikTok URL - provided URL is not from TikTok", None
	paths = parsed_url.path.split("/")
	if len(paths) < 4:
		return False, "Invalid TikTok URL - bad format", None

	return True, None, paths