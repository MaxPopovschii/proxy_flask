import os
import logging
import json
from typing import Dict, Optional, Any
from flask import Flask, request, Response
import requests
import yaml
from werkzeug.exceptions import BadRequest, InternalServerError

JSON_MIMETYPE = 'application/json'


class ResidorgProxy:
    def __init__(self, config_path: str = 'config.yaml'):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self.load_config(config_path)
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            config = self.default_config()
            config = self.load_yaml_config(config, config_path)
            config = self.override_with_env(config)
            self.logger.info(f"Configuration loaded successfully with {len(config['residorg_mapping'])} mappings")
            return config
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise

    def default_config(self) -> Dict[str, Any]:
        return {
            'residorg_mapping': {
                f'https://residorg{i}.residorg.eu': f'http://atf-service{i}:8000'
                for i in range(1, 11)
            },
            'default_service': 'http://default-atf-service:8000',
            'listen_port': 10000,
            'listen_host': '0.0.0.0',
            'timeout': 10,
            'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE']
        }

    def load_yaml_config(self, config: Dict[str, Any], config_path: str) -> Dict[str, Any]:
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                file_config = yaml.safe_load(file)
                if file_config:
                    self.logger.info(f"Loading configuration from {config_path}")
                    config.update(file_config)
        else:
            self.logger.warning(f"Configuration file {config_path} not found, using defaults")
        return config

    def override_with_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        env_mappings = {}
        for key, value in os.environ.items():
            if key.startswith('RESIDORG_'):
                origin = f"https://{key.replace('RESIDORG_', '')}.residorg.eu"
                env_mappings[origin] = value
                self.logger.info(f"Added mapping from environment: {origin} -> {value}")

        if env_mappings:
            config['residorg_mapping'].update(env_mappings)

        if os.environ.get('DEFAULT_SERVICE'):
            config['default_service'] = os.environ.get('DEFAULT_SERVICE')

        if os.environ.get('LISTEN_PORT'):
            try:
                config['listen_port'] = int(os.environ.get('LISTEN_PORT'))
            except ValueError:
                self.logger.warning("Invalid LISTEN_PORT value, using default")

        if os.environ.get('LISTEN_HOST'):
            config['listen_host'] = os.environ.get('LISTEN_HOST')

        if os.environ.get('REQUEST_TIMEOUT'):
            try:
                config['timeout'] = int(os.environ.get('REQUEST_TIMEOUT'))
            except ValueError:
                self.logger.warning("Invalid REQUEST_TIMEOUT value, using default")

        return config
    
    def get_target_service(self, origin: Optional[str]) -> str:
        if not origin:
            self.logger.info("No origin header found, using default service")
            return self.config['default_service']
        
        # Try to extract domain from origin if it has a scheme
        if '://' in origin:
            try:
                # Handle cases where origin might have path components
                origin_parts = origin.split('/')
                origin = f"{origin_parts[0]}//{origin_parts[2]}"
            except IndexError:
                self.logger.warning(f"Malformed origin header: {origin}")
        
        target = self.config['residorg_mapping'].get(origin, self.config['default_service'])
        self.logger.debug(f"Mapping origin {origin} to target {target}")
        return target
    
    def proxy_request(self, path: str) -> Response:
        try:
            # Verify method is allowed
            if request.method not in self.config.get('allowed_methods', ['GET', 'POST', 'PUT', 'DELETE']):
                self.logger.warning(f"Method {request.method} not allowed")
                raise BadRequest(f"Method {request.method} not allowed")
            
            # Get Origin header (use Referer as fallback)
            origin = (
                request.headers.get('Origin') or 
                request.headers.get('Referer')
            )
            
            # Select target service
            target_service = self.get_target_service(origin)
            
            # Special handling for /version endpoint
            if path == 'version':
                return self.handle_version_request()
            
            # Construct full URL (handling both with/without trailing slash)
            path = path.lstrip('/')
            target_url = f"{target_service}/{path}" if path else target_service
            
            # Prepare headers (remove problematic headers)
            headers = {
                key: value for key, value in request.headers.items()
                if key.lower() not in ['host', 'content-length']
            }
            
            # Add X-Forwarded headers
            headers['X-Forwarded-For'] = request.remote_addr
            headers['X-Forwarded-Proto'] = request.scheme
            headers['X-Forwarded-Host'] = request.host
            
            # Proxy the request
            self.logger.info(f"Proxying {request.method} request to {target_url} (Origin: {origin})")
            
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                timeout=self.config.get('timeout', 10)
            )
            
            # Create Flask response
            proxy_response = Response(
                response.content,
                status=response.status_code
            )
            
            # Forward response headers (excluding certain headers)
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            for name, value in response.headers.items():
                if name.lower() not in excluded_headers:
                    proxy_response.headers[name] = value
            
            # Log response
            self.logger.info(
                f"Proxied response from {target_url}: status={response.status_code}, "
                f"content-type={response.headers.get('content-type', 'unknown')}"
            )
            
            return proxy_response
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return Response(
                json.dumps({
                    "error": "Proxy service error",
                    "message": str(e)
                }),
                status=502,  # Bad Gateway
                mimetype=JSON_MIMETYPE
            )
    
    def handle_version_request(self) -> Response:
        version_response = {
            "platform": "Residorg",
            "version": "3.0.1",
            "uid": None,
            "guidBytes": "Qdvj72ZUssBYJIhNZn20iA=="
        }
        return Response(
            json.dumps(version_response),
            status=200,
            mimetype=JSON_MIMETYPE
        )


def create_app() -> Flask:
    app = Flask(__name__)
    
    # Configure app
    app.config['JSON_SORT_KEYS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Create proxy instance
    proxy = ResidorgProxy()
    app.config['proxy_instance'] = proxy  # Store proxy instance in app config
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return Response(
            json.dumps({"status": "healthy"}),
            status=200,
            mimetype=JSON_MIMETYPE
        )
    
    # Catch-all route for proxying requests
    @app.route('/', defaults={'path': ''}, methods=proxy.config.get('allowed_methods', ['GET', 'POST', 'PUT', 'DELETE']))
    @app.route('/<path:path>', methods=proxy.config.get('allowed_methods', ['GET', 'POST', 'PUT', 'DELETE']))
    def handle_proxy(path):
        return proxy.proxy_request(path)
    
    # Error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler."""
        proxy.logger.error(f"Unhandled exception: {e}", exc_info=True)
        
        if isinstance(e, BadRequest):
            status_code = 400
        elif isinstance(e, InternalServerError):
            status_code = 500
        else:
            status_code = 500  # Added default status code
            
        return Response(
            json.dumps({
                "error": e.__class__.__name__,
                "message": str(e)
            }),
            status=status_code,
            mimetype=JSON_MIMETYPE
        )
    
    return app


# Main entry point
if __name__ == '__main__':
    try:
        app = create_app()
        # Remove this line as proxy instance is already created in create_app()
        # proxy_instance = ResidorgProxy()
        
        # Get the proxy instance from app context
        proxy_instance = app.config['proxy_instance']
        
        # Log startup information
        proxy_instance.logger.info(
            f"Starting ResidorgProxy on {proxy_instance.config['listen_host']}:{proxy_instance.config['listen_port']}"
        )
        
        app.run(
            host=proxy_instance.config['listen_host'], 
            port=proxy_instance.config['listen_port'],
            debug=False
        )
    except Exception as e:
        logging.error(f"Failed to start application: {e}", exc_info=True)
        exit(1)