from openai import OpenAI
import json
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    os.getenv("API_KEY")
    client = OpenAI(
        base_url="https://api.kluster.ai/v1",
        api_key="dd93e43a-c722-4e17-92e5-9007c31002a1",  # Replace with your actual API key
    )

    batch_input_file = client.files.create(
        file=open("viel.jsonl", "rb"),
        purpose="batch"
    )

    batch_request = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="72h",
    )

if __name__ == "__main__":
    main()
