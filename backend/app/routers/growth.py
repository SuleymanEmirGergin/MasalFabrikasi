from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Waitlist, UserProfile, Story
from pydantic import EmailStr, BaseModel
from typing import Optional
import uuid
import random
import string

router = APIRouter(tags=["Growth & Referrals"])

@router.get("/ping")
async def growth_ping():
    return {"status": "growth_active", "version": "2.0.4"}

@router.get("/alembic-status")
async def check_alembic_status():
    import subprocess
    try:
        result = subprocess.run(["alembic", "current"], capture_output=True, text=True, check=True)
        return {"status": "success", "current": result.stdout}
    except Exception as e:
        return {"status": "error", "error": str(e), "output": getattr(e, 'stderr', 'No stderr')}

@router.get("/story-origin")
async def get_story_origin():
    try:
        import inspect
        origin = inspect.getfile(Story)
        attrs = [a for a in dir(Story) if not a.startswith("__")]
        return {
            "origin": origin,
            "has_share_token": hasattr(Story, "share_token"),
            "attributes": attrs
        }
    except Exception as e:
        return {"error": str(e)}

class WaitlistCreate(BaseModel):
    email: EmailStr
    source: Optional[str] = "landing_page"

@router.post("/waitlist", status_code=status.HTTP_201_CREATED)
async def join_waitlist(data: WaitlistCreate, db: Session = Depends(get_db)):
    """Landing page'den gelen abonelikleri kaydeder."""
    existing = db.query(Waitlist).filter(Waitlist.email == data.email).first()
    if existing:
        return {"message": "Zaten listedesin!", "email": data.email}
    
    new_entry = Waitlist(
        email=data.email,
        source=data.source
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "Başarıyla eklendi!", "id": str(new_entry.id)}

@router.post("/referral/generate")
async def generate_referral_code(user_auth_id: str, db: Session = Depends(get_db)):
    """Kullanıcı için benzersiz bir referans kodu oluşturur."""
    profile = db.query(UserProfile).filter(UserProfile.auth_user_id == user_auth_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Kullanıcı profili bulunamadı")
    
    if profile.referral_code:
        return {"referral_code": profile.referral_code}
    
    # Basit ama benzersiz kod üretimi
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Çakışma kontrolü
    while db.query(UserProfile).filter(UserProfile.referral_code == code).first():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
    profile.referral_code = code
    db.commit()
    return {"referral_code": code}

@router.get("/referral/stats")
async def get_referral_stats(user_auth_id: str, db: Session = Depends(get_db)):
    """Kullanıcının referans istatistiklerini getirir."""
    profile = db.query(UserProfile).filter(UserProfile.auth_user_id == user_auth_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Kullanıcı profili bulunamadı")
    
    if not profile.referral_code:
        return {"referrals_count": 0, "referral_code": None}
    
    count = db.query(UserProfile).filter(UserProfile.referred_by == profile.referral_code).count()
    return {
        "referral_code": profile.referral_code,
        "referrals_count": count,
        "reward_credits": count * 5  # Her referans için 5 kredi (örnek)
    }
@router.post("/story/share/{story_id}")
async def share_story(story_id: str, db: Session = Depends(get_db)):
    """Masal için paylaşım linki (token) oluşturur."""
    from app.models import Story
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Masal bulunamadı")
    
    if not story.share_token:
        # Benzersiz kısa token oluştur (örnek: 12 karakter)        
        story.share_token = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        story.is_public = True
        db.commit()
        db.refresh(story)
    
    return {
        "share_token": story.share_token,
        "public_url": f"https://masalfabrikasi.ai/shared/{story.share_token}"
    }

@router.get("/story/public/{token}")
async def get_public_story(token: str, db: Session = Depends(get_db)):
    """Token üzerinden masalı herkese açık olarak getirir."""
    from app.models import Story
    story = db.query(Story).filter(Story.share_token == token, Story.is_public == True).first()
    if not story:
        raise HTTPException(status_code=404, detail="Masal bulunamadı veya paylaşım süresi dolmuş")
    
    # Görüntülenme sayısını artır (opsiyonel)
    story.view_count += 1
    db.commit()
    
    return {
        "title": story.title,
        "story_text": story.story_text,
        "image_url": story.image_url,
        "audio_url": story.audio_url,
        "theme": story.theme,
        "created_at": story.created_at
    }
@router.get("/story/view/{token}", response_class=HTMLResponse)
async def view_public_story(token: str, db: Session = Depends(get_db)):
    """WhatsApp/Instagram paylaşımı için masalın web önizleme sayfasını döner."""
    try:
        story = db.query(Story).filter(Story.share_token == token, Story.is_public == True).first()
        if not story:
            return HTMLResponse(content="<h1>Masal bulunamadı</h1>", status_code=404)
        
        # Open Graph meta etiketleri ile zenginleştirilmiş HTML
        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{story.title} - Masal Fabrikası</title>
            
            <!-- Open Graph Meta Etiketleri -->
            <meta property="og:title" content="{story.title} - Masal Fabrikası">
            <meta property="og:description" content="AI ile üretilen bu harika masalı oku: {story.theme[:100]}...">
            <meta property="og:image" content="{story.image_url}">
            <meta property="og:url" content="https://masalfabrikasi.ai/shared/{token}">
            <meta property="og:type" content="article">
            
            <!-- Twitter Card -->
            <meta name="twitter:card" content="summary_large_image">
            <meta name="twitter:title" content="{story.title}">
            <meta name="twitter:description" content="Yapay zeka ile çocuğunuza özel masallar üretin.">
            <meta name="twitter:image" content="{story.image_url}">

            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Outfit', sans-serif; }}
                .story-container {{ 
                    background: linear-gradient(to bottom, #fef2f2, #ffffff);
                }}
            </style>
        </head>
        <body class="bg-gray-50">
            <div class="max-w-2xl mx-auto min-h-screen story-container shadow-xl overflow-hidden">
                <!-- Header -->
                <div class="p-6 bg-white border-b border-gray-100 flex justify-between items-center">
                    <div class="flex items-center gap-2 font-bold text-indigo-600">
                        <span>✨ Masal Fabrikası</span>
                    </div>
                    <a href="https://masalfabrikasi.ai" class="text-xs bg-indigo-600 text-white px-3 py-1.5 rounded-full font-bold">Uygulamayı İndir</a>
                </div>

                <!-- Content -->
                <div class="p-8 space-y-8">
                    <img src="{story.image_url}" class="w-full h-80 object-cover rounded-3xl shadow-lg border-4 border-white" alt="Masal Görseli">
                    
                    <div class="text-center space-y-4">
                        <h1 class="text-4xl font-extrabold text-gray-900 leading-tight">{story.title}</h1>
                        <div class="inline-block px-4 py-1 bg-indigo-50 text-indigo-600 rounded-full text-sm font-bold tracking-wide uppercase">
                             {(story.language or 'tr').upper()} MASAL
                        </div>
                    </div>

                    <div class="prose prose-indigo max-w-none">
                        <p class="text-xl text-gray-700 leading-relaxed whitespace-pre-wrap">{story.story_text}</p>
                    </div>
                </div>

                <!-- CTA Footer -->
                <div class="p-10 bg-indigo-600 text-white text-center space-y-6">
                    <h2 class="text-2xl font-bold">Kendi Masalını Üretmek İster Misin?</h2>
                    <p class="text-indigo-100 opacity-80">Çocuğunun kahramanı olduğu sınırsız masallar dünyasına katıl.</p>
                    <div class="flex justify-center gap-4">
                        <a href="#" class="bg-white text-indigo-600 px-8 py-3 rounded-2xl font-bold shadow-lg hover:scale-105 transition">Hemen Başla</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Hata: {str(e)}</h1>", status_code=500)

@router.post("/waitlist/invite")
async def invite_waitlist_user(email: str, db: Session = Depends(get_db)):
    """Waitlist'deki bir kullanıcıya özel davetiye tanımlar."""
    entry = db.query(Waitlist).filter(Waitlist.email == email).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Email bekleme listesinde bulunamadı")
    
    # Davet kodu üret ve durumu güncelle
    invite_code = "MF-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    entry.meta_data = {**entry.meta_data, "invite_code": invite_code, "is_invited": True}
    db.commit()
    
    return {
        "status": "success",
        "message": f"{email} için davetiye oluşturuldu.",
        "invite_code": invite_code
    }

@router.get("/waitlist/verify/{email}")
async def verify_invite(email: str, db: Session = Depends(get_db)):
    """Email'in davet edilip edilmediğini kontrol eder."""
    entry = db.query(Waitlist).filter(Waitlist.email == email).first()
    if not entry:
        return {"is_invited": False, "message": "Email listede yok"}
    
    is_invited = entry.meta_data.get("is_invited", False)
    return {
        "is_invited": is_invited,
        "invite_code": entry.meta_data.get("invite_code") if is_invited else None
    }
