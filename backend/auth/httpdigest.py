from pydantic import BaseModel, ValidationError
from ..config import AppSettings, get_config
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPDigest,
    HTTPAuthorizationCredentials,
)
from fastapi import Depends, HTTPException, Request, Security
from fastapi.responses import JSONResponse
import secrets
import base64
from hashlib import md5
from typing import Annotated
from ..logger import custom_logger

config = get_config()
logger = custom_logger(__name__, debug=config.DEBUG)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    password: str


# TODO
# currently, HTTPDigest would return 403 instead of 401, so it would not trigger prompt to enter credentials
# workaround is to use auto_error=False
security = HTTPDigest(auto_error=False)

class HTTPDigestCredentials(BaseModel):
    username: str
    realm: str
    nonce: str
    uri: str
    response: str

    @classmethod
    def from_digest_line(cls, digest_line: str):
        """Parse the digest line and return a dict of fields"""
        # split and extract fields
        cred_dict = {}

        try:
            cred_fields = [s.strip() for s in digest_line.split(",")]
            for field, value in [s.split("=", maxsplit=1) for s in cred_fields]:
                # remove quotes
                cred_dict[field] = value.strip('"')
        
            cred_obj = cls.model_validate(cred_dict)

        except (ValueError, ValidationError):
            return None
        
        return cred_obj

async def auth_admin(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
    config: AppSettings = Depends(get_config),
):
    """ """
    # http digest headers
    digest_params = {
        "realm": "admin-panel",
        # "qop": "auth",
        # "algorithm": "SHA-256",
        "nonce": secrets.token_hex(8),
        # "opaque": secrets.token_hex(8),
    }
    digest_line = ",".join(
        f'{key}="{value}"' for key, value in digest_params.items()
    )

    login_fail_exception = HTTPException(
        401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": f'Digest {digest_line}'},
    )

    # if no Authorization header is present, credentials will be None
    if credentials is None:
        raise login_fail_exception
    
    # we use pydantic to validate the requested credential strings
    current_cred = HTTPDigestCredentials.from_digest_line(credentials.credentials)
    if current_cred is None:
        raise login_fail_exception

    # caluculate response
    # https://en.wikipedia.org/wiki/Digest_access_authentication#Overview
    admin_config = config.ADMIN_PANEL
    
    # We don't store plain passwords but HA1 instead
    # HA1 = md5(f"{admin_config.username}:{admin_config.realm}:{admin_config.password}".encode()).hexdigest()
    HA1 = admin_config.token
    HA2 = md5(f"{request.method}:{current_cred.uri}".encode()).hexdigest()
    expected_response = md5(f"{HA1}:{current_cred.nonce}:{HA2}".encode()).hexdigest()

    correct_token = secrets.compare_digest(current_cred.response, expected_response)

    if not correct_token:
        raise login_fail_exception

    return JSONResponse({"user": admin_config.username})
