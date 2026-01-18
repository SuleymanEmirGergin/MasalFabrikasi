from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import jwt
import secrets
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, delete
import json

from app.core.database import AsyncSessionLocal
from app.models import User, PasswordResetToken, EmailVerificationToken
from app.core.config import settings
from app.core.business_metrics import auth_failures_total, auth_tokens_created_total, auth_tokens_consumed_total
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 24 * 60  # 24 hours

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Email'e göre kullanıcıyı getirir."""
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()
                if user:
                    user_dict = user.__dict__.copy()
                    user_dict.pop("_sa_instance_state", None)
                    return user_dict
                return None
            except Exception as e:
                logger.error(f"Error getting user by email: {e}")
                raise

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ID'ye göre kullanıcıyı getirir."""
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                if user:
                    user_dict = user.__dict__.copy()
                    user_dict.pop("_sa_instance_state", None)
                    return user_dict
                return None
            except Exception as e:
                logger.error(f"Error getting user by id: {e}")
                raise

    async def register_user(self, email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Yeni kullanıcı kaydı oluşturur."""
        # Email kontrolü
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("Bu email adresi zaten kayıtlı")

        async with AsyncSessionLocal() as session:
            # Şifreyi hashle
            hashed_password = self.hash_password(password)

            # Kullanıcı oluştur
            new_user = User(
                email=email,
                password_hash=hashed_password,
                name=name,
                email_verified=False,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            try:
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)

                user_dict = new_user.__dict__.copy()
                user_dict.pop("_sa_instance_state", None)
                return user_dict
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Kullanıcı kaydı oluşturulamadı: {str(e)}")

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Kullanıcıyı email ve şifre ile doğrular."""
        user = await self.get_user_by_email(email)
        if not user:
            auth_failures_total.labels(reason="user_not_found").inc()
            return None

        if not self.verify_password(password, user["password_hash"]):
            auth_failures_total.labels(reason="invalid_password").inc()
            return None

        return user

    async def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """JWT access token oluşturur."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        # Enforce algorithm
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm="HS256")
        return encoded_jwt

    async def create_refresh_token(self, user_id: str) -> str:
        """Refresh token oluşturur."""
        expire = datetime.utcnow() + timedelta(days=30)  # 30 gün
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm="HS256")
        return encoded_jwt

    async def verify_refresh_token(self, token: str) -> str:
        """Refresh token'ı doğrular ve user_id döndürür."""
        try:
            # Enforce strict algorithm validation
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")

            user_id: str = payload.get("sub")
            if user_id is None:
                raise ValueError("Invalid token")

            return user_id
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.JWTError:
            raise ValueError("Invalid token")

    async def verify_token(self, token: str) -> Optional[str]:
        """Access token'ı doğrular ve user_id döndürür."""
        try:
            # Enforce strict algorithm validation
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None

    async def blacklist_token(self, token: str):
        """Token'ı blacklist'e alır (logout için)."""
        # Bu basit implementasyon için in-memory blacklist kullanıyoruz
        # Production'da Redis veya database kullanılmalı
        # Bu kısım geliştirilebilir
        pass

    def hash_token(self, token: str) -> str:
        """Hashes the token using SHA256."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()

    async def create_password_reset_token(self, user_id: str, token: str):
        """Şifre sıfırlama token'ı oluşturur."""
        token_hash = self.hash_token(token)
        async with AsyncSessionLocal() as session:
            try:
                # Invalidate existing active tokens for this user
                await session.execute(
                    update(PasswordResetToken)
                    .where(
                        PasswordResetToken.user_id == user_id,
                        PasswordResetToken.consumed_at.is_(None)
                    )
                    .values(consumed_at=datetime.utcnow())
                )

                reset_token = PasswordResetToken(
                    user_id=user_id,
                    token_hash=token_hash,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                session.add(reset_token)
                await session.commit()
                auth_tokens_created_total.labels(token_type="password_reset").inc()
            except Exception as e:
                logger.error(f"Error creating password reset token: {e}")
                raise

    async def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """Token ile şifre sıfırlama."""
        token_hash = self.hash_token(token)
        async with AsyncSessionLocal() as session:
            try:
                # Token'ı doğrula ve user_id'yi al
                result = await session.execute(
                    select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
                )
                reset_record = result.scalar_one_or_none()

                if not reset_record:
                    return False

                if reset_record.consumed_at is not None:
                    # Token already consumed
                    return False

                if reset_record.expires_at < datetime.utcnow():
                    return False

                user_id = reset_record.user_id

                # Şifreyi güncelle
                hashed_password = self.hash_password(new_password)

                # Update user
                await session.execute(
                    update(User).where(User.id == user_id).values(
                        password_hash=hashed_password,
                        updated_at=datetime.utcnow()
                    )
                )

                # Mark token as consumed
                reset_record.consumed_at = datetime.utcnow()
                session.add(reset_record)

                await session.commit()
                auth_tokens_consumed_total.labels(token_type="password_reset").inc()
                return True

            except Exception as e:
                logger.error(f"Error resetting password: {e}")
                await session.rollback()
                return False

    async def create_email_verification_token(self, user_id: str, token: str):
        """Email doğrulama token'ı oluşturur."""
        token_hash = self.hash_token(token)
        async with AsyncSessionLocal() as session:
            try:
                # Invalidate existing tokens
                await session.execute(
                    update(EmailVerificationToken)
                    .where(
                        EmailVerificationToken.user_id == user_id,
                        EmailVerificationToken.consumed_at.is_(None)
                    )
                    .values(consumed_at=datetime.utcnow())
                )

                verification_token = EmailVerificationToken(
                    user_id=user_id,
                    token_hash=token_hash,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                session.add(verification_token)
                await session.commit()
                auth_tokens_created_total.labels(token_type="email_verification").inc()
            except Exception as e:
                logger.error(f"Error creating email verification token: {e}")
                raise

    async def verify_email_with_token(self, token: str) -> bool:
        """Token ile email doğrulaması."""
        token_hash = self.hash_token(token)
        async with AsyncSessionLocal() as session:
            try:
                # Token'ı doğrula
                result = await session.execute(
                    select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
                )
                verification_record = result.scalar_one_or_none()

                if not verification_record:
                    return False

                if verification_record.consumed_at is not None:
                    return False

                if verification_record.expires_at < datetime.utcnow():
                    return False

                user_id = verification_record.user_id

                # Email'i doğrulanmış olarak işaretle
                await session.execute(
                    update(User).where(User.id == user_id).values(
                        email_verified=True,
                        updated_at=datetime.utcnow()
                    )
                )

                # Mark token as consumed
                verification_record.consumed_at = datetime.utcnow()
                session.add(verification_record)

                await session.commit()
                auth_tokens_consumed_total.labels(token_type="email_verification").inc()
                return True

            except Exception as e:
                logger.error(f"Error verifying email: {e}")
                await session.rollback()
                return False

    def hash_password(self, password: str) -> str:
        """Şifreyi hashler."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Şifreyi doğrular."""
        return pwd_context.verify(plain_password, hashed_password)
