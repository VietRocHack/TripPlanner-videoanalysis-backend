import requests
import cv2
import json
import settings
from openai import OpenAI
import base64

client = OpenAI(api_key=settings.openapi_key)

with open('function/prompt.json', 'r') as prompt_file:
	prompt_json = json.load(prompt_file)
	system_prompt = prompt_json["system_prompt"]
	user_prompt = prompt_json["user_prompt"]

def analyze_image(image):
	# Convert the image to JPG format
	_, image_jpg = cv2.imencode('.jpg', image)

	# Convert the image data to bytes
	base64_image = base64.b64encode(image_jpg.tobytes()).decode('utf-8')

	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {settings.openapi_key}"
	}

	payload = {
		"model": "gpt-4o",
		"messages": [
			{
				"role": "user",
				"content": [
					{
						"type": "text",
						"text": "What's in this image?"
					},
					{
						"type": "image_url",
						"image_url": {
							"url": f"data:image/jpeg;base64,{base64_image}"
						}
					}
				]
			}
		],
		"max_tokens": 300
	}

	# Find API request object here https://platform.openai.com/docs/guides/vision
	response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

	return response.json()["choices"][0]["message"]["content"]
