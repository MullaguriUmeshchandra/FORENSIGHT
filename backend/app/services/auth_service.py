from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.auth.security import get_password_hash, verify_password
from app.auth.jwt import create_access_token
from app.services.activity_service import ActivityService

class AuthService:
    """Authentication and user management service."""

    @staticmethod
    def register_user(db: Session, user_in: UserCreate, ip_address: Optional[str] = None) -> UserResponse:
        # Check existing username
        if db.query(User).filter(User.username == user_in.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        # Check existing email
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        ActivityService.log_activity(
            db=db,
            action="USER_REGISTERED",
            user_id=db_user.id,
            details={"username": db_user.username, "role": str(db_user.role)},
            ip_address=ip_address
        )
        return UserResponse.model_validate(db_user)

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin, ip_address: Optional[str] = None) -> Token:
        user = db.query(User).filter(User.username == login_data.username).first()
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": str(user.role.value if hasattr(user.role, 'value') else user.role)}
        )

        ActivityService.log_activity(
            db=db,
            action="USER_LOGIN",
            user_id=user.id,
            details={"username": user.username},
            ip_address=ip_address
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
