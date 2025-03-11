import os
import time
import threading
import socket
import requests
from typing import Optional, Dict, Any, Callable
import logging
import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("keepalive")

class KeepAliveService:
    """
    A service to keep applications alive on platforms like Render and Koyeb
    that shut down inactive applications.
    """
    
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
        # Set up logging
        logger.setLevel(log_level)
        
        # Configuration
        self.ping_interval = ping_interval
        self.ping_endpoint = ping_endpoint.strip("/")
        self.ping_message = ping_message
        self.port = port
        self.host = host
        self.timezone = timezone
        self.external_url = external_url or self._detect_external_url()
        self.custom_pinger = custom_pinger
        self.use_flask = use_flask
        self.scheduler_options = scheduler_options or {}
        
        # Initialize components
        self.app = None
        self.scheduler = None
        self.flask_thread = None
        self._stats = {"total_pings": 0, "successful_pings": 0, "failed_pings": 0}
        self._start_time = time.time()
        self._running = False
        
        logger.info(f"KeepAliveService initialized with interval {ping_interval}s and endpoint /{self.ping_endpoint}")
    
    def _detect_external_url(self) -> str:
        """Auto-detect the external URL from environment variables or local network"""
        # Check common environment variables used by hosting platforms
        for env_var in ["RENDER_EXTERNAL_URL", "KOYEB_URL", "RAILWAY_STATIC_URL", "HEROKU_APP_URL"]:
            if env_var in os.environ:
                logger.info(f"Using {env_var} for external URL: {os.environ[env_var]}")
                return os.environ[env_var]
        
        # If no environment variable, try to determine local URL
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return f"http://{local_ip}:{self.port}"
        except Exception as e:
            logger.warning(f"Could not determine local IP: {e}")
            return f"http://{self.host}:{self.port}"
    
    def ping_self(self) -> bool:
        """
        Ping the application to keep it alive.
        Returns: Whether the ping was successful
        """
        if self.custom_pinger:
            try:
                self.custom_pinger()
                self._stats["total_pings"] += 1
                self._stats["successful_pings"] += 1
                logger.info("Custom ping successful")
                return True
            except Exception as e:
                logger.error(f"Custom pinger failed: {e}")
                self._stats["total_pings"] += 1
                self._stats["failed_pings"] += 1
                return False
        
        url = f"{self.external_url}/{self.ping_endpoint}"
        try:
            start_time = time.time()
            # Important: Set a reasonable timeout and handle exceptions
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start_time
            
            self._stats["total_pings"] += 1
            
            if response.status_code == 200:
                logger.info(f"Ping successful in {elapsed:.2f}s: {url}")
                self._stats["successful_pings"] += 1
                return True
            else:
                logger.error(f"Ping failed with status code {response.status_code}: {url}")
                self._stats["failed_pings"] += 1
                return False
        except requests.RequestException as e:
            # Handle specific request exceptions
            logger.error(f"Ping failed with request exception: {e} - URL: {url}")
            self._stats["total_pings"] += 1
            self._stats["failed_pings"] += 1
            return False
        except Exception as e:
            # Handle any other exceptions
            logger.error(f"Ping failed with unexpected exception: {e} - URL: {url}")
            self._stats["total_pings"] += 1
            self._stats["failed_pings"] += 1
            return False
    
    def start_scheduler(self) -> None:
        """Start the background scheduler to ping periodically"""
        tz = pytz.timezone(self.timezone)
        
        scheduler_opts = {
            "timezone": tz,
            **self.scheduler_options
        }
        
        # Make sure we only have one scheduler
        if self.scheduler and self.scheduler.running:
            logger.info("Scheduler already running, shutting down first")
            self.scheduler.shutdown()
        
        self.scheduler = BackgroundScheduler(**scheduler_opts)
        
        # Add the ping job with misfire handling
        self.scheduler.add_job(
            self.ping_self,
            IntervalTrigger(
                seconds=self.ping_interval, 
                timezone=tz
            ),
            id="ping_job",
            name="Keep-alive ping",
            replace_existing=True,
            # Critical: Handle misfires to ensure reliability
            misfire_grace_time=15,
            coalesce=True,
            max_instances=1
        )
        
        # Start the scheduler with safe error handling
        try:
            self.scheduler.start()
            logger.info(f"Scheduler started with {self.ping_interval}s interval")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def setup_flask(self) -> None:
        """Set up the Flask application with the ping endpoint"""
        if not self.use_flask:
            return
            
        self.app = Flask(__name__)
        
        # Register the ping endpoint
        @self.app.route(f"/{self.ping_endpoint}", methods=["GET"])
        def alive():
            logger.debug("Received ping request")
            return self.ping_message
        
        # Add a stats endpoint
        @self.app.route("/keepalive/stats", methods=["GET"])
        def stats():
            uptime = time.time() - self._start_time
            days, remainder = divmod(uptime, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            stats_data = {
                "uptime": f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s",
                "uptime_seconds": uptime,
                "ping_interval": self.ping_interval,
                "total_pings": self._stats["total_pings"],
                "successful_pings": self._stats["successful_pings"],
                "failed_pings": self._stats["failed_pings"],
                "success_rate": (self._stats["successful_pings"] / max(1, self._stats["total_pings"])) * 100,
                "started_at": datetime.fromtimestamp(self._start_time).strftime("%Y-%m-%d %H:%M:%S"),
                "external_url": self.external_url,
            }
            
            return stats_data
        
        logger.info(f"Flask application set up with ping endpoint /{self.ping_endpoint} and /keepalive/stats")
    
    def run_flask(self) -> None:
        """Run the Flask application in a separate thread"""
        if not self.use_flask or not self.app:
            return
            
        try:
            # Critical fix: Use threaded=True for better reliability
            self.app.run(host=self.host, port=self.port, threaded=True)
        except Exception as e:
            logger.error(f"Failed to start Flask server: {e}")
            # Don't suppress the exception - we want to know if Flask fails to start
            raise
    
    def start(self) -> "KeepAliveService":
        """Start the KeepAliveService (both Flask server and scheduler)"""
        if self._running:
            logger.warning("KeepAliveService is already running")
            return self
        
        # Set up and start Flask server first
        if self.use_flask:
            self.setup_flask()
            
            # Create and start the Flask thread
            self.flask_thread = threading.Thread(target=self.run_flask, name="KeepAlive-Flask")
            self.flask_thread.daemon = True  # Make it a daemon so it doesn't block program exit
            
            try:
                self.flask_thread.start()
                # Critical: Give Flask time to start up before proceeding
                time.sleep(1)  
                logger.info(f"Flask server started on {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Failed to start Flask thread: {e}")
                raise
        
        # Start the scheduler after Flask is running
        try:
            self.start_scheduler()
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
        
        self._running = True
        self._start_time = time.time()
        
        # Do an initial ping to verify everything is working
        success = self.ping_self()
        if not success:
            logger.warning("Initial ping failed - service may not be properly configured")
        
        return self
    
    def stop(self) -> None:
        """Stop the KeepAliveService"""
        if not self._running:
            logger.warning("KeepAliveService is not running")
            return
            
        # Stop the scheduler
        if self.scheduler and self.scheduler.running:
            try:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
            except Exception as e:
                logger.error(f"Error shutting down scheduler: {e}")
        
        # Flask server will stop when the main thread exits since it's a daemon
        
        self._running = False
        logger.info("KeepAliveService stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the KeepAliveService"""
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "ping_interval": self.ping_interval,
            "total_pings": self._stats["total_pings"],
            "successful_pings": self._stats["successful_pings"],
            "failed_pings": self._stats["failed_pings"],
            "success_rate": (self._stats["successful_pings"] / max(1, self._stats["total_pings"])) * 100,
            "started_at": datetime.fromtimestamp(self._start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "external_url": self.external_url,
        }


def create_service(**kwargs) -> KeepAliveService:
    """
    Helper function to create and start a KeepAliveService instance.
    
    Args:
        **kwargs: Arguments to pass to KeepAliveService constructor
        
    Returns:
        A started KeepAliveService instance
    """
    service = KeepAliveService(**kwargs)
    return service.start()