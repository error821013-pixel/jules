import uvicorn
import os

if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    # Get host from environment variable or default to 127.0.0.1
    host = os.getenv("HOST", "127.0.0.1")

    print(f"Starting Gaming Club Application on http://{host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )
