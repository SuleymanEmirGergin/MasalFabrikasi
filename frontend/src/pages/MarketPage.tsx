import { 
  Sparkles, 
  Crown, 
  Coins, 
  CheckCircle2, 
  Zap,
  Wand2
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export const MarketPage = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-magical-indigo via-magical-violet to-magical-rose bg-clip-text text-transparent">
          Büyülü Pazar Yeri
        </h1>
        <p className="text-slate-400 max-w-2xl mx-auto text-lg">
          Sihirli mürekkebinizi tazeleyin veya sınırsız masal dünyasının kapılarını açan Pro aboneliklere göz atın.
        </p>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Basic Plan */}
        <div className="bg-[#0b0816] border border-white/10 rounded-3xl p-8 flex flex-col relative overflow-hidden group hover:border-magical-indigo/50 transition-all duration-300">
          <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
            <Wand2 className="w-24 h-24 text-white" />
          </div>
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-white mb-2">Çırak</h3>
            <p className="text-slate-400">Yeni başlayan hikaye anlatıcıları için ideal.</p>
          </div>
          <div className="mb-8 flex items-baseline">
            <span className="text-5xl font-extrabold text-white">Ücretsiz</span>
          </div>
          <ul className="space-y-4 mb-8 flex-1">
            {[
              'Günde 2 Ücretsiz Hikaye',
              'Standart Karakter Seti',
              'Temel Sihirli Okuyucu Özellikleri',
              'Topluluk Kütüphanesine Erişim'
            ].map((feature, i) => (
              <li key={i} className="flex items-center text-slate-300">
                <CheckCircle2 className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
          <Button variant="outline" className="w-full rounded-xl border-white/20 hover:bg-white/5 h-12">
            Mevcut Plan
          </Button>
        </div>

        {/* Pro Plan (Popular) */}
        <div className="bg-gradient-to-b from-magical-indigo/20 to-[#0b0816] border-2 border-magical-indigo/50 rounded-3xl p-8 flex flex-col relative overflow-hidden transform md:-translate-y-4 shadow-[0_0_40px_rgba(99,102,241,0.2)]">
          <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-magical-indigo via-magical-violet to-magical-rose" />
          <div className="absolute top-4 right-4 bg-magical-indigo/20 text-magical-indigo text-xs font-bold px-3 py-1 rounded-full border border-magical-indigo/30 uppercase tracking-wider backdrop-blur-sm">
            En Popüler
          </div>
          <div className="absolute -top-10 -right-10 p-6 opacity-20 rotate-12 blur-sm">
            <Sparkles className="w-40 h-40 text-magical-indigo" />
          </div>
          
          <div className="mb-8 relative z-10">
            <h3 className="text-2xl font-bold text-white mb-2 flex items-center">
              <Sparkles className="w-5 h-5 text-magical-indigo mr-2" />
              Büyücü
            </h3>
            <p className="text-slate-400">Sınır tanımayan hayal güçleri için.</p>
          </div>
          <div className="mb-8 flex items-baseline relative z-10">
            <span className="text-5xl font-extrabold text-white">₺99</span>
            <span className="text-slate-400 ml-2">/ay</span>
          </div>
          <ul className="space-y-4 mb-8 flex-1 relative z-10">
            {[
              'Sınırsız Hikaye Üretimi',
              'Özel Karakter Yaratma',
              'Gelişmiş Sesli Okuma (Tüm Sesler)',
              'PDF ve EPUB Çıktısı Alma',
              'Öncelikli Sihirli Derleme (Daha Hızlı)'
            ].map((feature, i) => (
              <li key={i} className="flex items-center text-slate-200">
                <CheckCircle2 className="w-5 h-5 text-magical-indigo mr-3 flex-shrink-0" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
          <Button className="w-full rounded-xl bg-magical-indigo hover:bg-magical-indigo/90 text-white h-12 shadow-[0_0_20px_rgba(99,102,241,0.4)] relative z-10 transition-all hover:scale-[1.02]">
            Hemen Yükselt
          </Button>
        </div>

        {/* Premium Plan */}
        <div className="bg-[#0b0816] border border-white/10 rounded-3xl p-8 flex flex-col relative overflow-hidden group hover:border-magical-rose/50 transition-all duration-300">
          <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
            <Crown className="w-24 h-24 text-white" />
          </div>
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-white mb-2 flex items-center">
              <Crown className="w-5 h-5 text-magical-rose mr-2" />
              Üstat
            </h3>
            <p className="text-slate-400">Tüm galaksiyi bir araya getiren öğretmenler ve okullar için.</p>
          </div>
          <div className="mb-8 flex items-baseline">
            <span className="text-5xl font-extrabold text-white">₺249</span>
            <span className="text-slate-400 ml-2">/ay</span>
          </div>
          <ul className="space-y-4 mb-8 flex-1">
            {[
              'Büyücü planındaki her şey',
              '5 Alt Kullanıcı (Öğrenci Profili)',
              'Kendi Sesini Ekleme (Ses Klonlama)',
              'Toplu Kitap Basım Formatı',
              '7/24 Öncelikli Baykuş Desteği'
            ].map((feature, i) => (
              <li key={i} className="flex items-center text-slate-300">
                <CheckCircle2 className="w-5 h-5 text-magical-rose mr-3 flex-shrink-0" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
          <Button variant="outline" className="w-full rounded-xl border-magical-rose/30 text-magical-rose hover:bg-magical-rose/10 h-12">
            Satın Al
          </Button>
        </div>
      </div>

      {/* Credit Packages */}
      <div className="mt-16 pt-16 border-t border-white/10">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-white mb-4">Mürekkep (Kredi) Paketleri</h2>
          <p className="text-slate-400">Sadece ihtiyacınız olduğunda, fazladan sihirli mürekkep alın.</p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { credits: '100', price: '₺19', bonus: null },
            { credits: '500', price: '₺75', bonus: '+50 Bonus' },
            { credits: '1000', price: '₺139', bonus: '+150 Bonus' },
            { credits: '2500', price: '₺299', bonus: '+500 Bonus', popular: true }
          ].map((pkg, i) => (
            <div 
              key={i} 
              className={`bg-white/5 border rounded-2xl p-6 flex flex-col items-center cursor-pointer transition-all hover:scale-105 active:scale-95 ${
                pkg.popular 
                  ? 'border-magical-violet bg-magical-violet/10 shadow-[0_0_20px_rgba(167,139,250,0.2)]' 
                  : 'border-white/10 hover:border-white/30 hover:bg-white/10'
              }`}
            >
              {pkg.popular && (
                <div className="bg-magical-violet text-white text-[10px] uppercase font-bold px-2 py-1 rounded-full mb-3 shadow-[0_0_10px_rgba(167,139,250,0.5)]">
                  En İyi Seçenek
                </div>
              )}
              <Coins className={`w-12 h-12 mb-4 ${pkg.popular ? 'text-magical-violet drop-shadow-md' : 'text-slate-300'}`} />
              <div className="text-2xl font-bold text-white mb-1">{pkg.credits} Kredi</div>
              {pkg.bonus && <div className="text-sm text-green-400 font-medium mb-4">{pkg.bonus}</div>}
              {!pkg.bonus && <div className="h-5 mb-4" />} {/* Spacer */}
              <div className="text-xl font-semibold text-slate-300 mt-auto">{pkg.price}</div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Help Banner */}
      <div className="mt-12 bg-gradient-to-r from-blue-900/40 to-magical-indigo/20 border border-blue-500/30 rounded-2xl p-8 flex flex-col sm:flex-row items-center justify-between">
        <div className="flex items-center mb-4 sm:mb-0">
          <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mr-4">
            <Zap className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h4 className="text-lg font-bold text-white">Okul veya Kurum musunuz?</h4>
            <p className="text-slate-400">Çoklu lisans ve özel çözümler için bizimle iletişime geçin.</p>
          </div>
        </div>
        <Button variant="outline" className="rounded-xl border-blue-500/50 text-blue-300 hover:bg-blue-500/20">
          İletişime Geç
        </Button>
      </div>

    </div>
  );
};
