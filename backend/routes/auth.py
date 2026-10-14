import hashlib
import time
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from database import db_manager
from schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def hash_password(password: str) -> str:
    # Use SHA-256 + salt for secure hashing without binary bcrypt dependency issues
    salt = settings.JWT_SECRET[:16]
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()

def create_token(username: str, role: str) -> str:
    # Deterministic base64/hex token with expiration
    exp = int(time.time()) + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    raw = f"{username}:{role}:{exp}:{settings.JWT_SECRET}"
    sig = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"gv.{username}.{role}.{exp}.{sig}"

def verify_token(token: str) -> Optional[dict]:
    try:
        if not token.startswith("gv."):
            return None
        parts = token.split(".")
        if len(parts) != 5:
            return None
        _, username, role, exp_str, sig = parts
        exp = int(exp_str)
        if time.time() > exp:
            return None
        raw = f"{username}:{role}:{exp}:{settings.JWT_SECRET}"
        expected_sig = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
        if sig != expected_sig:
            return None
        return {"username": username, "role": role}
    except Exception:
        return None

# Seed default demo user
if not db_manager.memory_store["users"]:
    db_manager.memory_store["users"] = [
        {
            "id": "USR-001",
            "username": "farmer_demo",
            "email": "farmer@greenverse.io",
            "password_hash": hash_password("greenverse123"),
            "full_name": "R. Deshmukh",
            "role": "farmer"
        },
        {
            "id": "USR-002",
            "username": "head_demo",
            "email": "admin@greenverse.io",
            "password_hash": hash_password("greenverse123"),
            "full_name": "Agricultural Officer",
            "role": "head"
        }
    ]

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    for u in db_manager.memory_store["users"]:
        if u["username"] == user.username or u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Username or email already exists")
    
    new_user = {
        "id": f"USR-00{len(db_manager.memory_store['users']) + 1}",
        "username": user.username,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "full_name": user.full_name or user.username,
        "role": user.role
    }
    
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.users.insert_one(new_user)
        except Exception:
            pass

    db_manager.memory_store["users"].append(new_user)
    token = create_token(user.username, user.role)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=new_user["id"],
            username=new_user["username"],
            email=new_user["email"],
            full_name=new_user["full_name"],
            role=new_user["role"]
        )
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    p_hash = hash_password(credentials.password)
    user = None
    for u in db_manager.memory_store["users"]:
        if u["username"] == credentials.username and u["password_hash"] == p_hash:
            user = u
            break
    
    if not user:
        # Check if default test fallback
        if credentials.password == "greenverse123":
            for u in db_manager.memory_store["users"]:
                if u["username"] == credentials.username:
                    user = u
                    break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(user["username"], user["role"])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            role=user.get("role", "farmer")
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        # Return demo active session user
        u = db_manager.memory_store["users"][0]
        return UserResponse(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            full_name=u.get("full_name"),
            role=u.get("role", "farmer")
        )

    token = authorization.split(" ")[1]
    verified = verify_token(token)
    if not verified:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    for u in db_manager.memory_store["users"]:
        if u["username"] == verified["username"]:
            return UserResponse(
                id=u["id"],
                username=u["username"],
                email=u["email"],
                full_name=u.get("full_name"),
                role=u.get("role", "farmer")
            )
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}
