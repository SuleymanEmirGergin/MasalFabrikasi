from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.services.auth_service import AuthService
from app.core.config import settings

router = APIRouter()
auth_service = AuthService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class EmailVerificationConfirmRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=TokenResponse)
async def register_user(request: UserRegisterRequest, background_tasks: BackgroundTasks):
    """
    Yeni kullanıcı kaydı oluşturur ve email doğrulama gönderir.
    """
    try:
        # Kullanıcıyı oluştur
        user = await auth_service.register_user(
            email=request.email,
            password=request.password,
            name=request.name
        )

        # Email doğrulama token'ı oluştur
        verification_token = secrets.token_urlsafe(32)
        await auth_service.create_email_verification_token(user["id"], verification_token)

        # Email doğrulama maili gönder (background task)
        background_tasks.add_task(
            send_verification_email,
            request.email,
            verification_token
        )

        # Access token oluştur
        access_token = await auth_service.create_access_token(
            data={"sub": str(user["id"])},
            expires_delta=timedelta(hours=24)
        )

        return TokenResponse(
            access_token=access_token,
            expires_in=86400,  # 24 hours
            user=user
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kayıt sırasında hata oluştu: {str(e)}")

@router.post("/login", response_model=TokenResponse)
async def login_user(request: UserLoginRequest):
    """
    Kullanıcı girişi yapar.
    """
    try:
        user = await auth_service.authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Geçersiz email veya şifre")

        # Email doğrulanmamışsa uyarı ver ama girişe izin ver
        if not user.get("email_verified", False):
            # İsteğe bağlı: email doğrulama hatırlatma maili gönder
            pass

        access_token = await auth_service.create_access_token(
            data={"sub": str(user["id"])},
            expires_delta=timedelta(hours=24)
        )

        return TokenResponse(
            access_token=access_token,
            expires_in=86400,
            user=user
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Giriş sırasında hata oluştu: {str(e)}")

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh token kullanarak yeni access token alır.
    """
    try:
        # Refresh token'ı doğrula ve yeni access token oluştur
        user_id = await auth_service.verify_refresh_token(request.refresh_token)
        user = await auth_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=401, detail="Geçersiz refresh token")

        access_token = await auth_service.create_access_token(
            data={"sub": str(user["id"])},
            expires_delta=timedelta(hours=24)
        )

        return TokenResponse(
            access_token=access_token,
            expires_in=86400,
            user=user
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token yenileme sırasında hata oluştu: {str(e)}")

@router.post("/password-reset")
async def request_password_reset(request: PasswordResetRequest, background_tasks: BackgroundTasks):
    """
    Şifre sıfırlama maili gönderir.
    """
    try:
        # Kullanıcıyı bul (email var mı kontrol et)
        user = await auth_service.get_user_by_email(request.email)
        if user:
            # Reset token oluştur
            reset_token = secrets.token_urlsafe(32)
            await auth_service.create_password_reset_token(user["id"], reset_token)

            # Reset maili gönder
            background_tasks.add_task(
                send_password_reset_email,
                request.email,
                reset_token
            )

        # Güvenlik için her zaman aynı yanıtı ver (kullanıcı varlığını belli etme)
        return {"message": "Şifre sıfırlama maili gönderildi (eğer hesap varsa)"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Şifre sıfırlama isteği sırasında hata oluştu: {str(e)}")

@router.post("/password-reset-confirm")
async def confirm_password_reset(request: PasswordResetConfirmRequest):
    """
    Şifre sıfırlama token'ını kullanarak yeni şifre belirler.
    """
    try:
        success = await auth_service.reset_password_with_token(
            request.token,
            request.new_password
        )

        if not success:
            raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş token")

        return {"message": "Şifre başarıyla güncellendi"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Şifre güncelleme sırasında hata oluştu: {str(e)}")

@router.post("/verify-email")
async def request_email_verification(request: EmailVerificationRequest, background_tasks: BackgroundTasks):
    """
    Email doğrulama maili gönderir.
    """
    try:
        user = await auth_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        if user.get("email_verified", False):
            return {"message": "Email zaten doğrulanmış"}

        # Verification token oluştur
        verification_token = secrets.token_urlsafe(32)
        await auth_service.create_email_verification_token(user["id"], verification_token)

        # Verification maili gönder
        background_tasks.add_task(
            send_verification_email,
            request.email,
            verification_token
        )

        return {"message": "Email doğrulama maili gönderildi"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email doğrulama isteği sırasında hata oluştu: {str(e)}")

@router.post("/verify-email-confirm")
async def confirm_email_verification(request: EmailVerificationConfirmRequest):
    """
    Email doğrulama token'ını kullanarak email'i doğrular.
    """
    try:
        success = await auth_service.verify_email_with_token(request.token)

        if not success:
            raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş token")

        return {"message": "Email başarıyla doğrulandı"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email doğrulama sırasında hata oluştu: {str(e)}")

@router.post("/logout")
async def logout_user(token: str = Depends(oauth2_scheme)):
    """
    Kullanıcı çıkışını yapar (token'ı blacklist'e alır).
    """
    try:
        await auth_service.blacklist_token(token)
        return {"message": "Başarıyla çıkış yapıldı"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çıkış sırasında hata oluştu: {str(e)}")

# Email gönderme yardımcı fonksiyonları
async def send_verification_email(email: str, token: str):
    """Email doğrulama maili gönderir."""
    try:
        subject = "Masal Fabrikası - Email Doğrulama"
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        html_content = f"""
        <html>
        <body>
            <h2>Hoş Geldiniz!</h2>
            <p>Email adresinizi doğrulamak için aşağıdaki bağlantıya tıklayın:</p>
            <a href="{verification_url}">Email'i Doğrula</a>
            <p>Bu bağlantı 24 saat geçerlidir.</p>
            <p>Bu maili siz istemediyseniz, lütfen dikkate almayın.</p>
        </body>
        </html>
        """

        await send_email(email, subject, html_content)

    except Exception as e:
        print(f"Email doğrulama maili gönderilemedi: {str(e)}")

async def send_password_reset_email(email: str, token: str):
    """Şifre sıfırlama maili gönderir."""
    try:
        subject = "Masal Fabrikası - Şifre Sıfırlama"
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        html_content = f"""
        <html>
        <body>
            <h2>Şifre Sıfırlama</h2>
            <p>Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:</p>
            <a href="{reset_url}">Şifreyi Sıfırla</a>
            <p>Bu bağlantı 1 saat geçerlidir.</p>
            <p>Bu maili siz istemediyseniz, lütfen dikkate almayın.</p>
        </body>
        </html>
        """

        await send_email(email, subject, html_content)

    except Exception as e:
        print(f"Şifre sıfırlama maili gönderilemedi: {str(e)}")

async def send_email(to_email: str, subject: str, html_content: str):
    """Genel email gönderme fonksiyonu."""
    try:
        # SMTP ayarları (örnek - gerçek implementasyona göre değiştirin)
        smtp_server = settings.SMTP_SERVER or "smtp.gmail.com"
        smtp_port = settings.SMTP_PORT or 587
        smtp_username = settings.SMTP_USERNAME
        smtp_password = settings.SMTP_PASSWORD

        if not all([smtp_username, smtp_password]):
            print("SMTP ayarları eksik, email gönderilemedi")
            return

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = to_email

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()

    except Exception as e:
        print(f"Email gönderilemedi: {str(e)}")
        # Production'da error logging sistemi kullanılmalı
