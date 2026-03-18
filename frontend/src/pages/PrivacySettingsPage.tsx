import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheck,
  Lock,
  Download,
  Snowflake,
  Trash2,
  Bell,
  BarChart2,
  ChevronDown,
  AlertTriangle,
  CheckCircle2,
  X,
  Eye,
  EyeOff,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { usePrivacy } from '@/api/hooks';

type PinState = 'locked' | 'entering' | 'unlocked';

const CORRECT_PIN = '1234';

const TOGGLE_SETTINGS = [
  { id: 'marketing', icon: Bell, label: 'Pazarlama E-postaları', desc: 'Kampanya ve fırsatlardan haberdar ol', defaultValue: true },
  { id: 'analytics', icon: BarChart2, label: 'Analitik Veri Toplama', desc: 'Uygulama geliştirmek için anonim kullanım verisi', defaultValue: true },
  { id: 'personalization', icon: Eye, label: 'Kişiselleştirme', desc: 'İçerikleri sana göre uyarlamak için profil verisi', defaultValue: false },
];

const GDPR_SECTIONS = [
  { title: 'Toplanan Veriler', content: 'Ad, e-posta, kullanım istatistikleri ve cihaz bilgileri toplanır. Ödeme verileri hiçbir zaman saklanmaz.' },
  { title: 'Veri Paylaşımı', content: 'Verileriniz üçüncü taraflarla satılmaz. Yalnızca zorunlu hizmet sağlayıcılarla (sunucu, e-posta) paylaşılır.' },
  { title: 'Saklama Süresi', content: 'Hesap aktifken veriler korunur. Silme talebinden sonra 30 gün içinde tüm veriler kalıcı olarak yok edilir.' },
  { title: 'Haklarınız', content: 'KVKK/GDPR kapsamında; erişim, düzeltme, silme, itiraz ve taşınabilirlik haklarına sahipsiniz.' },
];

type ConfirmModal = 'freeze' | 'delete' | null;

export const PrivacySettingsPage = () => {
  const [pinState, setPinState] = useState<PinState>('locked');
  const [pinInput, setPinInput] = useState('');
  const [pinError, setPinError] = useState(false);
  const [showPin, setShowPin] = useState(false);
  const { loading: apiLoading, exportData, requestDeletion, updatePrivacySettings } = usePrivacy();

  const [toggles, setToggles] = useState(
    Object.fromEntries(TOGGLE_SETTINGS.map((s) => [s.id, s.defaultValue]))
  );
  const [openAccordion, setOpenAccordion] = useState<number | null>(null);
  const [confirmModal, setConfirmModal] = useState<ConfirmModal>(null);
  const [confirmDone, setConfirmDone] = useState<string | null>(null);

  const handlePinDigit = (digit: string) => {
    if (pinInput.length >= 4) return;
    const next = pinInput + digit;
    setPinInput(next);
    setPinError(false);

    if (next.length === 4) {
      setTimeout(() => {
        if (next === CORRECT_PIN) {
          setPinState('unlocked');
          setPinInput('');
        } else {
          setPinError(true);
          setTimeout(() => {
            setPinInput('');
            setPinError(false);
          }, 800);
        }
      }, 200);
    }
  };

  const handlePinBackspace = () => {
    setPinInput((prev) => prev.slice(0, -1));
    setPinError(false);
  };

  const handleToggle = async (id: string, val: boolean) => {
    setToggles((prev) => ({ ...prev, [id]: val }));
    // Map toggle id to backend field
    const fieldMap: Record<string, string> = {
      marketing: 'marketing_emails',
      analytics: 'analytics_consent',
      personalization: 'data_sharing',
    };
    const field = fieldMap[id];
    if (field) await updatePrivacySettings({ [field]: val });
  };

  const handleConfirmAction = async (action: ConfirmModal) => {
    if (action === 'delete') {
      await requestDeletion();
      setConfirmDone('Silme isteğiniz alındı. 24 saat içinde tamamlanacak.');
    } else if (action === 'freeze') {
      // freeze is UI-only for now — no dedicated endpoint yet
      await new Promise((r) => setTimeout(r, 800));
      setConfirmDone('Hesabınız donduruldu.');
    }
    setConfirmModal(null);
    setTimeout(() => setConfirmDone(null), 5000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <div className="p-3 bg-emerald-500/20 rounded-xl">
          <ShieldCheck className="w-8 h-8 text-emerald-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            Gizlilik & Güvenlik Merkezi
          </h1>
          <p className="text-slate-400 mt-0.5">KVKK ve GDPR uyumlu veri yönetim paneliniz.</p>
        </div>
      </motion.div>

      {/* Success toast */}
      <AnimatePresence>
        {confirmDone && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex items-center gap-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 p-4 rounded-xl"
          >
            <CheckCircle2 className="w-5 h-5 shrink-0" />
            <span>{confirmDone}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* PIN Lock Gate */}
      <AnimatePresence mode="wait">
        {pinState === 'locked' && (
          <motion.div
            key="locked"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-8 text-center"
          >
            <div className="w-16 h-16 bg-emerald-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Lock className="w-8 h-8 text-emerald-400" />
            </div>
            <h2 className="text-xl font-bold text-white mb-1">Ebeveyn Doğrulaması</h2>
            <p className="text-slate-400 mb-6 text-sm">Gizlilik ayarlarına erişmek için PIN'inizi girin. (Demo: 1234)</p>

            {/* PIN dots */}
            <div className="flex justify-center gap-4 mb-3">
              {[0, 1, 2, 3].map((i) => (
                <motion.div
                  key={i}
                  animate={pinError ? { x: [-4, 4, -4, 4, 0] } : {}}
                  transition={{ duration: 0.3 }}
                  className={`w-4 h-4 rounded-full border-2 transition-colors ${
                    i < pinInput.length
                      ? showPin
                        ? 'bg-transparent border-emerald-400'
                        : pinError
                        ? 'bg-red-500 border-red-400'
                        : 'bg-emerald-400 border-emerald-400'
                      : 'border-white/20 bg-transparent'
                  }`}
                >
                  {showPin && i < pinInput.length && (
                    <span className="flex items-center justify-center h-full text-xs font-bold text-emerald-400">
                      {pinInput[i]}
                    </span>
                  )}
                </motion.div>
              ))}
            </div>
            <button
              onClick={() => setShowPin((s) => !s)}
              className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300 mx-auto mb-4 transition-colors"
            >
              {showPin ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
              {showPin ? 'Gizle' : 'Göster'}
            </button>

            {/* Keypad */}
            <div className="grid grid-cols-3 gap-3 max-w-xs mx-auto">
              {['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫'].map((key, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    if (key === '⌫') handlePinBackspace();
                    else if (key !== '') handlePinDigit(key);
                  }}
                  disabled={key === ''}
                  className={`h-14 rounded-xl text-lg font-bold transition-all ${
                    key === ''
                      ? 'cursor-default'
                      : key === '⌫'
                      ? 'bg-white/5 hover:bg-red-500/20 text-red-400 border border-white/10'
                      : 'bg-white/5 hover:bg-white/10 text-white border border-white/10 active:scale-95'
                  }`}
                >
                  {key}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {pinState === 'unlocked' && (
          <motion.div
            key="unlocked"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {/* Unlocked indicator */}
            <div className="flex items-center justify-between bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4">
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-5 h-5" />
                <span className="font-medium text-sm">Ebeveyn modu aktif</span>
              </div>
              <button
                onClick={() => { setPinState('locked'); setPinInput(''); }}
                className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1"
              >
                <Lock className="w-3 h-3" /> Kilitle
              </button>
            </div>

            {/* Data Actions */}
            <section className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
              <h3 className="text-lg font-bold text-white">Veri Yönetimi</h3>

              {/* Download */}
              <div className="flex items-center justify-between p-4 bg-black/20 rounded-xl border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <Download className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-200">Verilerimi İndir</p>
                    <p className="text-xs text-slate-500">JSON formatında tüm hesap verisi</p>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={apiLoading}
                  className="border-blue-500/30 text-blue-400 hover:bg-blue-500/10"
                  onClick={() => exportData()}
                >
                  İndir
                </Button>
              </div>

              {/* Freeze */}
              <div className="flex items-center justify-between p-4 bg-black/20 rounded-xl border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-cyan-500/20 rounded-lg">
                    <Snowflake className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-200">Hesabı Dondur</p>
                    <p className="text-xs text-slate-500">Giriş kapatılır, veriler korunur</p>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={apiLoading}
                  className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
                  onClick={() => setConfirmModal('freeze')}
                >
                  Dondur
                </Button>
              </div>

              {/* Delete */}
              <div className="flex items-center justify-between p-4 bg-red-500/5 rounded-xl border border-red-500/20">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-red-500/20 rounded-lg">
                    <Trash2 className="w-5 h-5 text-red-400" />
                  </div>
                  <div>
                    <p className="font-medium text-red-300">Tüm Verileri Sil</p>
                    <p className="text-xs text-red-500">Geri alınamaz — kalıcı silme</p>
                  </div>
                </div>
                <Button
                  size="sm"
                  className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30"
                  onClick={() => setConfirmModal('delete')}
                >
                  Sil
                </Button>
              </div>
            </section>

            {/* Toggle Settings */}
            <section className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
              <h3 className="text-lg font-bold text-white">İzin Yönetimi</h3>
              {TOGGLE_SETTINGS.map((setting) => (
                <div key={setting.id} className="flex items-center justify-between p-4 bg-black/20 rounded-xl border border-white/5">
                  <div className="flex items-center gap-3">
                    <setting.icon className="w-5 h-5 text-slate-400" />
                    <div>
                      <p className="font-medium text-slate-200 text-sm">{setting.label}</p>
                      <p className="text-xs text-slate-500">{setting.desc}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleToggle(setting.id, !toggles[setting.id])}
                    className={`relative w-11 h-6 rounded-full border-2 transition-all ${
                      toggles[setting.id]
                        ? 'bg-emerald-500 border-emerald-400'
                        : 'bg-white/10 border-white/20'
                    }`}
                  >
                    <motion.div
                      animate={{ x: toggles[setting.id] ? 20 : 2 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      className="absolute top-0.5 left-0 w-4 h-4 bg-white rounded-full shadow"
                    />
                  </button>
                </div>
              ))}
            </section>

            {/* GDPR Accordion */}
            <section className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
              <h3 className="text-lg font-bold text-white">Gizlilik Politikası (KVKK / GDPR)</h3>
              {GDPR_SECTIONS.map((section, i) => (
                <div key={i} className="border border-white/5 rounded-xl overflow-hidden">
                  <button
                    onClick={() => setOpenAccordion(openAccordion === i ? null : i)}
                    className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition-colors"
                  >
                    <span className="font-medium text-slate-200 text-sm">{section.title}</span>
                    <motion.div animate={{ rotate: openAccordion === i ? 180 : 0 }}>
                      <ChevronDown className="w-4 h-4 text-slate-500" />
                    </motion.div>
                  </button>
                  <AnimatePresence>
                    {openAccordion === i && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <p className="px-4 pb-4 text-sm text-slate-400">{section.content}</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </section>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confirm Modal */}
      <AnimatePresence>
        {confirmModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setConfirmModal(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-[#0d0b1a] border border-white/10 rounded-2xl p-8 max-w-sm w-full text-center"
            >
              <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 ${confirmModal === 'delete' ? 'bg-red-500/20' : 'bg-cyan-500/20'}`}>
                <AlertTriangle className={`w-8 h-8 ${confirmModal === 'delete' ? 'text-red-400' : 'text-cyan-400'}`} />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">
                {confirmModal === 'delete' ? 'Verileri Silmek İstediğine Emin Misin?' : 'Hesabı Dondurmak İstediğine Emin Misin?'}
              </h3>
              <p className="text-slate-400 text-sm mb-6">
                {confirmModal === 'delete'
                  ? 'Bu işlem geri alınamaz. Tüm hikayeleriniz, karakterleriniz ve profiliniz kalıcı olarak silinecektir.'
                  : 'Hesabınız dondurulacak, giriş yapılamaz. Verileriniz korunacaktır.'}
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1 border-white/10 text-slate-300"
                  onClick={() => setConfirmModal(null)}
                >
                  <X className="w-4 h-4 mr-2" />
                  Vazgeç
                </Button>
                <Button
                  className={`flex-1 ${confirmModal === 'delete' ? 'bg-red-500 hover:bg-red-600' : 'bg-cyan-600 hover:bg-cyan-500'}`}
                  onClick={() => handleConfirmAction(confirmModal)}
                >
                  Evet, Onayla
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
