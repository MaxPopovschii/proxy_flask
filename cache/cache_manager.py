from cachetools import TTLCache
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))  # Default 5 min
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", 100))

# Initialize cache
cache = TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL)

def get_cache():
    """
    Returns the cache object.
    """
    return cache

def is_cached(cache_key):
    """
    Check if the response for the given cache key is cached.
    """
    return cache_key in cache

def cache_response(cache_key, content, status_code, headers):
    """
    Cache the response content, status code, and headers.
    """
    cache[cache_key] = {
        'content': content,
        'status_code': status_code,
        'headers': headers
    }
