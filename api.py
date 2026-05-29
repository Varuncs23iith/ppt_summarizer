"""
API Application Entry Point

Initializes and runs the FastAPI application with proper configuration.
"""

import uvicorn
from controller import app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Main entry point for the API server."""
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"
    log_level = os.getenv("API_LOG_LEVEL", "info")

    # Run the server
    uvicorn.run(
        "controller:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()
