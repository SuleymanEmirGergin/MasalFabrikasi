import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Crown, Check, CreditCard, Sparkles, X, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Plan {
  id: string;
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  isPopular?: boolean;
}

const PLANS: Plan[] = [
  {
    id: 'free',
    name: 'Maceracı (Ücretsiz)',
    price: '0 ₺',
    period: '/ ay',
    description: 'Masal dünyasına ilk adımlar.',
    features: [
      'Günde 2 Sihirli Masal üretimi',
      'Standart sesleri dinleme',
      'Temel ebeveyn paneli',
      'Reklamlı deneyim'
    ]
  },
  {
    id: 'premium',
    name: 'Sihirli Başlangıç',
    price: '99 ₺',
    period: '/ ay',
    description: 'Daha fazla masal, daha fazla yaratıcılık.',
    features: [
      'Günde 10 Sihirli Masal üretimi',
      '3 Kendi Sesini Klonlama hakkı',
      'Hikayeleri PDF indirme',
      'Reklamsız deneyim',
      'Gelişmiş ebeveyn raporları'
    ],
    isPopular: true
  },
  {
    id: 'pro',
    name: 'Sınırsız Evren',
    price: '899 ₺',
    period: '/ yıl',
    description: 'Her şey dahil masal fabrikası.',
    features: [
      'Sınırsız Masal Üretimi',
      'Sınırsız Ses Klonlama',
      'İnteraktif Hikayelere Tam Erişim',
      'Akıllı Oda Senkronizasyonu (Yakında)',
      'Özel Avatar Yaratıcısı'
    ]
  }
];

export const SubscriptionPage = () => {
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubscribe = (planId: string) => {
    if (planId === 'free') return;
    setSelectedPlan(planId);
  };

  const processPayment = (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    // Simulating Iyzico / Stripe check out
    setTimeout(() => {
      setIsProcessing(false);
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        setSelectedPlan(null);
      }, 3000);
    }, 2000);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-12 animate-in fade-in duration-500 pb-12">
      <div className="text-center space-y-4 pt-8">
        <div className="inline-flex p-3 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-2xl mb-2">
          <Crown className="w-12 h-12 text-amber-500" />
        </div>
        <h1 className="text-4xl md:text-5xl font-black bg-gradient-to-r from-amber-400 via-orange-500 to-rose-500 bg-clip-text text-transparent">
          Sınırsız Masal Dünyasının Kapılarını Açın
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
          Çocuğunuzun hayal gücünü geliştirmek ve kendi sesinizle her gece yeni bir macera yaratmak için planınızı seçin.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {PLANS.map((plan, index) => (
          <motion.div
            key={plan.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`relative rounded-3xl overflow-hidden border ${
              plan.isPopular 
                ? 'bg-gradient-to-b from-magical-purple/10 to-transparent border-magical-purple shadow-[0_0_40px_-10px_var(--magical-purple)]' 
                : 'bg-black/40 border-white/10'
            }`}
          >
            {plan.isPopular && (
              <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-magical-purple to-magical-rose" />
            )}
            
            <div className="p-8">
              {plan.isPopular && (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-magical-purple/20 text-magical-purple text-xs font-bold mb-4 border border-magical-purple/30">
                  <Star className="w-3.5 h-3.5 fill-current" />
                  EN ÇOK TERCİH EDİLEN
                </div>
              )}
              
              <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
              <p className="text-slate-400 text-sm mb-6">{plan.description}</p>
              
              <div className="mb-6">
                <span className="text-4xl font-black text-white">{plan.price}</span>
                <span className="text-slate-400">{plan.period}</span>
              </div>
              
              <Button
                onClick={() => handleSubscribe(plan.id)}
                variant={plan.isPopular ? "default" : "outline"}
                className={`w-full py-6 text-lg rounded-xl mb-8 ${
                  plan.isPopular 
                    ? 'bg-gradient-to-r from-magical-purple to-magical-rose hover:opacity-90 shadow-lg border-0' 
                    : 'border-white/20 hover:bg-white/5'
                }`}
                disabled={plan.id === 'free'}
              >
                {plan.id === 'free' ? 'Mevcut Planınız' : 'Premium\'a Geç'}
              </Button>
              
              <div className="space-y-4">
                {plan.features.map((feature, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="mt-1 p-0.5 rounded-full bg-emerald-500/20 shrink-0">
                      <Check className="w-4 h-4 text-emerald-500" />
                    </div>
                    <span className="text-slate-300 text-sm">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Payment Modal */}
      <AnimatePresence>
        {selectedPlan && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0f1115] border border-white/10 rounded-3xl p-6 w-full max-w-md shadow-2xl relative"
            >
              <button 
                onClick={() => !isProcessing && setSelectedPlan(null)}
                className="absolute right-4 top-4 p-2 text-slate-400 hover:text-white rounded-full bg-white/5 transition-colors pb-0"
              >
                <X className="w-5 h-5 mb-2" />
              </button>

              {showSuccess ? (
                <div className="py-12 text-center space-y-4">
                  <motion.div 
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
                  >
                    <Check className="w-10 h-10 text-emerald-500" />
                  </motion.div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                    Aramıza Hoş Geldiniz!
                  </h3>
                  <p className="text-slate-400">Ödemeniz başarıyla alındı. Sihirli güçleriniz aktif edildi.</p>
                </div>
              ) : (
                <>
                  <div className="flex items-center gap-3 mb-8">
                    <div className="p-2.5 bg-indigo-500/20 rounded-xl">
                      <CreditCard className="w-6 h-6 text-indigo-400" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">Güvenli Ödeme</h3>
                      <p className="text-slate-400 text-xs">Stripe / Iyzico Altyapısı İle</p>
                    </div>
                  </div>

                  <form onSubmit={processPayment} className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-slate-400 ml-1">KART ÜZERİNDEKİ İSİM</label>
                      <Input required placeholder="Ayşe Yılmaz" className="bg-black/50 border-white/10 text-white placeholder:text-slate-600 focus:border-indigo-500" />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-slate-400 ml-1">KART NUMARASI</label>
                      <div className="relative">
                        <Input required placeholder="0000 0000 0000 0000" maxLength={19} className="bg-black/50 border-white/10 text-white placeholder:text-slate-600 focus:border-indigo-500 pl-10" />
                        <CreditCard className="w-5 h-5 text-slate-500 absolute left-3 top-2.5" />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-slate-400 ml-1">SON KULLANMA</label>
                        <Input required placeholder="MM/YY" maxLength={5} className="bg-black/50 border-white/10 text-white placeholder:text-slate-600 focus:border-indigo-500" />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-slate-400 ml-1">CVC</label>
                        <Input required placeholder="123" maxLength={3} className="bg-black/50 border-white/10 text-white placeholder:text-slate-600 focus:border-indigo-500" />
                      </div>
                    </div>

                    <div className="pt-6">
                      <Button 
                        type="submit" 
                        disabled={isProcessing}
                        className="w-full h-12 bg-gradient-to-r from-indigo-500 to-purple-500 hover:opacity-90 text-white font-bold text-lg rounded-xl relative overflow-hidden"
                      >
                        {isProcessing ? (
                          <span className="flex items-center gap-2">
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            İşleniyor...
                          </span>
                        ) : (
                          <span className="flex items-center gap-2">
                            Kilitleri Aç <Sparkles className="w-5 h-5" />
                          </span>
                        )}
                      </Button>
                      <p className="text-center text-[10px] text-slate-500 mt-4">
                        256-bit SSL şifreleme ile güvence altındadır. Bütün ödemeler sanal ortamda simüle edilmektedir.
                      </p>
                    </div>
                  </form>
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
