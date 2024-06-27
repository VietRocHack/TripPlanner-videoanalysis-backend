from flask import Flask, jsonify, request
from openai import OpenAI
from dotenv import load_dotenv
from function import analyze_videos


load_dotenv()

app = Flask(__name__)

client = OpenAI()

model = "gpt-3.5-turbo"

USE_PARALLEL = True

@app.route("/")
def index():
	return "Hello world"

@app.route("/analyze_videos", methods=['POST'])
def generate_itinerary():
	if not request.is_json:
		return jsonify({"error": "Bad request "}), 400

	json_data: dict = request.get_json()
	# getting data for request
	urls = json_data.get("video_urls")
	num_frames_to_sample = json_data.get("num_frames_to_sample", 5)

	# processing request
	result, content = analyze_videos.analyze_from_urls(
		urls,
		num_frames_to_sample,
		use_parallel=USE_PARALLEL # parallel for speedup
	)

	if result:
		return jsonify(content), 200
	else:
		return jsonify({"error": content}), 500
	


if __name__ == "__main__":
	app.run()