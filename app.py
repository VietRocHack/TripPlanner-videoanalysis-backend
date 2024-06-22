from flask import Flask, jsonify, request

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI()

model = "gpt-3.5-turbo"

@app.route("/")
def index():
    return "Hello world"

@app.route("/analyze_videos", methods=['GET'])
def generate_itinerary():
    user_prompt = request.args.get("prompt")
    
    system_prompt_file = open("./prompts/one_day_prompt_system_json.txt", "r")
    system_prompt = system_prompt_file.read()

    completion = client.chat.completions.create(
        model = model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return completion.choices[0].message.content

if __name__ == "__main__":
    app.run()