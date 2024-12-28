from openai import OpenAI
import json
import os
import time

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=""
)

prompt = " ".join(open("gemini_prompt_1.txt","r").readlines())


def get_claims(json_file):
    completion = client.chat.completions.create(
        model="google/gemini-2.0-flash-thinking-exp:free",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}\n{json_file}"
                    }
                ]
            }
        ]
    )

    return completion.choices[0].message.content

def extract_claims(input_dir:str, output_dir:str):
    extracted_tables = os.listdir(input_dir)
    extracted_tables.sort()

    for filename in extracted_tables:
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            table_json = json.load(file)

        output_file_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_claims.txt")

        if os.path.exists(output_file_path):
            print(f"Output file already exists: {output_file_path}. Skipping...")
        else:
            print(f"extracting claims from: {file_path}")
            claims = get_claims(table_json)
            time.sleep(10)
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(claims)
