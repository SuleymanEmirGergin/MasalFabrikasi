from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, delete

from app.core.database import get_db

class GDPRService:
    def __init__(self):
        pass

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Kullanıcının tüm verilerini toplar ve dışa aktarılabilir formatta döndürür.
        GDPR Article 15 compliance.
        """
        async with get_db() as session:
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
                    select("*").where("id" == user_id).table("users")
                )
                user_row = user_result.fetchone()
                if user_row:
                    user_dict = dict(user_row)
                    # Hassas bilgileri çıkar (şifre hash'i gibi)
                    sensitive_fields = ["password_hash"]
                    for field in sensitive_fields:
                        user_dict.pop(field, None)
                    export_data["user_profile"] = user_dict

                # Hikayeler
                stories_result = await session.execute(
                    select("*").where("user_id" == user_id).table("stories")
                )
                stories = stories_result.fetchall()
                export_data["stories"] = [dict(story) for story in stories]

                # Karakterler
                characters_result = await session.execute(
                    select("*").where("user_id" == user_id).table("characters")
                )
                characters = characters_result.fetchall()
                export_data["characters"] = [dict(char) for char in characters]

                # Kullanım istatistikleri (varsa)
                try:
                    stats_result = await session.execute(
                        select("*").where("user_id" == user_id).table("user_statistics")
                    )
                    stats = stats_result.fetchone()
                    if stats:
                        export_data["usage_statistics"] = dict(stats)
                except Exception:
                    # Tablo yoksa sessizce geç
                    pass

                # Abonelik verileri (varsa)
                try:
                    subscription_result = await session.execute(
                        select("*").where("user_id" == user_id).table("subscriptions")
                    )
                    subscription = subscription_result.fetchone()
                    if subscription:
                        export_data["subscription_data"] = dict(subscription)
                except Exception:
                    pass

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
        async with get_db() as session:
            try:
                # 1. Hikayeleri sil (veya anonimleştir)
                await session.execute(
                    delete("stories").where("user_id" == user_id)
                )

                # 2. Karakterleri sil
                await session.execute(
                    delete("characters").where("user_id" == user_id)
                )

                # 3. İstatistikleri sil
                try:
                    await session.execute(
                        delete("user_statistics").where("user_id" == user_id)
                    )
                except Exception:
                    pass

                # 4. Abonelikleri iptal et (silme yerine)
                try:
                    await session.execute(
                        update("subscriptions").where("user_id" == user_id).values(
                            status="cancelled",
                            cancelled_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                except Exception:
                    pass

                # 5. Kullanıcıyı anonimleştir (tam silme yerine)
                # GDPR için verileri anonimleştirmek daha iyidir
                await session.execute(
                    update("users").where("id" == user_id).values(
                        email=f"deleted_{user_id}@anonymous.local",
                        name="Anonymous User",
                        password_hash="",
                        email_verified=False,
                        is_active=False,
                        deleted_at=datetime.utcnow(),
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
        async with get_db() as session:
            try:
                result = await session.execute(
                    select("*").where("user_id" == user_id).table("privacy_settings")
                )
                settings = result.fetchone()

                if settings:
                    return dict(settings)
                else:
                    # Varsayılan ayarlar
                    return {
                        "analytics_consent": True,
                        "marketing_emails": False,
                        "data_sharing": False,
                        "profile_visibility": "private",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
            except Exception:
                # Tablo yoksa varsayılan ayarları döndür
                return {
                    "analytics_consent": True,
                    "marketing_emails": False,
                    "data_sharing": False,
                    "profile_visibility": "private"
                }

    async def update_privacy_settings(self, user_id: str, settings: Dict[str, Any]):
        """
        Kullanıcının gizlilik ayarlarını günceller.
        """
        async with get_db() as session:
            try:
                settings["updated_at"] = datetime.utcnow()

                # Önce mevcut ayarları kontrol et
                existing = await session.execute(
                    select("id").where("user_id" == user_id).table("privacy_settings")
                )
                exists = existing.fetchone()

                if exists:
                    # Güncelle
                    await session.execute(
                        update("privacy_settings").where("user_id" == user_id).values(settings)
                    )
                else:
                    # Yeni oluştur
                    settings["user_id"] = user_id
                    settings["created_at"] = datetime.utcnow()
                    await session.execute(
                        insert("privacy_settings").values(settings)
                    )

                await session.commit()

            except Exception:
                await session.rollback()
                raise

    async def get_data_processing_log(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Kullanıcının veri işleme geçmişini döndürür.
        """
        async with get_db() as session:
            try:
                result = await session.execute(
                    select("*").where("user_id" == user_id)
                    .order_by("created_at DESC")
                    .limit(limit)
                    .offset(offset)
                    .table("data_processing_log")
                )
                logs = result.fetchall()
                return [dict(log) for log in logs]
            except Exception:
                # Tablo yoksa boş liste döndür
                return []

    async def log_data_export(self, user_id: str, export_type: str):
        """
        Veri dışa aktarma işlemini loglar.
        """
        async with get_db() as session:
            try:
                log_entry = {
                    "user_id": user_id,
                    "action": "data_export",
                    "details": json.dumps({"export_type": export_type}),
                    "created_at": datetime.utcnow()
                }
                await session.execute(
                    insert("data_processing_log").values(log_entry)
                )
                await session.commit()
            except Exception:
                # Tablo yoksa sessizce geç
                pass

    async def log_data_deletion(self, user_id: str, reason: str):
        """
        Veri silme işlemini loglar.
        """
        async with get_db() as session:
            try:
                log_entry = {
                    "user_id": user_id,
                    "action": "data_deletion",
                    "details": json.dumps({"reason": reason}),
                    "created_at": datetime.utcnow()
                }
                await session.execute(
                    insert("data_processing_log").values(log_entry)
                )
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
        async with get_db() as session:
            try:
                log_entry = {
                    "user_id": user_id,
                    "action": "consent_withdrawal",
                    "details": json.dumps({"consent_type": consent_type}),
                    "created_at": datetime.utcnow()
                }
                await session.execute(
                    insert("data_processing_log").values(log_entry)
                )
                await session.commit()
            except Exception:
                pass
