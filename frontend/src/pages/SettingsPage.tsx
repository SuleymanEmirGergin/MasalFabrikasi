import { 
  User, 
  Settings2, 
  Bell, 
  ShieldCheck, 
  Moon, 
  Sun,
  Smartphone,
  LogOut,
  Gem,
  Crown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuthStore } from '@/store/useAuthStore';
import { useThemeStore } from '@/store/useThemeStore';
import { useParentalStore } from '@/store/useParentalStore';
import { useState } from 'react';
import api from '@/api/client';

export const SettingsPage = () => {
  const user = useAuthStore((state) => state.user);
  const updateUser = useAuthStore((state) => state.updateUser);
  const logout = useAuthStore((state) => state.logout);
  const { theme, setTheme } = useThemeStore();
  const { 
    pin, setPin, 
    notificationsEnabled, setNotificationsEnabled,
    weeklyReportEnabled, setWeeklyReportEnabled 
  } = useParentalStore();
  
  const [activeTab, setActiveTab] = useState('profile');
  const [displayName, setDisplayName] = useState(user?.name || '');
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<{ type: 'success' | 'error', msg: string } | null>(null);

  const handleSaveProfile = async () => {
    if (!displayName.trim()) return;
    setIsSaving(true);
    setSaveStatus(null);
    try {
      await api.put('/users/profile', { name: displayName });
      updateUser({ name: displayName });
      setSaveStatus({ type: 'success', msg: 'Profil başarıyla güncellendi!' });
    } catch (err: any) {
      console.error(err);
      setSaveStatus({ type: 'error', msg: 'Güncelleme sırasında bir hata oluştu.' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-magical-violet to-magical-rose bg-clip-text text-transparent flex items-center">
          <Settings2 className="w-8 h-8 mr-3 text-magical-violet" />
          Hesap Ayarları
        </h1>
        <p className="text-slate-400 mt-1">
          Profil bilgilerinizi düzenleyin, tercihlerinizi yönetin ve sihirli aboneliğinizi kontrol edin.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        
        {/* Sidebar Nav */}
        <aside className="w-full md:w-64 space-y-2 flex-shrink-0">
          {[
            { id: 'profile', label: 'Profil Bilgileri', icon: User },
            { id: 'subscription', label: 'Abonelik & Kredi', icon: Gem },
            { id: 'preferences', label: 'Tercihler', icon: Moon },
            { id: 'notifications', label: 'Bildirimler', icon: Bell },
            { id: 'security', label: 'Güvenlik', icon: ShieldCheck },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === item.id 
                  ? 'bg-magical-violet/20 text-white border border-magical-violet/30 shadow-[0_0_15px_rgba(167,139,250,0.15)]' 
                  : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
              }`}
            >
              <item.icon className={`w-5 h-5 ${activeTab === item.id ? 'text-magical-violet' : ''}`} />
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
          
          <div className="pt-8 mt-8 border-t border-white/10 hidden md:block">
            <button 
              onClick={logout}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all text-red-400 hover:text-red-300 hover:bg-red-400/10"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Oturumu Kapat</span>
            </button>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 space-y-6">
          
          {/* Profile Section */}
          {activeTab === 'profile' && (
            <section className="animate-in fade-in duration-300">
              <div className="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 backdrop-blur-sm">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center pb-4 border-b border-white/10">
                  <User className="w-5 h-5 mr-3 text-magical-violet" />
                  Kişisel Bilgiler
                </h2>
                
                <div className="flex flex-col sm:flex-row gap-8 items-start mb-8">
                  <div className="flex flex-col items-center space-y-4">
                    <div className="w-24 h-24 rounded-2xl bg-gradient-to-tr from-magical-indigo to-magical-violet border border-white/20 shadow-[0_0_20px_rgba(99,102,241,0.3)] flex items-center justify-center relative group overflow-hidden">
                      <span className="text-4xl font-bold text-white uppercase">{user?.name?.charAt(0) || 'U'}</span>
                      <div className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                        <span className="text-xs font-medium text-white">Değiştir</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex-1 space-y-4 w-full">
                    <div className="space-y-2">
                      <Label htmlFor="name" className="text-slate-300">Görünen İsim</Label>
                      <Input 
                        id="name" 
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        className="bg-black/50 border-white/10 focus:border-magical-violet text-white h-11 transition-all rounded-xl"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-slate-300">E-posta Adresi</Label>
                      <Input 
                        id="email" 
                        type="email" 
                        defaultValue={user?.email}
                        disabled
                        className="bg-black/80 border-white/5 text-slate-500 h-11 rounded-xl cursor-not-allowed"
                      />
                    </div>
                  </div>
                </div>

                {saveStatus && (
                  <div className={`mb-4 p-3 rounded-xl border text-xs text-center ${
                    saveStatus.type === 'success' 
                      ? 'bg-green-500/10 border-green-500/20 text-green-400' 
                      : 'bg-red-500/10 border-red-500/20 text-red-400'
                  }`}>
                    {saveStatus.msg}
                  </div>
                )}
                
                <div className="flex justify-end pt-4 border-t border-white/10">
                  <Button 
                    onClick={handleSaveProfile}
                    disabled={isSaving || displayName === user?.name}
                    className="rounded-xl px-6 h-11 bg-gradient-to-r from-magical-violet to-magical-indigo hover:opacity-90 transition-opacity disabled:opacity-50"
                  >
                    {isSaving ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
                  </Button>
                </div>
              </div>
            </section>
          )}

          {/* Subscription Section */}
          {activeTab === 'subscription' && (
            <section className="animate-in fade-in duration-300">
              <div className="bg-gradient-to-r from-magical-indigo/20 via-magical-violet/10 to-[#0b0816] border border-magical-indigo/30 rounded-3xl p-6 md:p-8 flex flex-col sm:flex-row items-center justify-between gap-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10 blur-[2px]">
                  <Crown className="w-32 h-32 text-magical-indigo" />
                </div>
                
                <div className="relative z-10 flex items-center">
                  <div className="w-14 h-14 bg-magical-indigo/20 rounded-2xl flex items-center justify-center mr-5 border border-magical-indigo/30 shadow-[0_0_15px_rgba(99,102,241,0.2)]">
                    <Gem className="w-7 h-7 text-magical-indigo" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white flex items-center">
                      Mevcut Plan: Çırak (Ücretsiz)
                    </h3>
                    <p className="text-slate-400 mt-1 max-w-sm">Günlük hikaye kotanız ve kredi limitleriniz burada görüntülenir.</p>
                  </div>
                </div>
                
                <Button className="shrink-0 w-full sm:w-auto rounded-xl px-6 h-12 bg-white text-magical-indigo hover:bg-slate-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.2)] relative z-10 font-bold">
                  Büyücü'ye Yükselt
                </Button>
              </div>
            </section>
          )}

          {/* Theme Preferences */}
          {activeTab === 'preferences' && (
            <section className="animate-in fade-in duration-300">
              <div className="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 backdrop-blur-sm">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center pb-4 border-b border-white/10">
                  <Moon className="w-5 h-5 mr-3 text-magical-violet" />
                  Görünüm ve Tema
                </h2>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    { id: 'dark', label: 'Sihirli Gece', icon: Moon, desc: 'Karanlık Mod' },
                    { id: 'light', label: 'Aydınlık Gün', icon: Sun, desc: 'Açık Mod' },
                    { id: 'system', label: 'Cihaz Teması', icon: Smartphone, desc: 'Otomatik' },
                  ].map((t) => (
                    <button
                      key={t.id}
                      onClick={() => setTheme(t.id as any)}
                      className={`flex flex-col items-center justify-center p-6 rounded-2xl border transition-all ${
                        theme === t.id
                          ? 'bg-magical-indigo/10 border-magical-indigo/50 shadow-[0_0_15px_rgba(99,102,241,0.2)]'
                          : 'bg-black/50 border-white/10 hover:border-white/30 hover:bg-white/5'
                      }`}
                    >
                      <t.icon className={`w-8 h-8 mb-3 ${theme === t.id ? 'text-magical-indigo' : 'text-slate-400'}`} />
                      <span className="font-bold text-white mb-1">{t.label}</span>
                      <span className="text-xs text-slate-400">{t.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* Notifications Section */}
          {activeTab === 'notifications' && (
            <section className="animate-in fade-in duration-300">
              <div className="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 backdrop-blur-sm space-y-6">
                <h2 className="text-xl font-bold text-white flex items-center pb-4 border-b border-white/10">
                  <Bell className="w-5 h-5 mr-3 text-magical-rose" />
                  Bildirim Tercihleri
                </h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-black/30 rounded-2xl border border-white/5">
                    <div>
                      <h4 className="text-white font-medium">Uygulama Bildirimleri</h4>
                      <p className="text-xs text-slate-400">Yeni masallar ve etkinlikler hakkında anlık bilgi alın.</p>
                    </div>
                    <button 
                      onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                      className={`w-12 h-6 rounded-full transition-colors relative flex-shrink-0 ${notificationsEnabled ? 'bg-magical-rose' : 'bg-white/10'}`}
                    >
                      <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${notificationsEnabled ? 'left-7' : 'left-1'}`} />
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-black/30 rounded-2xl border border-white/5">
                    <div>
                      <h4 className="text-white font-medium">Haftalık Gelişim Raporu</h4>
                      <p className="text-xs text-slate-400">Ebeveyn paneli özetini e-posta ile her hafta sonu alın.</p>
                    </div>
                    <button 
                      onClick={() => setWeeklyReportEnabled(!weeklyReportEnabled)}
                      className={`w-12 h-6 rounded-full transition-colors relative flex-shrink-0 ${weeklyReportEnabled ? 'bg-magical-rose' : 'bg-white/10'}`}
                    >
                      <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${weeklyReportEnabled ? 'left-7' : 'left-1'}`} />
                    </button>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Security & PIN Section */}
          {activeTab === 'security' && (
            <section className="animate-in fade-in duration-300">
              <div className="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 backdrop-blur-sm space-y-6">
                <h2 className="text-xl font-bold text-white flex items-center pb-4 border-b border-white/10">
                  <ShieldCheck className="w-5 h-5 mr-3 text-emerald-400" />
                  Güvenlik Ayarları
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <Label className="text-slate-300 block mb-2">Ebeveyn Paneli PIN Kodu</Label>
                    <div className="flex flex-col sm:flex-row gap-4 sm:items-center">
                      <Input 
                        type="password"
                        maxLength={4}
                        value={pin}
                        onChange={(e) => {
                          const val = e.target.value.replace(/\D/g, '');
                          if (val.length <= 4) setPin(val);
                        }}
                        className="bg-black/50 border-white/10 text-white h-12 w-32 text-center text-xl tracking-[0.5em] font-bold rounded-xl"
                      />
                      <div className="flex-1">
                        <p className="text-sm text-slate-400 mb-1">Dört haneli PIN kodunuz.</p>
                        <p className="text-xs text-slate-500 italic">Ebeveyn paneline erişmek için bu kodu kullanacaksındaız.</p>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-white/5">
                    <h4 className="text-white font-medium mb-1">Hesap Güvenliği</h4>
                    <p className="text-sm text-slate-400">Şu an {user?.email} ile giriş yaptınız.</p>
                    <Button variant="outline" className="mt-4 border-white/10 text-slate-300 hover:bg-white/5 rounded-xl">
                      Şifre Değiştirme Bağlantısı Gönder
                    </Button>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Mobile Logout (Visible only on px-4) */}
          <div className="md:hidden pt-4">
             <button 
                onClick={logout}
                className="w-full flex items-center justify-center space-x-3 px-4 py-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 font-medium"
              >
                <LogOut className="w-5 h-5" />
                <span>Oturumu Kapat</span>
              </button>
          </div>

        </div>
      </div>
    </div>
  );
};
