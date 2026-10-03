from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from config import settings
from database import get_db, init_db
from models import User, RoleEnum, TokenBlacklist
from schemas import LoginRequest, LoginResponse, UserCreate, UserResponse, RefreshRequest, UserRoleUpdate
from auth import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, get_current_user, require_role, verify_token
)
from audit import init_kafka, close_kafka, log_audit_event
from metrics import auth_requests_total, auth_failures_total, active_users_gauge, request_duration_seconds

import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_kafka()
    yield
    await close_kafka()

app = FastAPI(title="Authentication Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    request_duration_seconds.labels(endpoint=request.url.path).observe(duration)
    return response

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth_requests_total.labels(method="POST", status="attempt").inc()
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().first()
    
    if not user or not verify_password(login_data.password, user.password_hash) or not user.is_active:
        auth_failures_total.labels(reason="invalid_credentials").inc()
        await log_audit_event(db, "LOGIN", "SYSTEM", "FAILED", ip_address=request.client.host)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    auth_requests_total.labels(method="POST", status="success").inc()
    await log_audit_event(db, "LOGIN", "SYSTEM", "SUCCESS", actor_id=user.id, ip_address=request.client.host)
    active_users_gauge.inc()
    
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)

@app.post("/auth/logout")
async def logout(request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]
        token_data = await verify_token(token, db)
        blacklist = TokenBlacklist(token_jti=token_data.jti)
        db.add(blacklist)
        await db.commit()
    
    await log_audit_event(db, "LOGOUT", "SYSTEM", "SUCCESS", actor_id=current_user.id, ip_address=request.client.host)
    active_users_gauge.dec()
    return {"message": "Successfully logged out"}

@app.post("/auth/refresh", response_model=LoginResponse)
async def refresh(refresh_req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        token_data = await verify_token(refresh_req.refresh_token, db)
        result = await db.execute(select(User).where(User.id == int(token_data.sub)))
        user = result.scalars().first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)
        
        return LoginResponse(access_token=access_token, refresh_token=new_refresh_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.post("/auth/register", response_model=UserResponse)
async def register(
    request: Request,
    user_data: UserCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(require_role([RoleEnum.ADMIN]))
):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    await log_audit_event(
        db, "REGISTER_USER", f"User:{new_user.id}", "SUCCESS", 
        actor_id=current_user.id, ip_address=request.client.host
    )
    return new_user

@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/auth/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.OPERATOR]))
):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@app.put("/auth/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    request: Request,
    user_id: int, 
    role_update: UserRoleUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN]))
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = user.role
    user.role = role_update.role
    await db.commit()
    await db.refresh(user)
    
    await log_audit_event(
        db, "UPDATE_ROLE", f"User:{user.id}", "SUCCESS", 
        actor_id=current_user.id, ip_address=request.client.host,
        details={"old": old_role.value, "new": user.role.value}
    )
    return user

@app.get("/health")
async def health():
    return {"status": "up"}

@app.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unready")

@app.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
