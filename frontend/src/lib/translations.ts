export type Locale = 'tr' | 'en';

type Translations = {
  common: {
    save: string;
    cancel: string;
    loading: string;
    error: string;
    or: string;
    user: string;
    offline: string;
    backOnline: string;
    skipToContent: string;
    mainContent: string;
  };
  login: {
    title: string;
    subtitle: string;
    email: string;
    emailPlaceholder: string;
    password: string;
    passwordPlaceholder: string;
    passwordMin: string;
    nameOptional: string;
    namePlaceholder: string;
    signIn: string;
    signInLoading: string;
    signUp: string;
    signUpLoading: string;
    forgotPassword: string;
    forgotPasswordHint: string;
    forgotPasswordSend: string;
    forgotPasswordSending: string;
    forgotPasswordSuccess: string;
    backToSignIn: string;
    noAccount: string;
    hasAccount: string;
    demoContinue: string;
    invalidCredentials: string;
    signUpError: string;
    emailRequired: string;
    passwordTooShort: string;
    emailNotFound: string;
    emailSendFailed: string;
    emailAlreadyInUse: string;
  };
  profile: {
    title: string;
    subtitle: string;
    name: string;
    email: string;
    logout: string;
  };
  nav: {
    home: string;
    discover: string;
    social: string;
    magicCanvas: string;
    achievements: string;
    quiz: string;
    parental: string;
    voice: string;
    smartRoom: string;
    privacy: string;
    bedtime: string;
    interactive: string;
    community: string;
    create: string;
    characters: string;
    market: string;
    settings: string;
    profile: string;
    premium: string;
    credits: string;
    logout: string;
    language: string;
    searchPlaceholder: string;
    freePlan: string;
    storyMap: string;
  };
  dashboard: {
    welcome: string;
    welcomeName: string;
    todayQuestion: string;
    myStories: string;
    myCharacters: string;
    magicPoints: string;
    recentDrafts: string;
    startNewStory: string;
    startNewStoryDesc: string;
    startMagic: string;
    recentStories: string;
    magicStats: string;
    createdAgo: string;
    storyTitleExample: string;
    recentStoryDateExample: string;
    statsPlaceholder: string;
  };
};

const tr: Translations = {
  common: {
    save: 'Kaydet',
    cancel: 'İptal',
    loading: 'Yükleniyor...',
    error: 'Hata',
    or: 'Veya',
    user: 'Kullanıcı',
    offline: 'Çevrimdışısınız. Bazı özellikler kullanılamayabilir.',
    backOnline: 'Bağlantı yeniden kuruldu.',
    skipToContent: 'İçeriğe atla',
    mainContent: 'Ana içerik',
  },
  login: {
    title: 'Masal Fabrikası',
    subtitle: 'Hayal gücünüzün sınırlarını AI ile keşfedin',
    email: 'E-posta',
    emailPlaceholder: 'isim@örnek.com',
    password: 'Şifre',
    passwordPlaceholder: '••••••••',
    passwordMin: 'En az 6 karakter',
    nameOptional: 'Ad (isteğe bağlı)',
    namePlaceholder: 'Adınız',
    signIn: 'Giriş Yap',
    signInLoading: 'Giriş yapılıyor...',
    signUp: 'Kayıt Ol',
    signUpLoading: 'Hesap oluşturuluyor...',
    forgotPassword: 'Şifremi unuttum',
    forgotPasswordHint: 'E-posta adresinizi girin, size şifre sıfırlama bağlantısı göndereceğiz.',
    forgotPasswordSend: 'Sıfırlama bağlantısı gönder',
    forgotPasswordSending: 'Gönderiliyor...',
    forgotPasswordSuccess: 'Şifre sıfırlama e-postası gönderildi. Gelen kutunuzu kontrol edin.',
    backToSignIn: 'Girişe dön',
    noAccount: 'Hesabınız yok mu? Kayıt olun',
    hasAccount: 'Zaten hesabınız var mı? Giriş yapın',
    demoContinue: 'Demo Hesabı ile Devam Et',
    invalidCredentials: 'E-posta veya şifre hatalı.',
    signUpError: 'Kayıt oluşturulamadı.',
    emailRequired: 'Lütfen e-posta adresinizi girin.',
    passwordTooShort: 'Şifre en az 6 karakter olmalıdır.',
    emailNotFound: 'Bu e-posta ile kayıtlı hesap bulunamadı.',
    emailSendFailed: 'E-posta gönderilemedi.',
    emailAlreadyInUse: 'Bu e-posta adresi zaten kullanılıyor.',
  },
  profile: {
    title: 'Profilim',
    subtitle: 'Hesap bilgileriniz',
    name: 'Ad',
    email: 'E-posta',
    logout: 'Çıkış Yap',
  },
  nav: {
    home: 'Ana Sayfa',
    discover: 'Hikayeleri Keşfet',
    social: 'Sosyal & Liderlik',
    magicCanvas: 'Büyülü Tuval',
    achievements: 'Kazanımlar',
    quiz: 'Eğlenceli Sınavlar',
    parental: 'Ebeveyn Paneli',
    voice: 'Sihirli Seslendirme',
    smartRoom: 'Akıllı Oda',
    privacy: 'Gizlilik Merkezi',
    bedtime: 'Uyku Vakti',
    interactive: 'İnteraktif Hikayeler',
    community: 'Topluluk Kütüphanesi',
    create: 'Sihirli Yazıcı',
    characters: 'Karakterler',
    market: 'Pazar Yeri',
    settings: 'Ayarlar',
    profile: 'Profilim',
    premium: "Premium'a Geç",
    credits: 'Kredi',
    logout: 'Çıkış Yap',
    language: 'Dil',
    searchPlaceholder: 'Masal veya karakter ara...',
    freePlan: 'Ücretsiz Plan',
    storyMap: 'Masal Diyarı',
  },
  dashboard: {
    welcome: 'Hoş Geldin',
    welcomeName: 'Emir',
    todayQuestion: 'Bugün hangi macerayı yazmak istersin?',
    myStories: 'Masallarım',
    myCharacters: 'Karakterlerim',
    magicPoints: 'Sihirli Puan',
    recentDrafts: 'Son Taslaklar',
    startNewStory: 'Yeni Bir Masala Başla',
    startNewStoryDesc: 'Karakterlerini seç, dünyanı belirle ve yapay zeka senin için eşsiz bir hikaye, görseller ve seslendirme oluştursun.',
    startMagic: 'Sihri Başlat',
    recentStories: 'Son Masallarım',
    magicStats: 'Sihirli İstatistikler',
    createdAgo: 'gün önce oluşturuldu',
    storyTitleExample: 'Kayıp Ejderhanın Sırrı',
    recentStoryDateExample: '2 gün önce oluşturuldu',
    statsPlaceholder: 'Burada masal üretim grafikleri yer alacak.',
  },
};

const en: Translations = {
  common: {
    save: 'Save',
    cancel: 'Cancel',
    loading: 'Loading...',
    error: 'Error',
    or: 'Or',
    user: 'User',
    offline: "You're offline. Some features may be unavailable.",
    backOnline: 'Connection restored.',
    skipToContent: 'Skip to main content',
    mainContent: 'Main content',
  },
  login: {
    title: 'Story Factory',
    subtitle: 'Explore the limits of your imagination with AI',
    email: 'Email',
    emailPlaceholder: 'name@example.com',
    password: 'Password',
    passwordPlaceholder: '••••••••',
    passwordMin: 'At least 6 characters',
    nameOptional: 'Name (optional)',
    namePlaceholder: 'Your name',
    signIn: 'Sign In',
    signInLoading: 'Signing in...',
    signUp: 'Sign Up',
    signUpLoading: 'Creating account...',
    forgotPassword: 'Forgot password',
    forgotPasswordHint: 'Enter your email and we’ll send you a password reset link.',
    forgotPasswordSend: 'Send reset link',
    forgotPasswordSending: 'Sending...',
    forgotPasswordSuccess: 'Password reset email sent. Check your inbox.',
    backToSignIn: 'Back to sign in',
    noAccount: "Don't have an account? Sign up",
    hasAccount: 'Already have an account? Sign in',
    demoContinue: 'Continue with Demo',
    invalidCredentials: 'Invalid email or password.',
    signUpError: 'Could not create account.',
    emailRequired: 'Please enter your email address.',
    passwordTooShort: 'Password must be at least 6 characters.',
    emailNotFound: 'No account found with this email.',
    emailSendFailed: 'Could not send email.',
    emailAlreadyInUse: 'This email is already in use.',
  },
  profile: {
    title: 'My Profile',
    subtitle: 'Your account information',
    name: 'Name',
    email: 'Email',
    logout: 'Sign Out',
  },
  nav: {
    home: 'Home',
    discover: 'Discover Stories',
    social: 'Social & Leaderboard',
    magicCanvas: 'Magic Canvas',
    achievements: 'Achievements',
    quiz: 'Fun Quizzes',
    parental: 'Parent Panel',
    voice: 'Magic Voice',
    smartRoom: 'Smart Room',
    privacy: 'Privacy Center',
    bedtime: 'Bedtime',
    interactive: 'Interactive Stories',
    community: 'Community Library',
    create: 'Story Creator',
    characters: 'Characters',
    market: 'Marketplace',
    settings: 'Settings',
    profile: 'My Profile',
    premium: 'Go Premium',
    credits: 'Credits',
    logout: 'Sign Out',
    language: 'Language',
    searchPlaceholder: 'Search stories or characters...',
    freePlan: 'Free Plan',
    storyMap: 'Story Map',
  },
  dashboard: {
    welcome: 'Welcome',
    welcomeName: 'Emir',
    todayQuestion: 'What adventure do you want to write today?',
    myStories: 'My Stories',
    myCharacters: 'My Characters',
    magicPoints: 'Magic Points',
    recentDrafts: 'Recent Drafts',
    startNewStory: 'Start a New Story',
    startNewStoryDesc: 'Choose your characters, set your world, and let AI create a unique story, images, and narration for you.',
    startMagic: 'Start Magic',
    recentStories: 'My Recent Stories',
    magicStats: 'Magic Stats',
    createdAgo: 'days ago',
    storyTitleExample: 'The Secret of the Lost Dragon',
    recentStoryDateExample: 'Created 2 days ago',
    statsPlaceholder: 'Story production charts will appear here.',
  },
};

export const translations: Record<Locale, Translations> = { tr, en };

/** Get nested value by path e.g. "login.title" */
function getByPath(obj: Record<string, unknown>, path: string): string | undefined {
  const keys = path.split('.');
  let current: unknown = obj;
  for (const key of keys) {
    if (current == null || typeof current !== 'object') return undefined;
    current = (current as Record<string, unknown>)[key];
  }
  return typeof current === 'string' ? current : undefined;
}

export function getTranslation(locale: Locale, key: string): string {
  const value = getByPath(translations[locale] as unknown as Record<string, unknown>, key);
  return value ?? key;
}
