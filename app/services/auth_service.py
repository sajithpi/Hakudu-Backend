from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import User as UserModel
from app.schemas import UserLogin, LoginResponse
from app.auth import verify_password, create_access_token
from app.security import get_client_ip
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication-related business logic"""
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin, client_ip: str = None) -> LoginResponse:
        """Authenticate user and return login response"""
        logger.info(f"Login attempt from {client_ip} for email: {login_data.email}")
        
        # Find user by email
        db_user = db.query(UserModel).filter(UserModel.email == login_data.email).first()
        
        # Check credentials
        if not db_user or not verify_password(login_data.password, db_user.hashed_password):
            logger.warning(f"Failed login attempt from {client_ip} for email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": db_user.username},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in successfully: {login_data.email} from {client_ip}")
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=db_user
        )
    
    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        """Refresh JWT token (placeholder for future implementation)"""
        # TODO: Implement token refresh logic
        logger.info("Token refresh requested")
        return {"message": "Token refresh functionality not implemented yet"}
    
    @staticmethod
    def initiate_password_reset(db: Session, email: str) -> dict:
        """Initiate password reset process"""
        # TODO: Implement password reset logic
        logger.info(f"Password reset requested for email: {email}")
        return {"message": "Password reset email sent (if email exists)"}
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> dict:
        """Reset password with token"""
        # TODO: Implement password reset with token validation
        logger.info("Password reset with token requested")
        return {"message": "Password reset functionality not implemented yet"}
