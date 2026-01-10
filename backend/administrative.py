import asyncio
import subprocess
from typing import Literal

import aiofiles
from fastapi import APIRouter, status
from pydantic import BaseModel

from .auth import APIKeyDep

router = APIRouter(tags=["administrative"])


class CertResponse(BaseModel):
    cert: str


class StatusResponse(BaseModel):
    status: Literal["ok"]


@router.post("/redeploy", status_code=status.HTTP_204_NO_CONTENT)
async def redeploy(_api_key: str = APIKeyDep) -> None:
    # Run the redeployment script
    await asyncio.to_thread(subprocess.run, ["/etc/raspap/redeploy.sh"], check=True)
    return None


@router.get("/certs")
async def get_certs(_api_key: str = APIKeyDep) -> CertResponse:
    """
    Get the SSL certificate for trusting the self-signed certificate
    """
    async with aiofiles.open("/etc/raspap/api/certs/server.crt") as f:
        return CertResponse(cert=await f.read())


@router.get("/status")
async def get_status(_api_key: str = APIKeyDep) -> StatusResponse:
    """
    Get the status of the API
    """
    return StatusResponse(status="ok")
