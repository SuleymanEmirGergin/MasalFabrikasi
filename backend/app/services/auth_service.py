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
                print(f"Error getting user by email: {e}")
                return None

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
                print(f"Error getting user by id: {e}")
                return None

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
            return None

        if not self.verify_password(password, user["password_hash"]):
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
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def create_refresh_token(self, user_id: str) -> str:
        """Refresh token oluşturur."""
        expire = datetime.utcnow() + timedelta(days=30)  # 30 gün
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def verify_refresh_token(self, token: str) -> str:
        """Refresh token'ı doğrular ve user_id döndürür."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
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
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
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

    async def create_password_reset_token(self, user_id: str, token: str):
        """Şifre sıfırlama token'ı oluşturur."""
        async with AsyncSessionLocal() as session:
            try:
                reset_token = PasswordResetToken(
                    user_id=user_id,
                    token=token,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                session.add(reset_token)
                await session.commit()
            except Exception as e:
                print(f"Error creating password reset token: {e}")
                raise

    async def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """Token ile şifre sıfırlama."""
        async with AsyncSessionLocal() as session:
            try:
                # Token'ı doğrula ve user_id'yi al
                result = await session.execute(
                    select(PasswordResetToken).where(PasswordResetToken.token == token)
                )
                reset_record = result.scalar_one_or_none()

                if not reset_record:
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

                # Token'ı sil
                await session.delete(reset_record)

                await session.commit()
                return True

            except Exception as e:
                print(f"Error resetting password: {e}")
                await session.rollback()
                return False

    async def create_email_verification_token(self, user_id: str, token: str):
        """Email doğrulama token'ı oluşturur."""
        async with AsyncSessionLocal() as session:
            try:
                verification_token = EmailVerificationToken(
                    user_id=user_id,
                    token=token,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                session.add(verification_token)
                await session.commit()
            except Exception as e:
                print(f"Error creating email verification token: {e}")
                raise

    async def verify_email_with_token(self, token: str) -> bool:
        """Token ile email doğrulaması."""
        async with AsyncSessionLocal() as session:
            try:
                # Token'ı doğrula
                result = await session.execute(
                    select(EmailVerificationToken).where(EmailVerificationToken.token == token)
                )
                verification_record = result.scalar_one_or_none()

                if not verification_record:
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

                # Token'ı sil
                await session.delete(verification_record)

                await session.commit()
                return True

            except Exception as e:
                print(f"Error verifying email: {e}")
                await session.rollback()
                return False

    def hash_password(self, password: str) -> str:
        """Şifreyi hashler."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Şifreyi doğrular."""
        return pwd_context.verify(plain_password, hashed_password)
