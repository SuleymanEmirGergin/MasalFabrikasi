from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import json
from datetime import datetime
import zipfile
import io

from app.services.gdpr_service import GDPRService
from app.core.auth_dependencies import get_current_user

router = APIRouter()

gdpr_service = GDPRService()

@router.get("/data-export", response_class=JSONResponse)
async def export_user_data(current_user: dict = Depends(get_current_user)):
    """
    GDPR Article 15: Kullanıcının kişisel verilerini dışa aktarma hakkı.
    Kullanıcının tüm verilerini JSON formatında döndürür.
    """
    try:
        user_id = current_user["id"]

        # Kullanıcının tüm verilerini topla
        user_data = await gdpr_service.export_user_data(user_id)

        # Export kaydını logla
        await gdpr_service.log_data_export(user_id, "JSON Export")

        return {
            "message": "Verileriniz başarıyla dışa aktarıldı",
            "export_date": datetime.utcnow().isoformat(),
            "data": user_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Veri dışa aktarma sırasında hata oluştu: {str(e)}"
        )

@router.get("/data-export-zip")
async def export_user_data_zip(current_user: dict = Depends(get_current_user)):
    """
    GDPR Article 15: Kullanıcının kişisel verilerini ZIP dosyası olarak dışa aktarma.
    Hassas veriler hariç tüm verileri içerir.
    """
    try:
        user_id = current_user["id"]

        # Kullanıcının tüm verilerini topla
        user_data = await gdpr_service.export_user_data(user_id)

        # JSON verisini string'e çevir
        json_data = json.dumps(user_data, indent=2, ensure_ascii=False, default=str)

        # ZIP dosyası oluştur
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('personal_data.json', json_data)

            # README dosyası ekle
            readme_content = f"""Masal Fabrikası - Kişisel Veri Dışa Aktarma

Dışa Aktarma Tarihi: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Kullanıcı ID: {user_id}

Bu dosya aşağıdaki verileri içerir:
- Kullanıcı profili bilgileri
- Oluşturulan hikayeler
- Karakter bilgileri
- Kullanım istatistikleri
- Abonelik bilgileri (varsa)

GDPR Hakkınız:
Bu veriler GDPR (Genel Veri Koruma Yönetmeliği) kapsamında
size aittir. Bu verileri istediğiniz zaman silebilir veya
güncelleyebilir isteyebilirsiniz.

İletişim: support@masalfabrikasi.com
"""
            zip_file.writestr('README.txt', readme_content)

        zip_buffer.seek(0)

        # Export kaydını logla
        await gdpr_service.log_data_export(user_id, "ZIP Export")

        # ZIP dosyasını döndür
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename=masal_fabrikasi_data_{user_id}_{datetime.utcnow().strftime("%Y%m%d")}.zip'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ZIP veri dışa aktarma sırasında hata oluştu: {str(e)}"
        )

@router.delete("/data-deletion", status_code=202)
async def delete_user_data(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    GDPR Article 17: Kullanıcının kişisel verilerini silme hakkı.
    Kullanıcının tüm verilerini anonimleştirir veya siler.
    """
    try:
        user_id = current_user["id"]

        # Önce veri silme işlemini doğrula (confirmation step)
        # Bu basit implementasyon için doğrudan silme işlemi başlatıyoruz
        # Production'da email confirmation gerekebilir

        # Background task olarak veri silme işlemini başlat
        background_tasks.add_task(gdpr_service.delete_user_data, user_id)

        # Silme isteğini logla
        await gdpr_service.log_data_deletion(user_id, "User Requested Deletion")

        return {
            "message": "Veri silme işlemi başlatıldı. İşlem tamamlandığında email ile bilgilendirileceksiniz.",
            "estimated_completion": "24 saat içinde",
            "request_id": f"del_{user_id}_{int(datetime.utcnow().timestamp())}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Veri silme işlemi başlatılırken hata oluştu: {str(e)}"
        )

@router.get("/privacy-settings")
async def get_privacy_settings(current_user: dict = Depends(get_current_user)):
    """
    Kullanıcının gizlilik ayarlarını döndürür.
    """
    try:
        user_id = current_user["id"]
        settings = await gdpr_service.get_privacy_settings(user_id)

        return {
            "privacy_settings": settings,
            "gdpr_rights": {
                "data_export": "Kişisel verilerinizi istediğiniz zaman dışa aktarabilirsiniz",
                "data_deletion": "Hesabınızı ve verilerinizi istediğiniz zaman silebilirsiniz",
                "data_rectification": "Yanlış verilerinizi düzelttirebilirsiniz",
                "consent_withdrawal": "Veri işleme izninizi istediğiniz zaman geri çekebilirsiniz"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gizlilik ayarları yüklenirken hata oluştu: {str(e)}"
        )

@router.put("/privacy-settings")
async def update_privacy_settings(
    settings_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Kullanıcının gizlilik ayarlarını günceller.
    """
    try:
        user_id = current_user["id"]

        # İzin verilen ayarları kontrol et
        allowed_settings = {
            "analytics_consent",
            "marketing_emails",
            "data_sharing",
            "profile_visibility"
        }

        filtered_settings = {
            k: v for k, v in settings_data.items()
            if k in allowed_settings
        }

        if not filtered_settings:
            raise HTTPException(
                status_code=400,
                detail="Geçersiz gizlilik ayarları"
            )

        await gdpr_service.update_privacy_settings(user_id, filtered_settings)

        return {
            "message": "Gizlilik ayarları güncellendi",
            "updated_settings": filtered_settings
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gizlilik ayarları güncellenirken hata oluştu: {str(e)}"
        )

@router.get("/data-processing-log")
async def get_data_processing_log(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    GDPR Article 15: Veri işleme geçmişini gösterir.
    Kullanıcının verilerinin ne zaman ve nasıl işlendiğini loglar.
    """
    try:
        user_id = current_user["id"]

        processing_log = await gdpr_service.get_data_processing_log(
            user_id, limit=limit, offset=offset
        )

        return {
            "processing_log": processing_log,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(processing_log) == limit
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Veri işleme geçmişi yüklenirken hata oluştu: {str(e)}"
        )

@router.post("/consent-withdrawal")
async def withdraw_consent(
    consent_type: str,
    current_user: dict = Depends(get_current_user)
):
    """
    GDPR Article 7: Veri işleme iznini geri çekme.
    Belirli bir veri işleme iznini geri çeker.
    """
    try:
        user_id = current_user["id"]

        # İzin verilen consent türleri
        valid_consents = {
            "analytics",
            "marketing",
            "personalization",
            "third_party_sharing"
        }

        if consent_type not in valid_consents:
            raise HTTPException(
                status_code=400,
                detail=f"Geçersiz consent türü. Geçerli türler: {', '.join(valid_consents)}"
            )

        await gdpr_service.withdraw_consent(user_id, consent_type)

        return {
            "message": f"{consent_type} consent başarıyla geri çekildi",
            "consent_type": consent_type,
            "withdrawn_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Consent geri çekme sırasında hata oluştu: {str(e)}"
        )
