import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
try:
    from jose import JWTError, jwt
except ImportError:
    import jwt
    try:
        from jwt.exceptions import PyJWTError as JWTError
    except ImportError:
        JWTError = Exception
from app.schemas.auth import TokenData
from app.utils.logger import logger

SECRET_KEY = os.getenv("JWT_SECRET", "forensics_super_secret_jwt_key_reconstruction_2026_x99182374")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role")
        if user_id is None:
            return None
        return TokenData(user_id=int(user_id), username=username, role=role)
    except JWTError as e:
        logger.debug(f"JWT decode error: {e}")
        return None
