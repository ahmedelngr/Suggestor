import os

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer()


def supabase_headers(token: str) -> dict[str, str]:
    return {"apikey": os.environ["SUPABASE_ANON_KEY"], "Authorization": f"Bearer {token}"}


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict[str, str]:
    url = f"{os.environ['SUPABASE_URL']}/auth/v1/user"
    resp = httpx.get(url, headers=supabase_headers(creds.credentials), timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"auth_id": resp.json()["id"], "token": creds.credentials}
