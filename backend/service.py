import asyncio
import subprocess

from fastapi import APIRouter, status

from .auth import APIKeyDep

router = APIRouter(tags=["service"])


@router.get("/redeploy", status_code=status.HTTP_204_NO_CONTENT)
async def redeploy(_api_key: str = APIKeyDep) -> None:
    # Run the redeployment script
    await asyncio.to_thread(subprocess.run, ["/etc/raspap/redeploy.sh"], check=True)
    return None
