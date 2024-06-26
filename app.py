import time
from flask import Flask, jsonify, request
from openai import OpenAI
from dotenv import load_dotenv
from function import analyze_videos
import asyncio


load_dotenv()

app = Flask(__name__)

client = OpenAI()
model = "gpt-3.5-turbo"

@app.route("/")
def index():
	return "Hello world"

@app.route("/analyze_videos", methods=['POST'])
def generate_itinerary():
	if not request.is_json:
		return jsonify({"error": "Bad request"}), 400

	json_data: dict = request.get_json()
	if "video_urls" not in json_data:
		return jsonify({"error": "Bad request"}), 400
		
	# getting data for request
	urls = json_data.get("video_urls")
	num_frames_to_sample = json_data.get("num_frames_to_sample", 5)

	# processing request
	_, content = asyncio.run(analyze_videos.analyze_from_urls(
		urls,
		num_frames_to_sample,
		metadata_fields=["title"]
	))

	response_packet = {
		"video_analysis": content,
		"metadata": {
			"request": {
				"video_urls": urls,
				"num_frames_to_sample": num_frames_to_sample
			},
			"timestamp": int(time.time())
		}
	}

	return jsonify(response_packet), 200
	


if __name__ == "__main__":
	app.run()