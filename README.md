# README.md
# Advanced Proxy Server

## Features
- **Asynchronous requests** using `httpx`.
- **Rate limiting** to prevent abuse.
- **Caching** for performance.
- **Logging** with `loguru`.
- **Configurable** via `.env`.
- **Docker support**.

## Installation
1. Clone the repo:
   ```sh
   git clone <repo-url>
   cd proxy_server
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Run with Docker
```sh
   docker build -t proxy_server .
   docker run -p 5000:5000 proxy_server
```