import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheck,
  BookOpen,
  Brain,
  Activity,
  Clock,
  TrendingUp,
  Lock,
  CheckCircle2,
  Timer,
  Sun,
} from 'lucide-react';
import { useParentalStats } from '@/api/hooks';
import { useAuthStore } from '@/store/useAuthStore';
import { useParentalStore } from '@/store/useParentalStore';

// UI-only mock data (not in backend yet)
const TODAYS_READS = [
  { title: 'Kayıp Ayıcık', minutes: 12, emoji: '🐻' },
  { title: 'Mürver Ağacı', minutes: 18, emoji: '🌳' },
  { title: 'Uçan Halı', minutes: 8, emoji: '🪄' },
];

export const ParentalDashboardPage = () => {
  const { user } = useAuthStore();
  const userId = user?.id;
  const parentName = user?.preferences?.username || 'Ebeveyn';

  const { data: apiStats, fetchStats } = useParentalStats(userId);

  useEffect(() => { fetchStats(); }, [fetchStats]);

  // Merge API data with defaults
  const stats = {
    total_stories_read: apiStats?.total_stories_read ?? 0,
    total_words_encountered: apiStats?.total_words_encountered ?? 0,
    unique_vocab_exposure: apiStats?.unique_vocab_exposure ?? 0,
    screen_time_today_min: 38, // UI-only, not in backend yet
    top_themes: apiStats?.top_themes ?? [],
    todays_reads: TODAYS_READS, // UI-only, not in backend yet
    recent_analyses: apiStats?.recent_analyses ?? [],
  };

  const maxThemeCount = Math.max(...stats.top_themes.map((t) => t.count), 1);

  // PIN gate
  const { pin: CORRECT_PIN, screenTimeLimit: screenLimitMin, setScreenTimeLimit: setScreenLimitMin } = useParentalStore();
  const [pinUnlocked, setPinUnlocked] = useState(false);
  const [pinInput, setPinInput] = useState('');
  const [pinError, setPinError] = useState(false);

  const handlePinDigit = (d: string) => {
    if (pinInput.length >= 4) return;
    const next = pinInput + d;
    setPinInput(next);
    setPinError(false);
    if (next.length === 4) {
      setTimeout(() => {
        if (next === CORRECT_PIN) {
          setPinUnlocked(true);
          setPinInput('');
        } else {
          setPinError(true);
          setTimeout(() => { setPinInput(''); setPinError(false); }, 800);
        }
      }, 200);
    }
  };

  const screenPct = Math.min((stats.screen_time_today_min / screenLimitMin) * 100, 100);
  const screenColor = screenPct > 90 ? 'from-rose-500 to-rose-400' : screenPct > 70 ? 'from-amber-500 to-amber-400' : 'from-emerald-500 to-emerald-400';

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4">
        <div className="p-3 bg-emerald-500/20 rounded-xl">
          <ShieldCheck className="w-8 h-8 text-emerald-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
            Ebeveyn Paneli
          </h1>
          <p className="text-slate-400 mt-0.5">Merhaba, {parentName} — çocuğunuzun gelişimini takip edin.</p>
        </div>
        {pinUnlocked && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={() => setPinUnlocked(false)}
            className="ml-auto flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            <Lock className="w-3 h-3" /> Kilitle
          </motion.button>
        )}
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[
          { icon: BookOpen, label: 'Okunан Masal', value: stats.total_stories_read, color: 'text-violet-400', bg: 'bg-violet-500/20' },
          { icon: Activity, label: 'Karşılaşılan Kelime', value: stats.total_words_encountered.toLocaleString(), color: 'text-amber-400', bg: 'bg-amber-500/20' },
          { icon: Brain, label: 'Öğrenilen Yeni Kelime', value: stats.unique_vocab_exposure, color: 'text-emerald-400', bg: 'bg-emerald-500/20' },
        ].map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-6 flex items-center gap-4"
          >
            <div className={`p-4 ${s.bg} rounded-xl ${s.color}`}>
              <s.icon className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs text-slate-400 font-medium">{s.label}</p>
              <p className="text-3xl font-bold text-white">{s.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bugün Okunanlar */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4"
        >
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Sun className="w-4 h-4 text-amber-400" />
            Bugün Okunanlar
          </h2>
          {stats.todays_reads.map((r, i) => (
            <div key={i} className="flex items-center gap-3 p-3 bg-black/20 rounded-xl border border-white/5">
              <span className="text-2xl">{r.emoji}</span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-200 text-sm truncate">{r.title}</p>
              </div>
              <span className="text-xs text-slate-500 shrink-0">{r.minutes} dk</span>
            </div>
          ))}
        </motion.div>

        {/* Screen Time */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-5"
        >
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Timer className="w-4 h-4 text-cyan-400" />
            Ekran Süresi
          </h2>
          <div className="text-center">
            <p className="text-4xl font-black text-white">{stats.screen_time_today_min}<span className="text-sm font-normal text-slate-400"> / {screenLimitMin} dk</span></p>
            <p className="text-xs text-slate-500 mt-1">Bugün</p>
          </div>
          <div className="h-3 bg-white/5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${screenPct}%` }}
              transition={{ duration: 1, delay: 0.5 }}
              className={`h-full rounded-full bg-gradient-to-r ${screenColor}`}
            />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Günlük Limit</span>
              <span className="font-mono font-bold text-white">{screenLimitMin} dk</span>
            </div>
            <input
              type="range"
              min={15}
              max={180}
              step={15}
              value={screenLimitMin}
              onChange={(e) => setScreenLimitMin(Number(e.target.value))}
              className="w-full accent-cyan-400"
            />
          </div>
        </motion.div>

        {/* Temalar */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4"
        >
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-violet-400" />
            En Çok Okunan Temalar
          </h2>
          {stats.top_themes.map((theme, i) => (
            <div key={i}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300 font-medium">{theme.name}</span>
                <span className="text-slate-500">{theme.count} hikaye</span>
              </div>
              <div className="h-2 bg-black/30 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(theme.count / maxThemeCount) * 100}%` }}
                  transition={{ duration: 0.8, delay: 0.5 + i * 0.1 }}
                  className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full"
                />
              </div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* PIN-Protected: Son Analizler */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white/5 border border-white/10 rounded-2xl p-6"
      >
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-emerald-400" />
          Son Analizler
          {!pinUnlocked && (
            <span className="ml-2 flex items-center gap-1 text-xs text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
              <Lock className="w-2.5 h-2.5" /> PIN Gerekli
            </span>
          )}
        </h2>

        <AnimatePresence mode="wait">
          {!pinUnlocked ? (
            <motion.div
              key="locked"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4 py-6"
            >
              <p className="text-sm text-slate-400">Detaylı analizleri görüntülemek için PIN'inizi girin. (Demo: 1234)</p>
              <div className="flex gap-3 mb-2">
                {[0, 1, 2, 3].map((i) => (
                  <motion.div
                    key={i}
                    animate={pinError ? { x: [-3, 3, -3, 3, 0] } : {}}
                    transition={{ duration: 0.3 }}
                    className={`w-3 h-3 rounded-full border-2 ${i < pinInput.length ? (pinError ? 'bg-red-500 border-red-400' : 'bg-emerald-400 border-emerald-400') : 'border-white/20'}`}
                  />
                ))}
              </div>
              <div className="grid grid-cols-3 gap-2 max-w-[240px]">
                {['1','2','3','4','5','6','7','8','9','','0','⌫'].map((key, idx) => (
                  <button
                    key={idx}
                    disabled={key === ''}
                    onClick={() => { if (key === '⌫') setPinInput(p => p.slice(0,-1)); else if (key) handlePinDigit(key); }}
                    className={`h-11 rounded-lg text-base font-bold transition-all ${key === '' ? 'cursor-default' : key === '⌫' ? 'bg-white/5 text-red-400 border border-white/10 hover:bg-red-500/10' : 'bg-white/5 text-white border border-white/10 hover:bg-white/10 active:scale-95'}`}
                  >
                    {key}
                  </button>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="unlocked"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              <div className="flex items-center gap-2 text-xs text-emerald-400 mb-4">
                <CheckCircle2 className="w-4 h-4" /> Ebeveyn modu aktif
              </div>
              {stats.recent_analyses.map((analysis, i) => (
                <div key={i} className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                  <div className="w-10 h-10 shrink-0 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                    <span className="text-xs font-bold text-emerald-400">{analysis.score}</span>
                  </div>
                  <div>
                    <h3 className="text-white font-medium">{analysis.story_title}</h3>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {analysis.themes.map((t, j) => (
                        <span key={j} className="text-xs px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/20">{t}</span>
                      ))}
                    </div>
                    <p className="text-xs text-slate-500 mt-2">
                      {new Date(analysis.date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};
