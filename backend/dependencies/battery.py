from typing import Annotated

from adafruit_max1704x import MAX17048
from fastapi import Depends, Request


def get_fuel_gauge(request: Request) -> MAX17048 | None:
    return request.app.state.fuel_gauge


BatteryDep = Annotated[MAX17048 | None, Depends(get_fuel_gauge)]
