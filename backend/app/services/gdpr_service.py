from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, delete

from app.core.database import get_db_context
from app.models import (
    User, UserProfile, Story, Character, Subscription,
    PrivacySettings, DataProcessingLog
)

class GDPRService:
    def __init__(self):
        pass

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Kullanıcının tüm verilerini toplar ve dışa aktarılabilir formatta döndürür.
        GDPR Article 15 compliance.
        """
        async with get_db_context() as session:
            export_data = {
                "export_info": {
                    "user_id": user_id,
                    "export_date": datetime.utcnow().isoformat(),
                    "gdpr_article": "Article 15 - Right of Access",
                    "data_controller": "Masal Fabrikası AI"
                },
                "user_profile": {},
                "stories": [],
                "characters": [],
                "usage_statistics": {},
                "subscription_data": {},
                "privacy_settings": {},
                "data_processing_log": []
            }

            try:
                # Kullanıcı profili
                user_result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user_dict = user.__dict__.copy()
                    user_dict.pop("_sa_instance_state", None)
                    # Hassas bilgileri çıkar
                    user_dict.pop("password_hash", None)
                    export_data["user_profile"] = user_dict

                # Kullanıcı Profili (Detaylar)
                profile_result = await session.execute(
                    select(UserProfile).where(UserProfile.auth_user_id == user_id)
                )
                profile = profile_result.scalar_one_or_none()
                if profile:
                    profile_dict = profile.__dict__.copy()
                    profile_dict.pop("_sa_instance_state", None)
                    export_data["user_profile"]["details"] = profile_dict
                    # İstatistikler profil içinde
                    export_data["usage_statistics"] = profile.statistics

                # Hikayeler
                # user_id profile.id ile eşleşir, ancak User tablosundaki id ile auth_user_id eşleşir.
                # Story tablosunda user_id UserProfile.id'dir.
                # Önce UserProfile id'sini bulmalıyız.
                if profile:
                    stories_result = await session.execute(
                        select(Story).where(Story.user_id == profile.id)
                    )
                    stories = stories_result.scalars().all()
                    export_data["stories"] = [
                        {k: v for k, v in s.__dict__.items() if k != "_sa_instance_state"}
                        for s in stories
                    ]

                    # Karakterler (created_by ile)
                    characters_result = await session.execute(
                        select(Character).where(Character.created_by == profile.id)
                    )
                    characters = characters_result.scalars().all()
                    export_data["characters"] = [
                        {k: v for k, v in c.__dict__.items() if k != "_sa_instance_state"}
                        for c in characters
                    ]

                    # Abonelik verileri
                    subscription_result = await session.execute(
                        select(Subscription).where(Subscription.user_id == profile.id)
                    )
                    subscription = subscription_result.scalar_one_or_none()
                    if subscription:
                        sub_dict = subscription.__dict__.copy()
                        sub_dict.pop("_sa_instance_state", None)
                        export_data["subscription_data"] = sub_dict

                # Gizlilik ayarları
                export_data["privacy_settings"] = await self.get_privacy_settings(user_id)

                # Veri işleme geçmişi
                export_data["data_processing_log"] = await self.get_data_processing_log(user_id, limit=100)

            except Exception as e:
                # Hata durumunda temel bilgileri döndür
                export_data["error"] = f"Veri toplama sırasında hata: {str(e)}"

            return export_data

    async def delete_user_data(self, user_id: str) -> bool:
        """
        Kullanıcının tüm verilerini anonimleştirir veya siler.
        GDPR Article 17 compliance.
        """
        async with get_db_context() as session:
            try:
                # UserProfile id bul
                profile_result = await session.execute(
                    select(UserProfile).where(UserProfile.auth_user_id == user_id)
                )
                profile = profile_result.scalar_one_or_none()

                if profile:
                    profile_id = profile.id

                    # 1. Hikayeleri sil
                    await session.execute(
                        delete(Story).where(Story.user_id == profile_id)
                    )

                    # 2. Karakterleri sil
                    await session.execute(
                        delete(Character).where(Character.created_by == profile_id)
                    )

                    # 4. Abonelikleri iptal et
                    await session.execute(
                        update(Subscription).where(Subscription.user_id == profile_id).values(
                            status="cancelled",
                            cancelled_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )

                # 5. Kullanıcıyı anonimleştir
                await session.execute(
                    update(User).where(User.id == user_id).values(
                        email=f"deleted_{user_id}@anonymous.local",
                        name="Anonymous User",
                        password_hash="",
                        email_verified=False,
                        is_active=False,
                        # deleted_at yok, updated_at kullan
                        updated_at=datetime.utcnow()
                    )
                )

                if profile:
                    await session.execute(
                        update(UserProfile).where(UserProfile.id == profile.id).values(
                            is_active=False,
                            is_banned=True, # Pasif yapmak için
                            updated_at=datetime.utcnow()
                        )
                    )

                await session.commit()

                # Silme işlemini logla
                await self.log_data_deletion(user_id, "GDPR Article 17 - Right to Erasure")

                return True

            except Exception as e:
                await session.rollback()
                print(f"Veri silme hatası: {str(e)}")
                return False

    async def get_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Kullanıcının gizlilik ayarlarını döndürür.
        """
        async with get_db_context() as session:
            try:
                result = await session.execute(
                    select(PrivacySettings).where(PrivacySettings.user_id == user_id)
                )
                settings = result.scalar_one_or_none()

                if settings:
                    settings_dict = settings.__dict__.copy()
                    settings_dict.pop("_sa_instance_state", None)
                    return settings_dict
                else:
                    return {
                        "analytics_consent": True,
                        "marketing_emails": False,
                        "data_sharing": False,
                        "profile_visibility": "private",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
            except Exception:
                return {
                    "analytics_consent": True,
                    "marketing_emails": False,
                    "data_sharing": False,
                    "profile_visibility": "private"
                }

    async def update_privacy_settings(self, user_id: str, settings_data: Dict[str, Any]):
        """
        Kullanıcının gizlilik ayarlarını günceller.
        """
        async with get_db_context() as session:
            try:
                settings_data["updated_at"] = datetime.utcnow()

                existing = await session.execute(
                    select(PrivacySettings).where(PrivacySettings.user_id == user_id)
                )
                existing_settings = existing.scalar_one_or_none()

                if existing_settings:
                    await session.execute(
                        update(PrivacySettings).where(PrivacySettings.user_id == user_id).values(**settings_data)
                    )
                else:
                    new_settings = PrivacySettings(
                        user_id=user_id,
                        **settings_data,
                        created_at=datetime.utcnow()
                    )
                    session.add(new_settings)

                await session.commit()

            except Exception:
                await session.rollback()
                raise

    async def get_data_processing_log(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Kullanıcının veri işleme geçmişini döndürür.
        """
        async with get_db_context() as session:
            try:
                result = await session.execute(
                    select(DataProcessingLog).where(DataProcessingLog.user_id == user_id)
                    .order_by(DataProcessingLog.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
                logs = result.scalars().all()
                return [
                    {k: v for k, v in log.__dict__.items() if k != "_sa_instance_state"}
                    for log in logs
                ]
            except Exception:
                return []

    async def log_data_export(self, user_id: str, export_type: str):
        """
        Veri dışa aktarma işlemini loglar.
        """
        async with get_db_context() as session:
            try:
                log_entry = DataProcessingLog(
                    user_id=user_id,
                    action="data_export",
                    details={"export_type": export_type},
                    created_at=datetime.utcnow()
                )
                session.add(log_entry)
                await session.commit()
            except Exception:
                pass

    async def log_data_deletion(self, user_id: str, reason: str):
        """
        Veri silme işlemini loglar.
        """
        async with get_db_context() as session:
            try:
                log_entry = DataProcessingLog(
                    user_id=user_id,
                    action="data_deletion",
                    details={"reason": reason},
                    created_at=datetime.utcnow()
                )
                session.add(log_entry)
                await session.commit()
            except Exception:
                pass

    async def withdraw_consent(self, user_id: str, consent_type: str):
        """
        Belirli bir consent'i geri çeker.
        """
        settings_map = {
            "analytics": "analytics_consent",
            "marketing": "marketing_emails",
            "personalization": "data_sharing",
            "third_party_sharing": "data_sharing"
        }

        if consent_type in settings_map:
            setting_key = settings_map[consent_type]
            await self.update_privacy_settings(user_id, {setting_key: False})

        # Consent geri çekme işlemini logla
        async with get_db_context() as session:
            try:
                log_entry = DataProcessingLog(
                    user_id=user_id,
                    action="consent_withdrawal",
                    details={"consent_type": consent_type},
                    created_at=datetime.utcnow()
                )
                session.add(log_entry)
                await session.commit()
            except Exception:
                pass
