import asyncio
import subprocess
from typing import Literal

import aiofiles
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.dependencies.auth import APIKeyDep
from backend.dependencies.battery import BatteryDep

router = APIRouter(tags=["administrative"])


class CertResponse(BaseModel):
    cert: str


class StatusResponse(BaseModel):
    status: Literal["ok"]


class BatteryResponse(BaseModel):
    battery: int = Field(ge=0, le=100)


@router.post("/redeploy", status_code=status.HTTP_204_NO_CONTENT)
async def redeploy(_api_key: APIKeyDep) -> None:
    # Run the redeployment script
    await asyncio.to_thread(subprocess.run, ["/etc/raspap/redeploy.sh"], check=True)
    return None


@router.get("/certs")
async def get_certs(_api_key: APIKeyDep) -> CertResponse:
    """
    Get the SSL certificate for trusting the self-signed certificate
    """
    async with aiofiles.open("/etc/raspap/api/certs/server.crt") as f:
        return CertResponse(cert=await f.read())


@router.get("/status")
async def get_status(_api_key: APIKeyDep) -> StatusResponse:
    """
    Get the status of the API
    """
    return StatusResponse(status="ok")


@router.get("/battery")
async def get_battery(
    _api_key: APIKeyDep,
    fuel_gauge: BatteryDep,
) -> BatteryResponse:
    """
    Get the battery level of the device
    """
    if fuel_gauge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Battery hardware not found"
        )

    # Convert percentage to int as required by the model
    return BatteryResponse(battery=int(fuel_gauge.cell_percent))
