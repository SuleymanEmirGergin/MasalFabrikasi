# 🚀 Masal Fabrikası - Future Roadmap

This document outlines planned improvements and features for upcoming releases.

---

## 📱 v1.1.0 - Push Notifications & Engagement

**Target:** Q1 2026

### Features
- [ ] Push notification infrastructure (Expo Notifications)
- [ ] Daily story reminders
- [ ] New content alerts
- [ ] Personalized recommendations based on reading history

### Technical
- [ ] Configure Firebase Cloud Messaging (FCM) — opsiyonel; backend Expo Push API kullanıyor
- [x] Backend notification service (Expo Push API; bkz. [NOTIFICATIONS_SETUP.md](NOTIFICATIONS_SETUP.md))
- [ ] User notification preferences
- **Not:** Backend hazır (Expo Push API); mobil tarafta Expo Notifications + token kaydı yapılacak.

---

## 🌍 v1.2.0 - Multi-Language Support

**Target:** Q2 2026

### Features
- [ ] English language stories
- [ ] German language stories
- [ ] Language switcher in settings
- [ ] Localized UI (i18n)

### Technical
- [ ] i18next integration
- [ ] Translation management system
- [ ] RTL support preparation

---

## 👨‍👩‍👧‍👦 v1.3.0 - Family Features

**Target:** Q2 2026

### Features
- [ ] Family accounts (up to 5 profiles)
- [ ] Child profiles with age-appropriate content
- [ ] Parental controls
- [ ] Reading progress tracking per child

### Technical
- [ ] Profile management API
- [ ] Content filtering by age
- [ ] Session management for multiple users

---

## 💎 v1.4.0 - Premium Tiers & Monetization

**Target:** Q3 2026

### Features
- [ ] Free tier (3 stories/day)
- [ ] Premium tier (unlimited stories, no ads)
- [ ] Pro tier (video generation, voice cloning)
- [ ] In-app purchase flows

### Technical
- [ ] Stripe subscription integration
- [ ] Usage tracking and limits
- [ ] Premium content gating
- **Mevcut:** iyzico (TR) ve Stripe entegrasyonları backend'de hazır; akış ve URL'ler için bkz. [PAYMENTS_INTEGRATION.md](PAYMENTS_INTEGRATION.md).

---

## ⚡ v1.5.0 - Performance & Optimization

**Target:** Q3 2026

### Features
- [ ] Faster app startup
- [ ] Reduced bundle size
- [ ] Improved image loading
- [ ] Better offline experience

### Technical
- [ ] Lazy loading for screens
- [ ] Image compression (WebP)
- [ ] Code splitting
- [ ] SQLite for offline storage
- [ ] Background sync

---

## 🎨 v2.0.0 - AI Enhancements

**Target:** Q4 2026

### Features
- [ ] Interactive story choices (branching narratives)
- [ ] Custom character creation
- [ ] Voice cloning for personalized narration
- [ ] Real-time story collaboration

### Technical
- [ ] Advanced prompt engineering
- [ ] Voice cloning API integration
- [ ] WebSocket for real-time features

---

## 📊 Analytics & Monitoring

**Ongoing**

- [ ] User behavior dashboards
- [ ] A/B testing framework
- [ ] Crash reporting (Sentry)
- [ ] Performance monitoring
- [ ] Funnel analysis

---

## 🔒 Security & Compliance

**Ongoing**

- [ ] Regular security audits
- [ ] GDPR compliance updates
- [ ] COPPA compliance maintenance
- [ ] Data encryption at rest
- [ ] API rate limiting improvements

---

## Contributing Ideas

Have a feature idea? Open an issue on GitHub with the `enhancement` label, or discuss in our community channels.

---

*Last updated: January 7, 2026*
