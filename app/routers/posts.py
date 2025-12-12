from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PostCreate, Post, PostUpdate
from app.models import Post as PostModel, User as UserModel
from app.services.post_service import PostService
from app.dependencies import get_current_active_user, optional_user
from app.middleware import limiter
from app.security import get_client_ip
import logging

router = APIRouter(prefix="/api/v1/posts", tags=["posts"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_post(
    request: Request,
    post: PostCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    client_ip = get_client_ip(request)
    logger.info(f"Post creation attempt from {client_ip} by user {current_user.id}")
    
    return PostService.create_post(db, post, current_user.id)


@router.get("/", response_model=list[Post])
@limiter.limit("30/minute")
async def list_posts(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True,
    db: Session = Depends(get_db)
):
    """List posts (paginated)"""
    return PostService.list_posts(db, skip, limit, published_only)


@router.get("/{post_id}", response_model=Post)
@limiter.limit("50/minute")
async def get_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific post"""
    return PostService.get_post_by_id(db, post_id)


@router.put("/{post_id}", response_model=Post)
@limiter.limit("10/minute")
async def update_post(
    request: Request,
    post_id: int,
    post_update: PostUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post"""
    db_post = PostService.get_post_by_id(db, post_id)
    return PostService.update_post(db, db_post, post_update, current_user.id)


@router.delete("/{post_id}")
@limiter.limit("5/minute")
async def delete_post(
    request: Request,
    post_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post"""
    db_post = PostService.get_post_by_id(db, post_id)
    PostService.delete_post(db, db_post, current_user.id)
    return {"message": "Post deleted successfully"}


@router.get("/user/{user_id}", response_model=list[Post])
@limiter.limit("30/minute")
async def get_user_posts(
    request: Request,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get posts by a specific user"""
    return PostService.get_user_posts(db, user_id, skip, limit)
