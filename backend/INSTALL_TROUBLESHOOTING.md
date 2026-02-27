# 🔧 Kurulum Sorun Giderme Rehberi

## ❌ Tokenizers Rust Hatası

Eğer `tokenizers` paketi kurulurken Rust toolchain hatası alıyorsanız:

### Çözüm 1: Pre-built Wheel Kullan (Önerilen)

```powershell
# Önce tokenizers'i pre-built wheel ile yükle
py -3.12 -m pip install --only-binary :all: tokenizers

# Sonra diğer paketleri yükle
py -3.12 -m pip install -r requirements.txt
```

### Çözüm 2: Tokenizers'i Atlayarak Yükle

Eğer `transformers` kullanmıyorsanız, `tokenizers` opsiyonel olabilir:

```powershell
# Transformers olmadan yükle
py -3.12 -m pip install -r requirements.txt --ignore-installed tokenizers
```

### Çözüm 3: Transformers Versiyonunu Güncelle

Daha yeni `transformers` versiyonu pre-built wheel'ler içerir:

```powershell
py -3.12 -m pip install transformers --upgrade
```

### Çözüm 4: Rust Kur (Opsiyonel)

Eğer gerçekten Rust ile derleme yapmak istiyorsanız:

1. [Rust İndirme Sayfası](https://www.rust-lang.org/tools/install) adresinden Rust'ı kurun
2. Terminali yeniden başlatın
3. Tekrar deneyin: `py -3.12 -m pip install -r requirements.txt`

## ❌ Googletrans Bağımlılık Çakışması

Eğer `googletrans` ve `httpx` arasında bağımlılık çakışması hatası alıyorsanız:

### Sorun:
- `googletrans 4.0.0rc1` → `httpx==0.13.3` gerektirir
- Proje → `httpx>=0.25.1,<0.28.0` gerektirir
- **Çakışma!**

### Çözüm:
`googletrans` zaten `requirements.txt`'den kaldırılmıştır çünkü:
- ✅ `translation_service.py` zaten opsiyonel yapılmış (try-except ile)
- ✅ Diğer çeviri servisleri OpenAI kullanıyor
- ✅ `googletrans` olmadan da uygulama çalışır

### Kurulum:
```powershell
# googletrans olmadan yükle (önerilen)
py -3.12 -m pip install -r requirements.txt
```

## ⚠️ Önemli Notlar

- **Tokenizers hatası kritik değil**: Eğer sadece API endpoint'lerini test ediyorsanız, `transformers` ve `tokenizers` gerekli olmayabilir
- **Googletrans hatası kritik değil**: Çeviri servisleri OpenAI kullanıyor
- **Pre-built wheel'ler**: Python 3.12 için pre-built wheel'ler mevcut olmalı
- **Testler çalışabilir**: Bu paketler olmadan da testler çalışabilir

## ✅ Test Etme

Kurulumdan sonra testleri çalıştırın:

```powershell
py -3.12 -m pytest tests/test_health.py -v
```

Eğer testler çalışıyorsa, `tokenizers` hatası önemli değildir.

## 🔍 Hangi Paketler Gerekli?

### Kritik Paketler (Mutlaka Gerekli):
- `fastapi`
- `uvicorn`
- `pytest`
- `httpx`
- `pydantic`

### Opsiyonel Paketler (AI Özellikleri İçin):
- `transformers` - AI model desteği için
- `tokenizers` - `transformers` bağımlılığı
- `torch` - PyTorch desteği için
- `openai` - OpenAI API için

Eğer sadece API testleri yapıyorsanız, AI paketleri gerekli değildir.

