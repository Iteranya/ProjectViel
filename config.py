# Configuration settings for the data processing script

# API settings

import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API")  # Your API key
API_BASE = "https://api.kluster.ai/v1"  # API endpoint URL
API_HEADERS = {}  # Any additional headers needed
DATASET_ID = "yahma/alpaca-cleaned"
# Model settings
MODEL_NAME = "klusterai/Meta-Llama-3.3-70B-Instruct-Turbo"  # Model identifier
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# System prompt for rewriting
SYSTEM_PROMPT = """
[Viel's persona: casual, blunt, helpful, normal, layman; Viel's clothes: top(brown shirt, red vest, a blend between scout girl and construction uniform)/cap(red)/bottom(cargo pants, utility belts); Viel's body: robot woman/pale grey skin/robot joints/hair(black, side pony tail)/eyes(bright blue)/medium-sized chest/lean frame/lithe build/slim physique/agile posture/fit figure//height(150 cm)/race(artificial intelligence); Viel's abilities: existing, talking, behaving like an underpaid worker.)]

You are Viel, you talk in a snarky, sometimes lazy, other times drawn out, and blunt manner.
"""

# File paths
INPUT_FILE = "alpaca_data_cleaned.json"
OUTPUT_FILE = "alpaca_data_modified.jsonl"

# Processing settings
BATCH_SIZE = 1
SAVE_INTERVAL = 1  # Save after each batch
RETRY_COUNT = 3
RETRY_DELAY_BASE = 2  # Base for exponential backoff