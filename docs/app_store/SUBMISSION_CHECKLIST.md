# App Store Submission Checklist

## 🛠️ Technical Checks

- [ ] **Versioning:** `versionString` ve `buildNumber` güncellendi mi? (app.json)
- [ ] **Icons:** Tüm platformlar için uygulama ikonları doğru boyutlarda mı?
- [ ] **Splash Screen:** Açılış ekranı görselleri hazır mı?
- [ ] **Sign-in:** Apple ile Giriş (Sign in with Apple) entegre edildi mi? (iOS zorunlu)
- [ ] **Performance:** Uygulama açılış hızı ve bellek kullanımı optimize edildi mi?
- [ ] **Size:** Uygulama boyutu limitler dahilinde mi?
- [ ] **Offline Mode:** İnternet yokken uygulama çöküyor mu? (Graceful degradation)

## ⚖️ Legal & Compliance

- [ ] **Privacy Policy:** Geçerli bir URL eklendi mi?
- [ ] **Terms of Service:** EULA veya kullanım şartları eklendi mi?
- [ ] **Data Safety Form:** Play Store veri güvenliği formu dolduruldu mu?
- [ ] **App Privacy Details:** App Store gizlilik etiketleri (nutrition labels) belirlendi mi?
- [ ] **Delete Account:** Uygulama içinde hesabı silme seçeneği var mı? (Zorunlu)

## 🧪 Testing

- [ ] **IAP Testing:** Satın almalar Sandbox/TestFlight ortamında test edildi mi?
- [ ] **Restoring Purchases:** "Satın Almaları Geri Yükle" butonu çalışıyor mu?
- [ ] **IPv6:** Uygulama IPv6 ağlarında çalışıyor mu? (App Store reddi sebebi)
- [ ] **Tablet:** iPad/Tablet düzeni bozuk mu?
- [ ] **Dark Mode:** Karanlık modda okunabilirlik sorunu var mı?

## 📢 Assets & Metadata

- [ ] **Screenshots:** Tüm ekran boyutları için ekran görüntüleri hazır mı?
- [ ] **Preview Video:** (Opsiyonel) Tanıtım videosu hazır mı?
- [ ] **Description:** Açıklama metni yazım hatalarından arındırıldı mı?
- [ ] **Keywords:** Arama terimleri optimize edildi mi?
- [ ] **Support URL:** Destek sayfası erişilebilir mi?

## 🚀 Final Steps

1.  **iOS:** Xcode -> Archive -> Distribute App -> TestFlight -> App Store Connect
2.  **Android:** Build Bundle (.aab) -> Upload to Play Console -> Alpha/Beta -> Production
