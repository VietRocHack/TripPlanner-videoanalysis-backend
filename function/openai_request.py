import requests
import cv2
from openai import OpenAI
import base64
from dotenv import load_dotenv
import os
import json
import logging
from function import utils
import time
from aiohttp import ClientSession, ClientError

openai_request_logger = utils.setup_logger(__name__, f"../logs/openai_request_logger_{int(time.time())}.log")

load_dotenv()

with open("./function/openai_analysis_json_template.txt") as f:
	analysis_template = f.read()

async def analyze_images(
		session: ClientSession,
		images: list,
		metadata: dict[str, str] = {}
	) -> dict:
	# Convert the image to JPG format
	# Convert the images to JPG format
	base_64_list = []
	for image in images:
		_, image_jpg = cv2.imencode('.jpg', image)
		base_64_list.append(base64.b64encode(image_jpg.tobytes()).decode('utf-8'))

	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer { os.environ.get('OPENAI_API_KEY') }"
	}

	content = []
	content.append(
		{
			"type": "text",
			"text": """These images are from a TikTok video. """
			"""Analyze this video using simple and to-the-point vocab using this json format: """
			f"""{ analysis_template }"""
			f"""Included is a metadata of the video for better analysis: {json.dumps(metadata)} """
		})
	
	for base64_image in base_64_list:
		content.append(
			{
				"type": "image_url",
				"image_url": {
					"detail": "low", # details low is around 20 tokens, while detail high is around 900 tokens
					"url": f"data:image/jpeg;base64,{base64_image}"
				}
			})

	payload = {
		"model": "gpt-4o",
  	"response_format": {"type": "json_object"},
		"messages": [
			{
				"role": "user",
				"content": content
			}
		],
		"max_tokens": 200
	}

	try:
		async with session.post(
			url="https://api.openai.com/v1/chat/completions",
			json=payload,
			headers=headers
		) as response:
			response_json = await response.json()

			openai_request_logger.info(
				f"Reponse received from OpenAI with code {response.status}: {json.dumps(response_json)}"
			)

			analysis_raw = response_json["choices"][0]["message"]["content"]

			analysis_json = json.loads(analysis_raw)
			return analysis_json

	except ClientError as e:
		openai_request_logger.error(f"ClientError durnig requesting OpenAI: {e}")
		return {}
	
	except Exception as e:
		openai_request_logger.error(f"Some happended during requesting OpenAI: {e}")
		return {}

