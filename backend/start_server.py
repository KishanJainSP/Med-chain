#!/usr/bin/env python3
import uvicorn
import os

if __name__ == "__main__":
    # Start the FastAPI server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )