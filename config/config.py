# config.py
import os
from dotenv import load_dotenv

load_dotenv()
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", 100))
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")