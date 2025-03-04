import pandas as pd
import json
import time
import sys
import requests
from dotenv import load_dotenv
import os
import config

def load_api_key():
    """Load API key from environment or config"""
    load_dotenv()
    return os.getenv("API_KEY") or config.API_KEY

def get_dataset_splits(dataset_id):
    """Fetch dataset splits information from Hugging Face"""
    try:
        url = f"https://datasets-server.huggingface.co/splits?dataset={dataset_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching dataset splits: {e}")
        return None

def rewrite_with_personality(original_output):
    try:
        url = f"{config.API_BASE}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Add any custom headers from config
        for key, value in config.API_HEADERS.items():
            headers[key] = value
        
        payload = {
            "model": config.MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": config.SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Here's the original answer: {original_output}. Now, rewrite the writer above in your quirky style. Do not add descriptor (like, what you do or does) just say your answer"
                }
            ],
            "temperature": config.TEMPERATURE,
            "max_tokens": config.MAX_TOKENS
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    except Exception as e:
        print(f"Error generating reply: {e}")
        return original_output  # Fallback to original

def main():
    global api_key
    # Load API key
    api_key = load_api_key()
    
    if not api_key:
        print("Error: No API key found in environment or config file")
        sys.exit(1)
    
    # Get dataset information
    dataset_id = config.DATASET_ID if hasattr(config, "DATASET_ID") else "yahma/alpaca-cleaned"
    print(f"Fetching dataset information for {dataset_id}...")
    
    splits_info = get_dataset_splits(dataset_id)
    if splits_info:
        print(f"Available splits for {dataset_id}:")
        for split in splits_info.get("splits", []):
            print(f"  - {split}")
    
    # File paths from config
    input_file = config.INPUT_FILE
    output_file = config.OUTPUT_FILE
    
    # Processing parameters from config
    batch_size = config.BATCH_SIZE
    retry_count = config.RETRY_COUNT
    
    # Load original dataset
    try:
        df_original = pd.read_json(input_file)
    except FileNotFoundError:
        print(f"Input file {input_file} not found.")
        print("Would you like to download the dataset from Hugging Face? (y/n)")
        choice = input().lower()
        if choice == 'y':
            try:
                # Simple implementation - in practice you might use the datasets library
                download_url = f"https://huggingface.co/datasets/{dataset_id}/resolve/main/{input_file}"
                print(f"Downloading from {download_url}...")
                response = requests.get(download_url)
                response.raise_for_status()
                with open(input_file, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded to {input_file}")
                df_original = pd.read_json(input_file)
            except Exception as e:
                print(f"Error downloading dataset: {e}")
                sys.exit(1)
        else:
            sys.exit(1)
   
    # Determine starting index
    try:
        with open(output_file, "r") as f:
            existing_lines = f.readlines()
        starting_index = len(existing_lines)
        print(f"Resuming from index {starting_index}")
    except FileNotFoundError:
        starting_index = 0
        
    # Process each batch
    for batch_start in range(starting_index, len(df_original), batch_size):
        batch_end = min(batch_start + batch_size, len(df_original))
        batch = df_original.iloc[batch_start:batch_end]
        enhanced_outputs = []
        
        for i, row in enumerate(batch.itertuples(index=False)):
            original_output = row.output
            print(f"Processing row {batch_start + i}...")
            retry = 0
            
            while retry < retry_count:
                try:
                    enhanced_output = rewrite_with_personality(original_output)
                    enhanced_outputs.append(enhanced_output)
                    break
                except Exception as e:
                    retry += 1
                    print(f"  Retry {retry}/{retry_count} failed. Error: {e}")
                    time.sleep(config.RETRY_DELAY_BASE**retry)  # Exponential backoff
            else:
                # All retries failed, use original
                enhanced_outputs.append(original_output)
                print(f"  Failed to enhance row {batch_start + i}, using original")
                
        # Create a new DataFrame for this batch with enhanced outputs
        enhanced_batch = pd.DataFrame({
            'instruction': batch['instruction'],
            'input': batch['input'],
            'output': enhanced_outputs
        })
        
        # Append to the output file
        with open(output_file, "a") as f:
            for idx, row in enhanced_batch.iterrows():
                json.dump(row.to_dict(), f)
                f.write('\n')
                
        print(f"  Saved rows {batch_start} to {batch_end-1} to {output_file}")

if __name__ == "__main__":
    main()