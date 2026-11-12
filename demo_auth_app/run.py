"""Runner script to start the local web application."""
import uvicorn
from app.config import APP_HOST, APP_PORT

if __name__ == "__main__":
    print(f"Starting Demo Auth App at http://{APP_HOST}:{APP_PORT} ...")
    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=True)

