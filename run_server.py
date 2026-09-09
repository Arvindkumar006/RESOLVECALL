import uvicorn
from resolvecall.core.config import settings

if __name__ == "__main__":
    print(f"Starting ResolveCall Mission Control on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "resolvecall.web.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info",
    )
