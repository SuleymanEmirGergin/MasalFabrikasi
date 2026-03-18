# Güvenlik Taraması (Vulnerability Scan)

Bu doküman, projede düzenli güvenlik taraması yapmak için kullanılacak adımları açıklar.

## 1. Bağımlılık açıkları (pip-audit)

Python paketlerinde bilinen CVE'leri tarar.

```bash
# Kurulum (backend klasöründe)
pip install pip-audit

# Tarama (backend klasöründen)
pip-audit
```

Veya tek komutla:

```bash
cd backend
pip install pip-audit && pip-audit
```

**Çıktı:** Açık bulunan paketler listelenir. Güncelleme önerileri verilir.  
**Hedef:** 0 açık. Çıkan paketleri güncellemek için `pip install -U <paket>` veya `requirements.txt` güncellenir.

## 2. Kod taraması (Bandit)

Python kodunda yaygın güvenlik hatalarını (hardcoded password, unsafe pickle, vb.) arar.

```bash
# Kurulum
pip install bandit

# Backend uygulama kodunu tara (backend klasöründen)
bandit -r app -ll

# Sadece yüksek/orta seviye uyarılar
bandit -r app -ll --severity-level high
```

- `-ll`: Sadece Low ve üzeri (varsayılan: Medium).  
- `-i`: Belirli test ID'lerini atla (false positive için).

## 3. Betik ile tek seferde tarama

Backend içinde güvenlik taramasını tek komutla çalıştırmak için:

```bash
cd backend
python scripts/security_scan.py
```

Bu betik `pip-audit` (ve varsa `bandit`) çalıştırır. Araçlar yüklü değilse kurulum komutlarını yazar.

## 4. CI/CD entegrasyonu

GitHub Actions veya diğer CI'da düzenli tarama için:

- **Bağımlılık:** `pip install pip-audit && pip-audit` (açık varsa fail).
- **Kod:** `pip install bandit && bandit -r app -ll --format json` (opsiyonel; çıktıyı artifact olarak saklayabilirsiniz).

Mevcut `.github/workflows/ci-cd.yml` içine bir job eklenebilir; ihtiyaç halinde ayrı bir `security_scan.yml` da kullanılabilir.

## 5. Ne sıklıkla yapılmalı?

- **pip-audit:** Her release öncesi ve en az ayda bir.
- **Bandit:** Büyük özellik değişikliklerinden sonra veya en az çeyrek dönemde bir.
- **Tam güvenlik denetimi:** Yılda en az bir kez (iç veya dış denetim).

## 6. Bulunan açıklar için akış

1. pip-audit/bandit çıktısını kaydedin.
2. Kritik/yüksek öncelikli maddeleri TODO veya issue olarak işaretleyin.
3. Güncelleme veya patch uygulayın; tekrar tarama yaparak doğrulayın.
4. Değişiklikleri SECURITY.md veya changelog'da kısaca belirtin.

---

*Son güncelleme: Mart 2026*
