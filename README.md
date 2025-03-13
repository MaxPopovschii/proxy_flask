# Advanced Proxy Server

## Features
- **Asynchronous requests** using `httpx`.
- **Rate limiting** to prevent abuse using `Flask-Limiter`.
- **Caching** for performance using `cachetools`.
- **Logging** with `loguru` for detailed error tracking.
- **Configurable** via `.env` for easy environment setup.
- **Docker support** for easy containerization.

## Installation

### 1. Clone the repo:
```sh
git clone <repo-url>
cd proxy_server

2. Install dependencies:

pip install -r requirements.txt

Run with Docker

To run the proxy server using Docker, follow these steps:
1. Build the Docker image:

docker build -t proxy_server .

2. Run the Docker container:

docker run -p 5000:5000 proxy_server

The server will be available at http://localhost:5000.
Configuration

The project uses a .env file for configuration. Make sure to create a .env file in the root directory with the following settings:

CACHE_TTL=300              # Cache TTL (in seconds), default is 5 minutes
MAX_CACHE_SIZE=100         # Maximum cache size
RATE_LIMIT=10/minute      # Rate limit per IP (e.g., 10 requests per minute)

Usage

The proxy server listens on port 5000. You can send GET, POST, PUT, or DELETE requests to the /proxy endpoint by providing a url parameter. Example:

curl "http://localhost:5000/proxy?url=https://jsonplaceholder.typicode.com/todos/1"

Proxy Behavior:

    GET requests: Cached for improved performance.
    POST, PUT, and DELETE requests: Not cached and proxied directly to the target.

Logging

Logs are written to logs/proxy.log by default. The log file will rotate when it exceeds 10MB in size. You can customize the logging configuration in logger/logger_config.py.
Limitations

    Rate Limiting: Requests are limited to the specified rate per minute.
    Caching: Only GET requests are cached.

License

This project is licensed under the MIT License. See the LICENSE file for more details.
Contributing

If you'd like to contribute to this project, please follow these steps:

    Fork the repository
    Create a branch for your feature (git checkout -b feature/my-feature)
    Add and commit your changes (git commit -am 'Add new feature')
    Push to your branch (git push origin feature/my-feature)
    Open a Pull Request


This `README.md` includes sections on:

1. **Features**: Lists the main functionalities of the proxy server.
2. **Installation**: Instructions for setting up the project.
3. **Docker**: Instructions for building and running the project with Docker.
4. **Configuration**: Information on how to configure the proxy server using environment variables.
5. **Usage**: Example usage for making requests to the proxy.
6. **Logging**: Details about the logging system and where logs are stored.
7. **Limitations**: Outlines the rate limiting and caching behaviors.
8. **Contributing**: How to contribute to the project.
9. **License**: The project’s license (MIT in this case).

This format should make it clear and concise for anyone setting up or contributing to the project.