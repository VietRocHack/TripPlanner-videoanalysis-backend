import time
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from function import analyze_videos, suggest_videos
import asyncio


load_dotenv()

app = Flask(__name__)

model = "gpt-3.5-turbo"

@app.route("/")
def index():
	return "Hello world"

@app.route("/analyze_videos", methods=["POST"])
def analyze_videos_http():
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
	
@app.route("/suggest_videos", methods=["GET"])
def suggest_videos_http():
	args_location = request.args.get("location", "")
	num_videos = request.args.get("num_videos", 5)

	if args_location == "":
		return jsonify({"error": "Bad request"}), 400

	result, content = suggest_videos.suggest(args_location, int(num_videos))

	# check if suggest videos succeed
	if result:
		return jsonify({"result": content["result"]}), 200
	else:
		return jsonify(content), 500



if __name__ == "__main__":
	app.run()