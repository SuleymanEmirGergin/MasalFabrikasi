import asyncio
import os
import sys
from dotenv import load_dotenv

# Root dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# .env dosyasını yükle
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from app.services.wiro_client import wiro_client
from app.core.config import settings

async def user_playground():
    print("🌟 Masal Fabrikası AI Playground'a Hoş Geldiniz!")
    print("-" * 50)
    
    # Kısayol: Test etmek istediğiniz özellikleri 'True' yapın
    TEST_STORY = True
    TEST_IMAGE = True
    TEST_VIDEO = True
    
    # 1. Hikaye Testi (LLM)
    if TEST_STORY:
        print("\n📝 [1/3] Hikaye Oluşturma Test Ediliyor (GPT-OSS)...")
        prompt = "Cesur bir karıncanın dev bir elma ile olan macerası."
        try:
            result = await wiro_client.run_and_wait(
                provider="openai",
                model_slug="gpt-oss-20b",
                inputs={"prompt": prompt, "max_tokens": 150},
                is_json=True
            )
            detail = result.get('detail') or {}
            task_list = detail.get('tasklist', [])
            status = task_list[0].get('status', 'Bilinmiyor') if task_list else 'Gorev Beklemede'
            
            if status != 'Bilinmiyor':
                print(f"✅ Hikaye Goresi Tamamland/Durumu: {status}")
            else:
                errors = result.get('run_response', {}).get('errors', [])
                if errors:
                    print(f"⚠️ Wiro Hatasi: {errors[0].get('message')}")
                else:
                    print("✅ Hikaye Basariyla Kuyruga Alindi.")

        except Exception as e:
            print(f"❌ Hikaye Hatasi: {e}")

    # 2. Görsel Testi (Imagen)
    if TEST_IMAGE:
        print(f"\n🖼️ [2/3] Görsel Oluşturma Test Ediliyor ({settings.IMAGEN_FAST_MODEL})...")
        prompt = "A brave ant carrying a giant red apple, cinematic lighting, 3d render"
        try:
            parts = settings.IMAGEN_FAST_MODEL.split("/")
            provider = parts[0] if len(parts) > 1 else "google"
            model_slug = parts[1] if len(parts) > 1 else parts[0]

            result = await wiro_client.run_and_wait(
                provider=provider,
                model_slug=model_slug,
                inputs={"prompt": prompt},
                is_json=True
            )
            detail = result.get('detail') or {}
            task_list = detail.get('tasklist', [])
            status = task_list[0].get('status', 'Bilinmiyor') if task_list else 'Gorev Beklemede'

            if task_list:
                print(f"✅ Görsel Durumu: {status}")
            else:
                run_resp = result.get('run_response', {})
                errors = run_resp.get('errors', [])
                if errors:
                    print(f"⚠️ Wiro Hatasi: {errors[0].get('message')}")
                    if errors[0].get('message') == 'tool-not-accessible':
                         print("💡 İpucu: Bu model (Imagen) Wiro Dashboard'unuzda aktif olmayabilir veya yetkiniz yoktur.")
                else:
                    print("✅ Görsel Basariyla Kuyruga Alindi.")

        except Exception as e:
            print(f"❌ Görsel Hatası: {e}")

    # 3. Video Testi (Sora-2)
    if TEST_VIDEO:
        print("\n🎬 [3/3] Video Oluşturma Test Ediliyor (Sora-2)...")
        prompt = "A small ant lifting a giant apple and walking slowly."
        try:
            result = await wiro_client.run_and_wait(
                provider="openai",
                model_slug="sora-2",
                inputs={"prompt": prompt, "seconds": "4"},
                is_json=False
            )
            detail = result.get('detail') or {}
            task_list = detail.get('tasklist', [])
            status = task_list[0].get('status', 'Bilinmiyor') if task_list else 'Gorev Beklemede'

            if task_list:
              print(f"✅ Video Durumu: {status}")
            else:
                errors = result.get('run_response', {}).get('errors', [])
                if errors:
                    print(f"⚠️ Wiro Hatasi: {errors[0].get('message')}")
                else:
                    print("✅ Video Basariyla Kuyruga Alindi.")
        except Exception as e:
            print(f"❌ Video Hatası: {e}")

    print("\n" + "-" * 50)
    print("🚀 Testler tamamlandı! Dashboard'dan (api.wiro.ai) süreçleri takip edebilirsiniz.")

if __name__ == "__main__":
    asyncio.run(user_playground())
