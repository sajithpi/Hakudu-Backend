from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, User, UserUpdate, UserLogin, LoginResponse
from app.models import User as UserModel
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.security import get_client_ip
from app.dependencies import get_current_active_user, optional_user
from app.middleware import limiter
import logging

router = APIRouter(prefix="/api/v1/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    client_ip = get_client_ip(request)
    logger.info(f"User registration attempt from {client_ip} for email: {user.email}")
    
    # Use service to create user
    db_user = UserService.create_user(db, user)
    
    logger.info(f"User registered successfully: {user.email} from {client_ip}")
    
    return db_user


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """User login"""
    client_ip = get_client_ip(request)
    
    # Use service to authenticate user
    return AuthService.authenticate_user(db, login_data, client_ip)


@router.get("/profile", response_model=User)
@limiter.limit("30/minute")
async def get_user_profile(
    request: Request,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get current user's profile"""
    return current_user


@router.put("/profile", response_model=User)
@limiter.limit("10/minute")
async def update_user_profile(
    request: Request,
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    # Use service to update user
    return UserService.update_user(db, current_user, user_update)


@router.get("/{user_id}", response_model=User)
@limiter.limit("30/minute")
async def get_user_by_id(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user by ID (public profile)"""
    return UserService.get_user_by_id(db, user_id)


@router.get("/", response_model=list[User])
@limiter.limit("20/minute")
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List users (paginated)"""
    return UserService.list_users(db, skip, limit)


@router.delete("/{user_id}")
@limiter.limit("5/minute")
async def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete user"""
    UserService.delete_user(db, user_id)
    return {"message": "User deleted successfully"}
