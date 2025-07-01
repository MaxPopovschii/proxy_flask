# Residorg Proxy

Residorg Proxy is a Flask-based proxy that forwards requests to backend services based on the `Origin` header. 
The proxy supports dynamic request mapping, configuration loading from YAML files and environment variables, and provides health check and versioning endpoints.

## Features
- HTTP request proxying to configured backend services
- Dynamic mapping support via configuration file or environment variables
- Detailed logging of requests and responses
- `/health` endpoint for service status checks
- `/version` endpoint to get service version information
- Advanced error handling

## Requirements
- Python 3.7+
- Flask
- Requests
- PyYAML

## Installation

1. Download the project files.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure the `config.yaml` file if needed.

## Configuration

### `config.yaml` file
The `config.yaml` file allows you to configure service mappings and other settings:
```yaml
residorg_mapping:
  https://residorg1.residorg.eu: http://atf-service1:8000
  https://residorg2.residorg.eu: http://atf-service2:8000

default_service: http://default-atf-service:8000
listen_port: 10000
listen_host: "0.0.0.0"
timeout: 10
allowed_methods: ["GET", "POST", "PUT", "DELETE"]
```

### Environment Variables
The service can also be configured using environment variables:
```sh
export RESIDORG_residorg1=http://custom-service1:8000
export DEFAULT_SERVICE=http://my-default-service:8000
export LISTEN_PORT=8080
```

## Running the Proxy

To start the proxy:
```sh
python app.py
```

## Usage

### Health Check
```sh
curl http://localhost:10000/health
```

### Version
```sh
curl http://localhost:10000/version
```

### Proxy a Request
```sh
curl -H "Origin: https://residorg1.residorg.eu" http://localhost:10000/api/data
```

## Logging
The service uses `logging` to record requests and errors. Logs are printed to the console and can be redirected to a file if needed.

## Common Errors
- **"Proxy request error"**: The backend service may be unreachable, or the mapping is not configured correctly.
- **"Method not allowed"**: The HTTP method is not supported (check `allowed_methods` in the config).
- **"Invalid LISTEN_PORT value"**: The specified port is not valid; use a correct numeric value.

## Contributing
If you want to contribute to the project:
1. Make the necessary changes.
2. Share your feedback or any improvements.

## License
This project is released under the MIT license.

