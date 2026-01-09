from fastapi import Cookie, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from .settings import settings

api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def get_api_key(
    api_key_header: str | None = Security(api_key_header),
    access_token: str | None = Cookie(None),
) -> str:
    # Check cookie first (for browser), then header (for API clients)
    provided_key = access_token or api_key_header

    if provided_key is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="403: Unauthorized"
        )

    if provided_key == settings.raspap_api_key:
        return provided_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="403: Unauthorized"
        )


APIKeyDep = Depends(get_api_key)
