# keepalive/service.py
import os
import time
import threading
import socket
import requests
from typing import Optional, Dict, Any, Callable, Union
import logging
import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask

# Configure logging
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
        """
        Initialize the KeepAliveService.
        
        Args:
            ping_interval: Interval in seconds between pings
            ping_endpoint: Endpoint path to use for ping
            ping_message: Message returned when ping endpoint is hit
            port: Port for the Flask server to run on
            host: Host for the Flask server to run on
            timezone: Timezone for the scheduler
            external_url: URL to ping (defaults to auto-detected URL)
            custom_pinger: Custom function to execute instead of the default pinger
            use_flask: Whether to start a Flask server
            scheduler_options: Additional options for the BackgroundScheduler
            log_level: Logging level
        """
        # Set up logging
        self.configure_logging(log_level)
        
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
    
    def configure_logging(self, log_level: int) -> None:
        """Set up logging for the service"""
        logger.setLevel(log_level)
        
        # Create handler if none exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    
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
                return True
            except Exception as e:
                logger.error(f"Custom pinger failed: {e}")
                self._stats["total_pings"] += 1
                self._stats["failed_pings"] += 1
                return False
        
        url = f"{self.external_url}/{self.ping_endpoint}"
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start_time
            
            self._stats["total_pings"] += 1
            
            if response.status_code == 200:
                logger.info(f"Ping successful in {elapsed:.2f}s")
                self._stats["successful_pings"] += 1
                return True
            else:
                logger.error(f"Ping failed with status code {response.status_code}")
                self._stats["failed_pings"] += 1
                return False
        except Exception as e:
            logger.error(f"Ping failed with exception: {e}")
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
        
        self.scheduler = BackgroundScheduler(**scheduler_opts)
        
        # Add the ping job
        self.scheduler.add_job(
            self.ping_self,
            IntervalTrigger(seconds=self.ping_interval),
            id="ping_job",
            name="Keep-alive ping",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started with {self.ping_interval}s interval")
    
    def setup_flask(self) -> None:
        """Set up the Flask application with the ping endpoint"""
        if not self.use_flask:
            return
            
        self.app = Flask(__name__)
        
        # Register the ping endpoint
        @self.app.route(f"/{self.ping_endpoint}")
        def alive():
            logger.debug("Received ping request")
            return self.ping_message
        
        # Add a stats endpoint
        @self.app.route("/keepalive/stats")
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
            self.app.run(host=self.host, port=self.port)
        except Exception as e:
            logger.error(f"Failed to start Flask server: {e}")
    
    def start(self) -> "KeepAliveService":
        """Start the KeepAliveService (both Flask server and scheduler)"""
        if self._running:
            logger.warning("KeepAliveService is already running")
            return self
            
        # Set up and start Flask server if needed
        if self.use_flask:
            self.setup_flask()
            self.flask_thread = threading.Thread(target=self.run_flask)
            self.flask_thread.daemon = True
            self.flask_thread.start()
            logger.info(f"Flask server started on {self.host}:{self.port}")
        
        # Start the scheduler
        self.start_scheduler()
        
        self._running = True
        self._start_time = time.time()
        
        # Do an initial ping
        self.ping_self()
        
        return self
    
    def stop(self) -> None:
        """Stop the KeepAliveService"""
        if not self._running:
            logger.warning("KeepAliveService is not running")
            return
            
        # Stop the scheduler
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        
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