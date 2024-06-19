import os
import settings
from openai import OpenAI

client = OpenAI(api_key=settings.openapi_key)

system_prompt_file = open("./prompts/one_day_prompt_system_json.txt", "r")

system_prompt = system_prompt_file.read()

user_prompt_file = open("./prompts/one_day_prompt_user.txt")

user_prompt = user_prompt_file.read()


completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  response_format={"type": "json_object"},
  messages=[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
  ]
)

print(completion.choices[0].message.content)