import asyncio
import os
import logging
import httpx
from flask import Flask, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from loguru import logger
from dotenv import load_dotenv
from cache.cache_manager import get_cache, is_cached, cache_response

# Load environment variables
load_dotenv()

# Configuration
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")  # Example: 10 requests per minute

# Initialize Flask app
app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=[RATE_LIMIT])
logger.add("logs/proxy.log", rotation="10MB", level="INFO")

async def fetch_url(method, url, headers, data, cookies):
    async with httpx.AsyncClient(http1=True) as client:
        response = await client.request(method, url, headers=headers, data=data, cookies=cookies, follow_redirects=False)
        return response

@app.route('/proxy', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit(RATE_LIMIT)
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        logger.warning("Missing 'url' parameter in request")
        return Response("Missing 'url' parameter", status=400)
    
    cache_key = f"{request.method}:{target_url}:{request.get_data()}"
    
    # Check if the response is cached
    if request.method == 'GET' and is_cached(cache_key):
        logger.info(f"Cache hit for: {target_url}")
        cached_response = get_cache()[cache_key]
        return Response(cached_response['content'], cached_response['status_code'], cached_response['headers'])
    
    logger.info(f"Proxying request to: {target_url}")
    
    try:
        response = asyncio.run(fetch_url(
            request.method, target_url,
            {k: v for k, v in request.headers if k.lower() != 'host'},
            request.get_data(), request.cookies
        ))
        
        logger.info(f"Received response with status code: {response.status_code}")
        
        if request.method == 'GET' and response.status_code == 200:
            cache_response(cache_key, response.content, response.status_code, dict(response.headers))
            logger.info(f"Response cached for: {target_url}")

            if "transfer-encoding" in response.headers:
                del response.headers["transfer-encoding"]
        
        return Response(response.content, response.status_code, response.headers)
    except Exception as e:
        logger.error(f"Error fetching {target_url}: {str(e)}")
        return Response(f"Error fetching {target_url}: {str(e)}", status=502)

if __name__ == '__main__':
    logger.info("Starting proxy server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
