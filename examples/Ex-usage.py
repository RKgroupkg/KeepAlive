# examples/basic_usage.py
from keep-alive-ping import create_service

# Simplest usage - automatically keeps the app alive with default settings
service = create_service()

# Your actual application code below
print("Main application running...")

# ----------------------------------------------------------------

# examples/advanced_usage.py
from keep-alive-ping import KeepAliveService
import logging

# Custom ping function example
def custom_ping_function():
    print("Custom ping executed!")
    # Could do anything - call a database, touch a file, etc.
    return True

# Advanced configuration
service = KeepAliveService(
    ping_interval=120,  # ping every 2 minutes 
    ping_endpoint="health",  # use /health endpoint instead of /alive
    ping_message="Service is healthy!",
    port=8080,
    host="0.0.0.0",
    timezone="America/New_York",
    external_url="https://my-custom-app.onrender.com",  # explicitly set URL
    custom_pinger=custom_ping_function,  # use custom ping function
    use_flask=True,
    log_level=logging.DEBUG,
    scheduler_options={
        "job_defaults": {
            "coalesce": True,
            "max_instances": 1
        }
    }
)

# Start the service
service.start()

# Your actual application code below
print("Main application running...")

# Get statistics about the service
stats = service.get_stats()
print(stats)

# ----------------------------------------------------------------

# examples/fastapi_integration.py
from fastapi import FastAPI
from keep-alive-ping import create_service

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Configure keepalive service to run without Flask
# since we're using FastAPI
service = create_service(
    use_flask=False,  # don't start Flask server
    custom_pinger=lambda: print("Keeping app alive!")  # custom ping function
)

# Now run FastAPI with uvicorn
# uvicorn examples.fastapi_integration:app