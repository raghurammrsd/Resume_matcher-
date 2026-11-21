import os
import uvicorn
from backend.app.core.logging import logger

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting TalentMatch AI on 0.0.0.0:{port}...")
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
