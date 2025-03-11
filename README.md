# KeepAlive

A robust, production-grade Python package to keep your web applications alive on platforms like Render, Koyeb, Railway, and Heroku that shut down inactive applications.

## Features

- **Automatic ping**: Keeps your application alive by pinging it at regular intervals
- **Production-ready**: Built with reliability, configurability, and error handling in mind
- **Easy to integrate**: Simple interface that works with any Python web application
- **Configurable**: Extensive options for customization
- **Flexible**: Works with Flask, FastAPI, Django, or any other web framework
- **Monitoring**: Built-in statistics endpoint to monitor uptime and success rate
- **Environment-aware**: Automatically detects common platform environments

## Installation

```bash
pip install keepalive
```

## Basic Usage

The simplest way to use KeepAlive is to import and create a service:

```python
from keepalive import create_service

# Create and start the service with default settings
service = create_service()

# Your application code goes here
```

This will:
1. Start a Flask server on port 10000
2. Create an `/alive` endpoint that returns "I am alive!"
3. Set up a scheduler to ping this endpoint every 60 seconds
4. Add a `/keepalive/stats` endpoint for monitoring

## Advanced Usage

For more control, you can configure the service with custom settings:

```python
from keepalive import KeepAliveService
import logging

# Create a service with custom settings
service = KeepAliveService(
    ping_interval=120,  # Ping every 2 minutes
    ping_endpoint="health",  # Use /health endpoint
    ping_message="Service is healthy!",
    port=8080,
    timezone="America/New_York",
    log_level=logging.DEBUG
)

# Start the service
service.start()

# Your application code goes here

# Get statistics about the service
stats = service.get_stats()
print(stats)
```

## Integration with Other Frameworks

### FastAPI

```python
from fastapi import FastAPI
from keepalive import create_service

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Configure keepalive service to run without Flask
service = create_service(
    use_flask=False,  # Don't start Flask server
    custom_pinger=lambda: print("Keeping app alive!")  # Custom ping function
)

# Run with: uvicorn myapp:app
```

### Django

```python
# In your settings.py
INSTALLED_APPS = [
    # ... other apps
    'my_keepalive_app',
]

# In my_keepalive_app/apps.py
from django.apps import AppConfig
from keepalive import create_service

class MyKeepaliveAppConfig(AppConfig):
    name = 'my_keepalive_app'
    
    def ready(self):
        # Only start on the main process, not in reloader
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            service = create_service(
                use_flask=False,  # Don't start Flask server
                # Use a custom ping function for Django
                custom_pinger=lambda: print("Django app is alive!")
            )
```

## Configuration Options

You can configure KeepAlive with the following options:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ping_interval` | int | 60 | Interval in seconds between pings |
| `ping_endpoint` | str | "alive" | Endpoint path to use for ping |
| `ping_message` | str | "I am alive!" | Message returned when ping endpoint is hit |
| `port` | int | 10000 | Port for the Flask server |
| `host` | str | "0.0.0.0" | Host for the Flask server |
| `timezone` | str | "UTC" | Timezone for the scheduler |
| `external_url` | str | auto-detected | URL to ping |
| `custom_pinger` | function | None | Custom function to execute instead of default pinger |
| `use_flask` | bool | True | Whether to start a Flask server |
| `scheduler_options` | dict | {} | Additional options for the BackgroundScheduler |
| `log_level` | int | logging.INFO | Logging level |

## Environment Variables

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

## License

MIT
