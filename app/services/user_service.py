from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import User as UserModel
from app.schemas import UserCreate, UserUpdate
from app.auth import get_password_hash
from app.security import SecurityValidator
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user-related business logic"""
    
    @staticmethod
    def validate_user_data(user_data: UserCreate) -> None:
        """Validate user registration data"""
        # Validate password strength
        password_validation = SecurityValidator.validate_password_strength(user_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "issues": password_validation["issues"]
                }
            )
        
        # Validate username
        username_validation = SecurityValidator.validate_username(user_data.username)
        if not username_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Username is invalid",
                    "issues": username_validation["issues"]
                }
            )
    
    @staticmethod
    def check_user_exists(db: Session, email: str, username: str) -> None:
        """Check if user with email or username already exists"""
        db_user = db.query(UserModel).filter(
            (UserModel.email == email) | (UserModel.username == username)
        ).first()
        
        if db_user:
            if db_user.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserModel:
        """Create a new user in the database"""
        # Validate user data
        UserService.validate_user_data(user_data)
        
        # Check if user already exists
        UserService.check_user_exists(db, user_data.email, user_data.username)
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user instance
        db_user = UserModel(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active
        )
        
        # Save to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User created successfully: {user_data.email}")
        
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> UserModel:
        """Get user by ID"""
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> UserModel:
        """Get user by email"""
        db_user = db.query(UserModel).filter(UserModel.email == email).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return db_user
    
    @staticmethod
    def update_user(db: Session, user: UserModel, user_update: UserUpdate) -> UserModel:
        """Update user information"""
        update_data = user_update.dict(exclude_unset=True)
        
        # If email or username is being updated, check for conflicts
        if "email" in update_data or "username" in update_data:
            new_email = update_data.get("email", user.email)
            new_username = update_data.get("username", user.username)
            
            # Check if new email or username conflicts with existing users
            existing_user = db.query(UserModel).filter(
                UserModel.id != user.id,  # Exclude current user
                (UserModel.email == new_email) | (UserModel.username == new_username)
            ).first()
            
            if existing_user:
                if existing_user.email == new_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
        
        # Update user fields
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated successfully: {user.email}")
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        """Delete user by ID"""
        db_user = UserService.get_user_by_id(db, user_id)
        
        db.delete(db_user)
        db.commit()
        
        logger.info(f"User deleted successfully: {db_user.email}")
    
    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserModel]:
        """Get paginated list of users"""
        return db.query(UserModel).offset(skip).limit(limit).all()
