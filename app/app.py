from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")  # Example: 10 requests per minute

# Initialize Flask app
app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=[RATE_LIMIT])

# Return the app and limiter so they can be used elsewhere
def create_app():
    return app, limiter
