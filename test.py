from keep-alive-ping import KeepAliveService
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    # Advanced configuration
    service = KeepAliveService(
      ping_interval=60,
      log_level = logging.DEBUG
    
    )

    # Start the service
    service.start()
    print("Main application running...")

    while True:
        try:
            # Get statistics about the service
            stats = service.get_stats()
            print(stats)
            time.sleep(120) # print stats every 2 min 
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(5)  # Avoid rapid crashes

except Exception as e:
    logging.critical(f"Critical error on startup: {e}")