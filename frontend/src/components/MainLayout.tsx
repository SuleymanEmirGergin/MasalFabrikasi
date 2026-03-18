import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/useAuthStore';
import { 
  LayoutDashboard, 
  BookOpen, 
  Store, 
  Settings, 
  LogOut, 
  Coins,
  Search,
  Menu,
  X,
  Compass,
  BrainCircuit,
  MessageSquare,
  Trophy,
  ShieldCheck,
  MicVocal,
  Library,
  Crown,
  Moon,
  Map,
  Sparkles,
  Lightbulb,
  Lock,
  User,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useLocaleStore, type Locale } from '@/store/useLocaleStore';
import { useTranslation } from '@/hooks/useTranslation';
import { OfflineBanner } from '@/components/OfflineBanner';
import { ScreenTimeMonitor } from './ScreenTimeMonitor';

const SIDEBAR_ITEMS: { icon: React.ComponentType<{ className?: string }>; labelKey: string; path: string }[] = [
  { icon: LayoutDashboard, labelKey: 'nav.home', path: '/' },
  { icon: Map, labelKey: 'nav.storyMap', path: '/story-map' },
  { icon: Compass, labelKey: 'nav.discover', path: '/story' },
  { icon: Trophy, labelKey: 'nav.social', path: '/social' },
  { icon: Sparkles, labelKey: 'nav.magicCanvas', path: '/magic-canvas' },
  { icon: Trophy, labelKey: 'nav.achievements', path: '/gamification' },
  { icon: BrainCircuit, labelKey: 'nav.quiz', path: '/quiz' },
  { icon: ShieldCheck, labelKey: 'nav.parental', path: '/parental' },
  { icon: MicVocal, labelKey: 'nav.voice', path: '/voice-cloning' },
  { icon: Lightbulb, labelKey: 'nav.smartRoom', path: '/smart-room' },
  { icon: Lock, labelKey: 'nav.privacy', path: '/privacy' },
  { icon: Moon, labelKey: 'nav.bedtime', path: '/bedtime' },
  { icon: Map, labelKey: 'nav.interactive', path: '/interactive' },
  { icon: Library, labelKey: 'nav.community', path: '/community' },
  { icon: BookOpen, labelKey: 'nav.create', path: '/create' },
  { icon: MessageSquare, labelKey: 'nav.characters', path: '/characters' },
  { icon: Store, labelKey: 'nav.market', path: '/market' },
  { icon: Settings, labelKey: 'nav.settings', path: '/settings' },
  { icon: User, labelKey: 'nav.profile', path: '/profile' },
];

const BOTTOM_NAV_ITEMS: { icon: React.ComponentType<{ className?: string }>; labelKey: string; path: string }[] = [
  { icon: LayoutDashboard, labelKey: 'nav.home', path: '/' },
  { icon: Map, labelKey: 'nav.storyMap', path: '/story-map' },
  { icon: Sparkles, labelKey: 'nav.magicCanvas', path: '/magic-canvas' },
  { icon: MessageSquare, labelKey: 'nav.characters', path: '/characters' },
  { icon: Settings, labelKey: 'nav.settings', path: '/settings' },
];

export const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { t } = useTranslation();
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);
  const locale = useLocaleStore((state) => state.locale);
  const setLocale = useLocaleStore((state) => state.setLocale);
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => !prev);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  React.useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  return (
    <div className="min-h-screen bg-[#02010a] text-white flex overflow-hidden">
      <OfflineBanner />
      {/* Skip to main content - off-screen until focused (keyboard/screen reader) */}
      <a
        href="#main-content"
        className="absolute left-[-9999px] top-0 z-[100] px-4 py-2 bg-magical-indigo text-white rounded-lg outline-none focus:left-4 focus:top-4 focus:ring-2 focus:ring-white"
      >
        {t('common.skipToContent')}
      </a>

      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 border-r border-white/10 flex-col p-6 space-y-8 h-screen sticky top-0 shrink-0">
        <div className="flex items-center space-x-3 px-2">
          <img src="/logo.png" alt="Masal Fabrikası Icon" className="w-10 h-10 rounded-xl shadow-[0_0_15px_rgba(167,139,250,0.3)] border border-white/10" />
          <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent uppercase tracking-wider">
            FABRİKA
          </span>
        </div>

        <nav className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-2">
          {SIDEBAR_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link 
                key={item.path} 
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all group ${
                  isActive 
                    ? 'bg-magical-indigo/20 text-white border border-magical-indigo/30' 
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <item.icon className={`w-5 h-5 ${isActive ? 'text-magical-indigo' : 'group-hover:text-magical-indigo'}`} />
                <span className="font-medium">{t(item.labelKey)}</span>
              </Link>
            );
          })}
        </nav>

        <div className="pt-6 border-t border-white/10 space-y-4">
          <div className="flex items-center space-x-3 px-4 py-2 bg-magical-rose/10 rounded-xl border border-magical-rose/20">
            <Coins className="w-5 h-5 text-magical-rose shrink-0" />
            <span className="text-sm font-semibold capitalize">500 {t('nav.credits')}</span>
          </div>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-slate-400 hover:text-magical-rose hover:bg-magical-rose/10 px-4 h-12 transition-all rounded-xl"
            onClick={logout}
          >
            <LogOut className="w-5 h-5 mr-3 shrink-0" />
            {t('nav.logout')}
          </Button>
        </div>
      </aside>

      {/* Mobile Sidebar (Drawer) */}
      <div 
        role="presentation"
        aria-hidden={!isMobileMenuOpen}
        className={`fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300 ${isMobileMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={closeMobileMenu}
      />
      <aside 
        aria-label="Menü"
        aria-hidden={!isMobileMenuOpen}
        className={`fixed top-0 left-0 bottom-0 w-72 max-w-[85vw] bg-[#02010a] border-r border-white/10 flex flex-col p-6 space-y-8 z-50 transform transition-transform duration-300 ease-out lg:hidden ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center space-x-3">
            <img src="/logo.png" alt="Icon" className="w-8 h-8 rounded-lg shadow-[0_0_15px_rgba(167,139,250,0.3)]" />
            <span className="text-lg font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent uppercase tracking-wider">
              FABRİKA
            </span>
          </div>
          <Button variant="ghost" size="icon" onClick={closeMobileMenu} className="text-slate-400 hover:text-white hover:bg-white/10">
            <X className="w-6 h-6" />
          </Button>
        </div>

        <nav className="flex-1 overflow-y-auto p-4 space-y-2 relative scrollbar-hide">
          <Link 
            to="/subscription"
            className="flex items-center justify-between p-3 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 mt-1 mb-4 hover:bg-amber-500/20 transition-colors group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="p-1.5 bg-amber-500/20 rounded-lg group-hover:scale-110 transition-transform">
                <Crown className="w-4 h-4 text-amber-500" />
              </div>
              <span className="text-sm font-bold bg-gradient-to-r from-amber-200 to-amber-500 bg-clip-text text-transparent">
                {t('nav.premium')}
              </span>
            </div>
          </Link>
          <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 px-4 mt-6">Tüm Sayfalar</div>
          {SIDEBAR_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            const isAtBottomNav = BOTTOM_NAV_ITEMS.some(b => b.path === item.path);
            if (isAtBottomNav) return null; // Alt barda olanları Drawer'da gizle (opsiyonel ama daha temiz)
            
            return (
              <Link 
                key={item.path} 
                to={item.path}
                onClick={closeMobileMenu}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                  isActive 
                    ? 'bg-magical-indigo/20 text-white border border-magical-indigo/30' 
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <item.icon className={`w-5 h-5 ${isActive ? 'text-magical-indigo' : ''}`} />
                <span className="font-medium text-sm">{t(item.labelKey)}</span>
              </Link>
            );
          })}
        </nav>

        <div className="pt-6 border-t border-white/10 space-y-4 shrink-0">
          <div className="flex items-center justify-between gap-2 px-4">
            <span className="text-xs text-slate-500">{t('nav.language')}</span>
            <Select value={locale} onValueChange={(v) => setLocale(v as Locale)}>
              <SelectTrigger className="w-[72px] h-9 bg-white/5 border-white/10 text-slate-300 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-white/10">
                <SelectItem value="tr" className="text-white focus:bg-white/10">TR</SelectItem>
                <SelectItem value="en" className="text-white focus:bg-white/10">EN</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center space-x-3 px-4 py-3 bg-magical-rose/10 rounded-xl border border-magical-rose/20">
            <Coins className="w-5 h-5 text-magical-rose shrink-0" />
            <span className="text-sm font-semibold">500 {t('nav.credits')}</span>
          </div>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-400/10 px-4 h-12 transition-all rounded-xl"
            onClick={() => { closeMobileMenu(); logout(); }}
          >
            <LogOut className="w-5 h-5 mr-3 shrink-0" />
            {t('nav.logout')}
          </Button>
        </div>
      </aside>

      {/* Mobile Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 h-16 bg-[#02010a]/90 backdrop-blur-xl border-t border-white/10 flex items-center justify-around px-2 z-40 lg:hidden shadow-[0_-10px_20px_rgba(0,0,0,0.5)]">
        {BOTTOM_NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link 
              key={item.path} 
              to={item.path}
              className={`flex flex-col items-center justify-center space-y-1 transition-all flex-1 py-1 rounded-xl ${
                isActive ? 'text-magical-indigo' : 'text-slate-500 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-[10px] font-medium tracking-tight truncate w-full text-center">
                {t(item.labelKey).split(' ').pop()}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Main Content */}
      <main
        id="main-content"
        role="main"
        aria-label={t('common.mainContent')}
        className="flex-1 flex flex-col min-w-0 max-h-screen overflow-y-auto pb-20 lg:pb-0"
      >
        <ScreenTimeMonitor />
        {/* Header */}
        <header className="h-16 md:h-20 border-b border-white/10 px-4 md:px-8 flex items-center justify-between backdrop-blur-md bg-[#02010a]/80 sticky top-0 z-20 shrink-0">
          
          <div className="flex items-center gap-4">
            {/* Mobile Hamburger Button */}
            <Button 
              variant="ghost" 
              size="icon" 
              className="lg:hidden text-slate-300 hover:text-white hover:bg-white/10 shrink-0"
              onClick={toggleMobileMenu}
            >
              <Menu className="w-6 h-6" />
            </Button>
            
            {/* Search Bar - Hidden on very small screens, visible from sm up */}
            <div className="relative w-full max-w-xs md:w-96 hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <Input 
                placeholder={t('nav.searchPlaceholder')} 
                className="pl-10 bg-white/5 border-white/10 focus:border-magical-indigo h-10 md:h-11 transition-all rounded-xl w-full"
              />
            </div>
            {/* Mobile Search Icon Only */}
            <Button variant="ghost" size="icon" className="sm:hidden text-slate-400 hover:text-white shrink-0">
              <Search className="w-5 h-5" />
            </Button>
          </div>

          <div className="flex items-center gap-2 md:gap-4 shrink-0">
            <Select value={locale} onValueChange={(v) => setLocale(v as Locale)}>
              <SelectTrigger className="w-[72px] h-9 bg-white/5 border-white/10 text-slate-300 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-white/10">
                <SelectItem value="tr" className="text-white focus:bg-white/10">TR</SelectItem>
                <SelectItem value="en" className="text-white focus:bg-white/10">EN</SelectItem>
              </SelectContent>
            </Select>
            <Link to="/profile" className="hidden sm:flex flex-col items-end hover:opacity-90 transition-opacity">
              <span className="font-semibold text-sm truncate max-w-[120px]">{user?.name || t('common.user')}</span>
              <span className="text-xs text-slate-500">{t('nav.freePlan')}</span>
            </Link>
            <Link to="/profile" className="w-9 h-9 md:w-10 md:h-10 rounded-full bg-gradient-to-tr from-magical-indigo to-magical-violet border-2 border-white/20 shadow-lg flex items-center justify-center shrink-0 hover:ring-2 hover:ring-magical-indigo/50 transition-all">
              <span className="text-white text-xs font-bold">{user?.name?.charAt(0) || 'M'}</span>
            </Link>
          </div>
        </header>

        {/* Content Area */}
        <div className="p-4 md:p-8 flex-1">
          {children}
        </div>
      </main>
    </div>
  );
};
