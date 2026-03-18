# Changelog

All notable changes to the Masal Fabrikası project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-07

### 🎉 Initial Release

First production release of Masal Fabrikası - AI-powered Turkish story generator for children.

### Added

- **AI Story Generation**
  - Multi-provider AI integration (Gemini, GPT, Wiro)
  - Turkish language optimized story creation
  - Age-appropriate content filtering (3-12 years)
  - Multiple story themes and characters

- **Media Generation**
  - AI-generated story illustrations (Google Imagen)
  - Text-to-speech narration (Turkish voices)
  - Video generation for story scenes

- **User Features**
  - Supabase authentication (Email, Google, Apple)
  - Story library and favorites
  - Share stories as PDF/images
  - Offline story access

- **Infrastructure**
  - Railway backend deployment (FastAPI + PostgreSQL + Redis)
  - Celery async task processing
  - EAS Build CI/CD pipeline
  - Comprehensive health monitoring

### Technical Stack

- **Frontend**: React Native (Expo SDK 52)
- **Backend**: FastAPI, SQLAlchemy, Celery
- **Database**: PostgreSQL, Redis
- **AI**: Gemini, GPT-OSS, Google Imagen
- **Auth**: Supabase
- **Deployment**: Railway, EAS Build

---

## [Unreleased]

### Planned

- Push notifications for new stories
- Enhanced analytics dashboard
- Multi-language support (English, German)
- Family sharing features
- Premium subscription tiers
- Performance optimizations (lazy loading, image compression)

---

## Version History

| Version | Date       | Description              |
|---------|------------|--------------------------|
| 1.0.0   | 2026-01-07 | Initial production release |

---

## Contributing

When adding to this changelog:

1. Add changes under `[Unreleased]` section
2. Use categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
3. Keep entries concise but descriptive
4. Include issue/PR references when applicable

## Release Process

1. Update version in `package.json` and `app.json`
2. Move `[Unreleased]` items to new version section
3. Update version history table
4. Commit with message: `chore: release vX.Y.Z`
5. Tag release: `git tag vX.Y.Z`
