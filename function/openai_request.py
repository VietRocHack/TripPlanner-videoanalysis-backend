import requests
import cv2
from openai import OpenAI
import base64
from dotenv import load_dotenv
import os
import json

load_dotenv()

def analyze_images(images: list, metadata: dict[str: str] = {}):
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
			"""Analyze this video using simple and to-the-point """ 
			"""vocab and in one paragraph. """
			"""Included is a metadata of the video for better analysis: """
			f"""{json.dumps(metadata)} """
		})
	
	print(content)

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
		"messages": [
			{
				"role": "user",
				"content": content
			}
		],
		"max_tokens": 200
	}

	response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

	return response.json()["choices"][0]["message"]["content"]
