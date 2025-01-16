import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", port=9000, reload=os.getenv("USH_DEBUG", False))
