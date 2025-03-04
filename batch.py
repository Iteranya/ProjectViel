import json
import pandas as pd
import os
import sys
import requests
from dotenv import load_dotenv
import config

def load_dataset(input_file, dataset_id):
    """
    Load the dataset from a local JSON file.
    If not found, attempt to download it from Hugging Face.
    """
    try:
        df = pd.read_json(input_file)
        return df
    except FileNotFoundError:
        print(f"Input file {input_file} not found.")
        print("Would you like to download the dataset from Hugging Face? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            try:
                download_url = f"https://huggingface.co/datasets/{dataset_id}/resolve/main/{input_file}"
                print(f"Downloading dataset from {download_url}...")
                response = requests.get(download_url)
                response.raise_for_status()
                with open(input_file, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded dataset to {input_file}")
                df = pd.read_json(input_file)
                return df
            except Exception as e:
                print(f"Error downloading dataset: {e}")
                sys.exit(1)
        else:
            sys.exit(1)

def create_batch_requests(df):
    """
    Create a batch request for each row in the dataset.
    Each request is structured as a JSON object matching the
    documentation format. It uses the dataset row's `output` field
    to build the prompt for rewriting with personality.
    """
    batch_requests = []
    for i, row in enumerate(df.itertuples(index=False)):
        original_output = row.output
        request_obj = {
            "custom_id": f"request-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": config.MODEL_NAME,
                "messages": [
                    {
                        "role": "system",
                        "content": config.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"Here's the original answer: <answer>{original_output}.</answer> \n\nNow, rewrite the answer as Viel. Stay in character and keep the character personality consistent."
                    }
                ],
                "temperature": config.TEMPERATURE,
                "max_completion_tokens": config.MAX_TOKENS
            }
        }
        batch_requests.append(request_obj)
    return batch_requests

def main():
    load_dotenv()  # Load environment variables from .env
    dataset_id = getattr(config, "DATASET_ID", "yahma/alpaca-cleaned")
    input_file = config.INPUT_FILE  # e.g., "alpaca.json"
    output_file = getattr(config, "BATCH_OUTPUT_FILE", "mybatchtest.jsonl")
    
    # Load the dataset (or download it if not present locally)
    df = load_dataset(input_file, dataset_id)
    print(f"Loaded dataset with {len(df)} rows.")
    
    # Create a batch request for each row
    batch_requests = create_batch_requests(df)
    
    # Write the batch requests to a JSONL file
    with open(output_file, "w") as f:
        for req in batch_requests:
            f.write(json.dumps(req) + "\n")
    
    print(f"Batch file '{output_file}' created with {len(batch_requests)} requests.")

if __name__ == "__main__":
    main()
