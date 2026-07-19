import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Request, Depends
import os

DEFAULT_DEV_SECRET = "supersecretkey_for_dev_only"
SECRET_KEY = os.environ.get("SECRET_KEY", DEFAULT_DEV_SECRET)
APP_ENV = os.environ.get("APP_ENV", "development").lower()
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "true" if APP_ENV == "production" else "false").lower() in {"1", "true", "yes"}
if APP_ENV == "production" and SECRET_KEY == DEFAULT_DEV_SECRET:
    raise RuntimeError("SECRET_KEY must be set in production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        # We no longer strip "Bearer " because the cookie now contains the raw JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub_str = payload.get("sub")
        role: str = payload.get("role")
        if sub_str is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id: int = int(sub_str)
        return {"id": user_id, "role": role}
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Could not validate credentials")


def require_boss(user: dict = Depends(get_current_user)):
    if user.get("role") != "boss":
        raise HTTPException(status_code=403, detail="Not authorized. Boss access required.")
    return user

def require_academic_admin(user: dict = Depends(get_current_user)):
    if user.get("role") not in ["boss", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized. Academic Admin access required.")
    return user

def require_teacher_access(user: dict = Depends(get_current_user)):
    if user.get("role") not in ["boss", "supervisor", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized. Teacher access required.")
    return user

def require_finance_access(user: dict = Depends(get_current_user)):
    if user.get("role") not in ["boss", "moneyman"]:
        raise HTTPException(status_code=403, detail="Not authorized. Finance access required.")
    return user
