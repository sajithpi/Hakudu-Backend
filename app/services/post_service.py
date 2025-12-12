from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Post as PostModel
from app.schemas import PostCreate, PostUpdate
import logging

logger = logging.getLogger(__name__)


class PostService:
    """Service class for post-related business logic"""
    
    @staticmethod
    def create_post(db: Session, post_data: PostCreate, author_id: int) -> PostModel:
        """Create a new post"""
        db_post = PostModel(
            title=post_data.title,
            content=post_data.content,
            author_id=author_id,
            is_published=post_data.is_published
        )
        
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        logger.info(f"Post created successfully: {db_post.id} by user {author_id}")
        
        return db_post
    
    @staticmethod
    def get_post_by_id(db: Session, post_id: int) -> PostModel:
        """Get post by ID"""
        db_post = db.query(PostModel).filter(PostModel.id == post_id).first()
        
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return db_post
    
    @staticmethod
    def list_posts(db: Session, skip: int = 0, limit: int = 100, published_only: bool = True) -> list[PostModel]:
        """Get paginated list of posts"""
        query = db.query(PostModel)
        
        if published_only:
            query = query.filter(PostModel.is_published == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_posts(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[PostModel]:
        """Get posts by a specific user"""
        return db.query(PostModel).filter(
            PostModel.author_id == user_id,
            PostModel.is_published == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_post(db: Session, post: PostModel, post_update: PostUpdate, user_id: int) -> PostModel:
        """Update a post (only by owner)"""
        # Check ownership
        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )
        
        # Update post fields
        update_data = post_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)
        
        db.commit()
        db.refresh(post)
        
        logger.info(f"Post updated successfully: {post.id} by user {user_id}")
        
        return post
    
    @staticmethod
    def delete_post(db: Session, post: PostModel, user_id: int) -> None:
        """Delete a post (only by owner)"""
        # Check ownership
        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )
        
        db.delete(post)
        db.commit()
        
        logger.info(f"Post deleted successfully: {post.id} by user {user_id}")
