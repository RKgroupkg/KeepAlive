from keepalive import KeepAliveService
import logging
import time


import os

render_url = os.getenv("RENDER_EXTERNAL_URL")
print(f"My Render URL: {render_url}")


# Custom ping function example
def custom_ping_function():
    print("Custom ping executed!")
    # Could do anything - call a database, touch a file, etc.
    return True

# Advanced configuration
service = KeepAliveService(
    ping_interval=5,  # ping every 2 minutes 
    ping_endpoint="health",  # use /health endpoint instead of /alive
    ping_message="Service is healthy!",
    port=8080,
    host="0.0.0.0",
    timezone="America/New_York",
    external_url=render_url,  # explicitly set URL
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

while True:
  # Get statistics about the service
  stats = service.get_stats()
  print(stats)
  time.sleep(1)
