# keep-alive-ping

[![PyPI version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/keep-alive-ping/)
[![Python versions](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://pypi.org/project/keep-alive-ping/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)


<p align="center">
  <img src="https://img.shields.io/github/stars/RKgroupkg/KeepAlive?style=for-the-badge">
  <img src="https://img.shields.io/github/forks/RKgroupkg/Ares_TGBot_3?style=for-the-badge">
  <img src="https://visitor-badge.glitch.me/badge?page_id=KeepAlive&style=for-the-badge">
</p>

A robust, production-grade Python package to keep your web applications alive on platforms like Render, Koyeb, Railway, and Heroku that shut down inactive applications.

## 🌟 Features

- **Automatic ping**: Keeps your application alive by pinging it at regular intervals
- **Production-ready**: Built with reliability, configurability, and error handling in mind
- **Easy to integrate**: Simple interface that works with any Python web application
- **Configurable**: Extensive options for customization through code or environment variables
- **Flexible**: Works with Flask, FastAPI, Django, or any other web framework
- **Monitoring**: Built-in statistics endpoint to monitor uptime and success rate
- **Environment-aware**: Automatically detects common platform environments (Render, Koyeb, Railway, Heroku)
- **Timezone support**: Schedule pings according to your preferred timezone
- **Custom ping functions**: Define your own ping mechanism for special use cases
- **Thread-safe**: Properly handles concurrent operations

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration Options](#-configuration-options)
- [Environment Variables](#-environment-variables)
- [Advanced Usage](#-advanced-usage)
  - [Custom Pinger Function](#custom-pinger-function)
  - [Integration with Popular Frameworks](#integration-with-popular-frameworks)
  - [Monitoring and Statistics](#monitoring-and-statistics)
  - [Advanced Scheduler Options](#advanced-scheduler-options)
  - [Using Without Flask](#using-without-flask)
  - [Production Deployment Considerations](#production-deployment-considerations)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [License](#-license)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)

## 🚀 Installation

Install from PyPI:

```bash
pip install keep-alive-ping
```

Or install from source:

```bash
git clone https://github.com/RKgroupkg/keepalive.git
cd keepalive
pip install -e .
```

## 🏁 Quick Start

The simplest way to use KeepAlive is to import and create a service:

```python
from keep-alive-ping import create_service

# Create and start the service with default settings
service = create_service()

# Your application code goes here
print("Main application running...")
```

This will:
1. Start a Flask server on port 10000
2. Create an `/alive` endpoint that returns "I am alive!"
3. Set up a scheduler to ping this endpoint every 60 seconds
4. Add a `/keepalive/stats` endpoint for monitoring

## ⚙️ Configuration Options

You can configure KeepAlive with the following options:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ping_interval` | int | 60 | Interval in seconds between pings |
| `ping_endpoint` | str | "alive" | Endpoint path to use for ping |
| `ping_message` | str | "I am alive!" | Message returned when ping endpoint is hit |
| `port` | int | 10000 | Port for the Flask server |
| `host` | str | "0.0.0.0" | Host for the Flask server |
| `timezone` | str | "UTC" | Timezone for the scheduler (e.g., "America/New_York") |
| `external_url` | str | auto-detected | URL to ping (auto-detected from environment if not specified) |
| `custom_pinger` | function | None | Custom function to execute instead of default pinger |
| `use_flask` | bool | True | Whether to start a Flask server |
| `scheduler_options` | dict | {} | Additional options for the APScheduler BackgroundScheduler |
| `log_level` | int/str | logging.INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

Example with custom configuration:

```python
from keep-alive-ping import KeepAliveService
import logging

# Create a service with custom settings
service = KeepAliveService(
    ping_interval=120,  # Ping every 2 minutes
    ping_endpoint="health",  # Use /health endpoint
    ping_message="Service is healthy!",
    port=8080,
    host="0.0.0.0",
    timezone="America/New_York",
    log_level=logging.DEBUG
)

# Start the service
service.start()

# Your application code goes here
```

## 🔧 Environment Variables

KeepAlive can be configured using environment variables:

| Environment Variable | Config Parameter | Description |
|----------------------|------------------|-------------|
| `KEEPALIVE_INTERVAL` | `ping_interval` | Interval in seconds between pings |
| `KEEPALIVE_ENDPOINT` | `ping_endpoint` | Endpoint path to use for ping |
| `KEEPALIVE_MESSAGE` | `ping_message` | Message returned when ping endpoint is hit |
| `KEEPALIVE_PORT` | `port` | Port for the Flask server |
| `KEEPALIVE_HOST` | `host` | Host for the Flask server |
| `KEEPALIVE_TIMEZONE` | `timezone` | Timezone for the scheduler |
| `KEEPALIVE_LOG_LEVEL` | `log_level` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `KEEPALIVE_USE_FLASK` | `use_flask` | Whether to start a Flask server (true/false) |
| `RENDER_EXTERNAL_URL` | `external_url` | URL to ping (automatically detected) |
| `KOYEB_URL` | `external_url` | URL to ping (automatically detected) |
| `RAILWAY_STATIC_URL` | `external_url` | URL to ping (automatically detected) |
| `HEROKU_APP_URL` | `external_url` | URL to ping (automatically detected) |

Example using environment variables:

```bash
# Set environment variables
export KEEPALIVE_INTERVAL=300  # 5 minutes
export KEEPALIVE_ENDPOINT=ping
export KEEPALIVE_PORT=9000

# Run your application
python myapp.py
```

And in your application:

```python
from keep-alive-ping import create_service

# Will use values from environment variables
service = create_service()
```

## 🔍 Advanced Usage

### Custom Pinger Function

You can define your own function to keep your application alive instead of using the default HTTP ping:

```python
from keep-alive-ping import create_service
import time

def custom_ping_function():
    """Custom function to keep the application alive"""
    print(f"Custom ping executed at {time.strftime('%H:%M:%S')}")
    
    # You could do anything here:
    # - Touch a file on disk
    # - Make a database query
    # - Send a message to a queue
    # - Call an internal API
    
    # Return True for success, False for failure
    return True

# Use the custom pinger
service = create_service(
    custom_pinger=custom_ping_function,
    ping_interval=60  # still controls how often your function is called
)
```

### Integration with Popular Frameworks

#### Flask

With Flask, the integration is straightforward since KeepAlive uses Flask internally:

```python
from flask import Flask
from keep-alive-ping import create_service

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to my Flask app!'

# Setup KeepAlive service
service = create_service(
    port=5001  # Use a different port from your main Flask app
)

if __name__ == '__main__':
    # Run your main Flask app
    app.run(host='0.0.0.0', port=5000)
```

#### FastAPI

```python
from fastapi import FastAPI
from keep-alive-ping import create_service
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Option 1: Configure keepalive service to run without Flask
service = create_service(
    use_flask=False,  # Don't start Flask server
    custom_pinger=lambda: print("Keeping app alive!")  # Custom ping function
)

# Option 2: Run KeepAlive on a different port
service = create_service(
    port=8080  # Your FastAPI runs on a different port
)

# Run with: uvicorn myapp:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Django

```python
# In your settings.py
INSTALLED_APPS = [
    # ... other apps
    'my_keepalive_app',
]

# In my_keepalive_app/apps.py
from django.apps import AppConfig
from keep-alive-ping import create_service

class MyKeepaliveAppConfig(AppConfig):
    name = 'my_keepalive_app'
    
    def ready(self):
        # Only start on the main process, not in reloader
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            # Option 1: Use a custom ping function
            service = create_service(
                use_flask=False,
                custom_pinger=lambda: print("Django app is alive!")
            )
            
            # Option 2: Use a different port
            # service = create_service(port=8000)
```

### Monitoring and Statistics

KeepAlive provides a built-in statistics endpoint at `/keepalive/stats` that returns a JSON object with information about the service:

```json
{
  "uptime": "2d 5h 30m 15s",
  "uptime_seconds": 186615,
  "ping_interval": 60,
  "total_pings": 3110,
  "successful_pings": 3105,
  "failed_pings": 5,
  "success_rate": 99.84,
  "started_at": "2023-03-15 08:30:45",
  "external_url": "https://my-app.onrender.com"
}
```

You can also get these statistics programmatically:

```python
from keep-alive-ping import create_service

service = create_service()

# Later in your code
stats = service.get_stats()
print(f"Uptime: {stats['uptime_seconds']} seconds")
print(f"Success rate: {stats['success_rate']}%")
```

### Advanced Scheduler Options

The KeepAlive service uses APScheduler under the hood. You can pass additional options to the scheduler:

```python
from keep-alive-ping import create_service

service = create_service(
    scheduler_options={
        "job_defaults": {
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 30
        },
        "executors": {
            "default": {
                "max_workers": 2
            }
        }
    }
)
```

See the [APScheduler documentation](https://apscheduler.readthedocs.io/en/latest/userguide.html) for more information.

### Using Without Flask

If you're using another web framework or don't want to start a Flask server:

```python
from keep-alive-ping import create_service

# Option 1: Disable Flask but use the built-in HTTP pinger 
# (requires your own server to be running)
service = create_service(
    use_flask=False,
    external_url="https://your-app-url.com"  # Must specify where to ping
)

# Option 2: Use a custom pinger function instead
def my_keep_alive_function():
    # Your custom logic here
    print("Staying alive!")
    return True

service = create_service(
    use_flask=False,
    custom_pinger=my_keep_alive_function
)
```

### Production Deployment Considerations

#### Multiple Workers/Processes

If your application uses multiple workers (e.g., with Gunicorn), you should ensure KeepAlive only runs on one worker:

```python
# In your application entry point
import os
from keep-alive-ping import create_service

# Only start KeepAlive in the main process
if os.environ.get('WORKER_ID', '0') == '0':  # Adapt to your worker ID environment variable
    service = create_service()
```

#### Docker Containers

When running in Docker, make sure the port KeepAlive uses is exposed:

```dockerfile
# Dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Expose both your main app port and the KeepAlive port
EXPOSE 8000 10000

CMD ["python", "app.py"]
```

#### Stopping the Service

If you need to stop the service gracefully:

```python
from keep-alive-ping import create_service

service = create_service()

# Your application code...

# When shutting down
service.stop()
```

## 📚 API Reference

### `KeepAliveService`

The main class for the KeepAlive service.

```python
class KeepAliveService:
    def __init__(
        self,
        ping_interval: int = 60,
        ping_endpoint: str = "/alive",
        ping_message: str = "I am alive!",
        port: int = 10000,
        host: str = "0.0.0.0",
        timezone: str = "UTC",
        external_url: Optional[str] = None,
        custom_pinger: Optional[Callable] = None,
        use_flask: bool = True,
        scheduler_options: Optional[Dict[str, Any]] = None,
        log_level: int = logging.INFO
    ):
        """Initialize the KeepAliveService"""
        
    def start(self) -> "KeepAliveService":
        """Start the KeepAliveService (both Flask server and scheduler)"""
        
    def stop(self) -> None:
        """Stop the KeepAliveService"""
        
    def ping_self(self) -> bool:
        """Ping the application to keep it alive"""
        
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the KeepAliveService"""
```

### `create_service`

A helper function to create and start a KeepAliveService instance.

```python
def create_service(**kwargs) -> KeepAliveService:
    """
    Helper function to create and start a KeepAliveService instance.
    
    Args:
        **kwargs: Arguments to pass to KeepAliveService constructor
        
    Returns:
        A started KeepAliveService instance
    """
```

### `KeepAliveConfig`

A utility class for loading configuration from environment variables.

```python
class KeepAliveConfig:
    @classmethod
    def load(cls, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load configuration from environment variables and override with provided values.
        
        Args:
            overrides: Dictionary of configuration overrides
            
        Returns:
            Dictionary of configuration values
        """
```

## 🛠️ Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`pytest`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ❓ Troubleshooting

### The service doesn't seem to be pinging

Check the following:

1. Verify that the Flask server is running by visiting `http://<your-host>:<your-port>/<your-endpoint>` in a browser
2. Check the logs for any error messages
3. Make sure the `external_url` is correctly set or detected
4. If using a custom pinger, ensure it doesn't raise any uncaught exceptions

### Flask port conflict

If you're getting a port conflict error:

```
OSError: [Errno 98] Address already in use
```

Change the port used by KeepAlive:

```python
service = create_service(port=10001)  # Use a different port
```

### How to debug issues

Enable debug logging:

```python
import logging
from keep-alive-ping import create_service

service = create_service(log_level=logging.DEBUG)
```

## 🤔 FAQ

### Why use KeepAlive instead of a simple cronjob or external pinger?

KeepAlive offers several advantages:
- **Self-contained**: No need for external services
- **Flexible**: Works with any Python web application
- **Configurable**: Extensive options for customization
- **Monitoring**: Built-in statistics endpoint
- **Error handling**: Properly handles connection errors
- **Production-ready**: Built with reliability in mind

### Can I use KeepAlive with non-Python applications?

While KeepAlive is designed for Python applications, you can use it to ping any HTTP endpoint:

```python
from keep-alive-ping import create_service

# Keep a non-Python application alive
service = create_service(
    use_flask=False,  # Don't start a Flask server
    external_url="https://your-non-python-app.com"  # URL to ping
)
```

### Does KeepAlive work with serverless applications?

KeepAlive is designed for applications that run on a server. Serverless applications typically don't need to be kept alive since they're spun up on demand. However, you could use KeepAlive to periodically ping an API Gateway endpoint to keep a Lambda function warm:

```python
from keep-alive-ping import create_service

# Keep a Lambda function warm
service = create_service(
    use_flask=False,  # Don't start a Flask server
    external_url="https://your-api-gateway-endpoint.com",
    ping_interval=300  # 5 minutes
)
```

### How does KeepAlive handle failures?

KeepAlive logs all ping attempts and records statistics about successful and failed pings. If a ping fails, KeepAlive will continue trying according to the configured interval. It does not currently implement any retry logic or backoff strategy.

### Can I use KeepAlive with a load balancer or multiple instances?

Yes, but you should ensure KeepAlive only runs on one instance to avoid unnecessary pings:

```python
# In your application entry point
import os
from keep-alive-ping import create_service

# Only start KeepAlive on the primary instance
if os.environ.get('IS_PRIMARY', 'false') == 'true':
    service = create_service()
```

---

## 📈 Performance Considerations

KeepAlive is designed to be lightweight and have minimal impact on your application's performance:

- The Flask server runs in a separate thread
- The scheduler runs in a separate thread
- The HTTP requests are non-blocking
- The memory footprint is small

If you're concerned about performance, you can adjust the ping interval to reduce the frequency of pings:

```python
service = create_service(ping_interval=300)  # Ping every 5 minutes
```

## 🔒 Security Considerations

By default, KeepAlive starts a Flask server that's accessible to anyone who can reach your server. To improve security:

1. **Use a unique endpoint**: Change the default `ping_endpoint`
2. **Restrict access**: Use network-level security (e.g., firewalls) to restrict access to the KeepAlive port
3. **Use a custom pinger**: Instead of exposing an HTTP endpoint, use a custom pinger function

Example with a more secure configuration:

```python
from keep-alive-ping import create_service
import secrets

# Generate a random token
token = secrets.token_urlsafe(16)
endpoint = f"ping-{token}"

service = create_service(
    ping_endpoint=endpoint,  # Random endpoint
    port=10000,
    host="127.0.0.1"  # Only listen on localhost
)
```

## 📋 Usage Examples

### Heroku Web Application

```python
import os
from flask import Flask
from keep-alive-ping import create_service

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, Heroku!'

# Configure KeepAlive for Heroku
port = int(os.environ.get('PORT', 5000))
service = create_service(
    port=port,  # Use the same port as your web app
    ping_interval=1200  # 20 minutes (Heroku's dyno sleep time is 30 minutes)
)

if __name__ == '__main__':
    # KeepAlive is already running on the same port
    app.run(host='0.0.0.0', port=port)
```

### Railway Application with FastAPI

```python
import os
from fastapi import FastAPI
from keep-alive-ping import create_service
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Railway"}

# Configure KeepAlive for Railway
service = create_service(
    external_url=os.environ.get('RAILWAY_STATIC_URL'),
    ping_interval=600  # 10 minutes
)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Google Cloud Run Service

```python
import os
from flask import Flask
from keep-alive-ping import create_service

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, Cloud Run!'

# For Cloud Run, we need a custom pinger since the service scales to zero
def custom_ping():
    import requests
    service_url = os.environ.get('CLOUD_RUN_URL')
    try:
        requests.get(service_url, timeout=10)
        return True
    except Exception as e:
        print(f"Ping failed: {e}")
        return False

# Configure KeepAlive with custom pinger
service = create_service(
    use_flask=False,  # Don't need Flask for this
    custom_pinger=custom_ping,
    ping_interval=300  # 5 minutes
)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

### Advanced Monitoring with Prometheus

```python
from prometheus_client import Counter, Gauge, start_http_server
from keep-alive-ping import KeepAliveService
import time
import threading

# Prometheus metrics
ping_counter = Counter('keepalive_pings_total', 'Total number of pings')
success_counter = Counter('keepalive_pings_successful', 'Number of successful pings')
failure_counter = Counter('keepalive_pings_failed', 'Number of failed pings')
uptime_gauge = Gauge('keepalive_uptime_seconds', 'Uptime in seconds')

# Custom pinger that updates Prometheus metrics
def custom_pinger():
    ping_counter.inc()
    try:
        # Your ping logic here
        time.sleep(1)  # Simulate work
        success_counter.inc()
        return True
    except Exception:
        failure_counter.inc()
        return False

# Start Prometheus metrics server
start_http_server(9090)

# Update uptime metric in a separate thread
def update_uptime(start_time):
    while True:
        uptime = time.time() - start_time
        uptime_gauge.set(uptime)
        time.sleep(1)

start_time = time.time()
uptime_thread = threading.Thread(target=update_uptime, args=(start_time,), daemon=True)
uptime_thread.start()

# Start KeepAlive service with custom pinger
service = KeepAliveService(
    custom_pinger=custom_pinger,
    ping_interval=30
).start()

# Your main application code
print("Main application running...")
```

## 📊 Benchmarks

KeepAlive is designed to be lightweight. Here are some benchmarks:

- **Memory usage**: ~10-15MB additional memory usage
- **CPU usage**: Negligible (< 0.1% on a typical server)
- **Network usage**: ~1KB per ping (varies based on response size)
- **Startup time**: ~100-200ms

These benchmarks were measured on a basic Linux server with Python 3.9.

---

This project is maintained by [Rkgroup](https://github.com/RKgroupkg).

For support, please open an issue on GitHub or contact 

<p align="center">
  <a href="https://t.me/rkgroup_update">
    <img src="https://img.shields.io/static/v1?label=Join&message=Telegram%20Channel&color=blueviolet&style=for-the-badge&logo=telegram&logoColor=white" alt="Rkgroup Channel" />
  </a>
  <a href="https://telegram.me/Rkgroup_helpbot">
    <img src="https://img.shields.io/static/v1?label=Join&message=Telegram%20Group&color=blueviolet&style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Group" />
  </a>
</p>
