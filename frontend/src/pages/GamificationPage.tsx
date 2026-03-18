import { useState } from 'react';
import { motion } from 'framer-motion';
import { Award, Star, Zap, Shield, Crown, BookOpen, Clock, Heart, Flame, Sparkles } from 'lucide-react';

// Mock Badges Data
const BADGES = [
  { id: 1, title: 'İlk Adım', description: 'İlk masalını okudun!', icon: <BookOpen className="w-8 h-8" />, color: 'from-blue-400 to-indigo-500', isUnlocked: true, date: '12 Eki' },
  { id: 2, type: 'epic', title: 'Hızlı Kâşif', description: '1 haftada 7 masal!', icon: <Zap className="w-8 h-8" />, color: 'from-amber-300 to-orange-500', isUnlocked: true, date: '15 Eki' },
  { id: 3, title: 'Cesur Şövalye', description: 'İnteraktif bir masalı tamamladın.', icon: <Shield className="w-8 h-8" />, color: 'from-slate-300 to-slate-500', isUnlocked: true, date: '18 Eki' },
  { id: 4, type: 'legendary', title: 'Masal Ustası', description: 'Toplam 50 masal okudun.', icon: <Crown className="w-8 h-8 text-yellow-100" />, color: 'from-yellow-400 to-amber-600', isUnlocked: false },
  { id: 5, title: 'Gece Kuşu', description: 'Uyku modunda masal dinledin.', icon: <Star className="w-8 h-8" />, color: 'from-indigo-500 to-purple-600', isUnlocked: true, date: '20 Eki' },
  { id: 6, title: 'Zaman Yolcusu', description: 'Arka arkaya 15 gün okuma serisi.', icon: <Clock className="w-8 h-8" />, color: 'from-teal-400 to-emerald-500', isUnlocked: false },
  { id: 7, title: 'Büyük Kalp', description: '10 masalı beğendin.', icon: <Heart className="w-8 h-8" />, color: 'from-pink-400 to-rose-500', isUnlocked: false },
];

export const GamificationPage = () => {
  const [selectedBadge, setSelectedBadge] = useState<number | null>(null);

  // Level info
  const level = 4;
  const currentXP = 850;
  const targetXP = 1000;
  const progressPercent = Math.round((currentXP / targetXP) * 100);

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-10 max-w-6xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6 text-center sm:text-left">
        <div>
          <h1 className="text-4xl sm:text-5xl font-black bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent flex justify-center sm:justify-start items-center gap-3 drop-shadow-sm">
            <Award className="w-10 h-10 sm:w-12 sm:h-12 text-emerald-500" />
            Kazanımlarım
          </h1>
          <p className="text-slate-400 mt-2 font-medium text-lg">Seviyeni yükselt, sihirli ormanı büyüt ve yeni rozetler kazan!</p>
        </div>
        
        <div className="bg-[#1a1c23] border border-white/10 rounded-3xl px-8 py-5 flex items-center gap-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-3xl -mr-10 -mt-10 rounded-full" />
          <div className="flex flex-col items-center">
            <div className="text-slate-400 font-bold mb-1 flex items-center gap-1.5">
              <Flame className="w-5 h-5 text-amber-500" /> Seri
            </div>
            <div className="text-3xl font-black text-white">12 Gün</div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        
        {/* Left Column: Magic Tree (Level Progress) */}
        <div className="bg-gradient-to-b from-[#15171e] to-[#0f1115] border border-white/10 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden flex flex-col items-center justify-center min-h-[400px]">
          {/* Decorative glowing background */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-emerald-500/10 blur-[100px] rounded-full" />
          
          <div className="relative z-10 w-full mb-8">
             <div className="flex justify-between items-end mb-4">
               <div>
                  <h2 className="text-2xl font-black text-white">Seviye {level}</h2>
                  <p className="text-emerald-400 font-bold">Bilge Çınar</p>
               </div>
               <div className="text-right">
                  <span className="text-2xl font-black text-white">{currentXP}</span>
                  <span className="text-slate-500 font-medium"> / {targetXP} XP</span>
               </div>
             </div>
             
             {/* Progress Bar */}
             <div className="h-6 w-full bg-[#1e212b] rounded-full overflow-hidden border border-white/5 relative shadow-inner">
               <motion.div 
                 className="h-full bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full relative"
                 initial={{ width: 0 }}
                 animate={{ width: `${progressPercent}%` }}
                 transition={{ duration: 1.5, ease: "easeOut" }}
               >
                 {/* Shine effect on progress bar */}
                 <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-white/30 to-transparent" />
               </motion.div>
             </div>
             <p className="text-center text-sm text-slate-400 mt-4 font-medium">
               Sonraki seviyeye {targetXP - currentXP} XP kaldı!
             </p>
          </div>

          {/* Isometric Tree Visual Representation (Simplified CSS Art) */}
          <motion.div 
            className="relative z-10 mt-6"
            animate={{ y: [0, -10, 0] }}
            transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
          >
            {/* Tree Leaves */}
            <div className="w-48 h-48 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-full shadow-2xl relative z-10 border-4 border-[#0f1115]/20 flex items-center justify-center">
               <div className="w-32 h-32 bg-gradient-to-br from-emerald-300 to-teal-500 rounded-full opacity-80" />
               <Sparkles className="absolute top-5 right-10 text-yellow-200 w-6 h-6 animate-pulse" />
               <Sparkles className="absolute bottom-10 left-8 text-yellow-200 w-4 h-4 animate-pulse delay-150" />
            </div>
            {/* Tree Trunk */}
            <div className="w-12 h-20 bg-gradient-to-b from-amber-700 to-amber-900 mx-auto -mt-6 rounded-b-xl relative z-0 border-x-4 border-[#0f1115]/20 shadow-inner" />
            {/* Ground shadow */}
            <div className="w-32 h-4 bg-black/40 blur-xl rounded-full mx-auto mt-2" />
          </motion.div>
        </div>

        {/* Right Column: Badges Collection */}
        <div className="bg-[#15171e] border border-white/5 rounded-[2.5rem] p-8 shadow-xl relative">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-black text-white flex items-center gap-3">
              <Award className="w-7 h-7 text-indigo-400" />
              Rozet Panosu
            </h2>
            <div className="bg-[#1a1c23] px-4 py-1.5 rounded-xl border border-white/10 text-sm font-bold text-slate-300">
              <span className="text-indigo-400">{BADGES.filter(b => b.isUnlocked).length}</span> / {BADGES.length} Kazanıldı
            </div>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-5">
            {BADGES.map((badge, idx) => {
              const unlocked = badge.isUnlocked;
              return (
                <motion.div
                  key={badge.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.1 }}
                  onClick={() => setSelectedBadge(badge.id)}
                  className={`
                    relative group cursor-pointer aspect-square rounded-3xl p-4 flex flex-col items-center justify-center gap-3 text-center transition-all duration-300
                    ${unlocked 
                      ? 'bg-gradient-to-b from-[#1e212b] to-[#1a1c23] border border-white/10 hover:border-indigo-500/50 hover:shadow-lg hover:shadow-indigo-500/20' 
                      : 'bg-[#12141a] border border-slate-800/50 opacity-60 hover:opacity-100'}
                  `}
                >
                  {/* Badge Icon Container */}
                  <div className={`
                    w-16 h-16 rounded-2xl flex items-center justify-center transform transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3
                    ${unlocked ? `bg-gradient-to-br ${badge.color} text-white shadow-lg` : 'bg-slate-800 text-slate-500'}
                  `}>
                    {/* Inner styling based on type */}
                    <div className={`
                      w-14 h-14 rounded-xl flex items-center justify-center border-2 
                      ${unlocked ? 'border-white/20' : 'border-slate-700/50'}
                      ${badge.type === 'legendary' ? 'border-yellow-200/50 bg-white/10' : ''}
                      ${badge.type === 'epic' ? 'border-orange-200/50 bg-white/10' : ''}
                    `}>
                       {badge.icon}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className={`font-bold text-xs sm:text-sm line-clamp-1 ${unlocked ? 'text-slate-100' : 'text-slate-500'}`}>
                      {badge.title}
                    </h3>
                    {unlocked && badge.date && (
                      <span className="text-[10px] text-slate-500 font-medium">{badge.date}</span>
                    )}
                    {!unlocked && (
                      <span className="text-[10px] text-slate-600 font-medium">Kilitli</span>
                    )}
                  </div>
                  
                  {/* Selected Outline / Glow */}
                  {selectedBadge === badge.id && (
                    <motion.div 
                      layoutId="outline"
                      className="absolute inset-0 border-2 border-indigo-500 rounded-3xl z-10"
                      initial={false}
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                </motion.div>
              );
            })}
          </div>

          {/* Badge Detail Panel (bottom) */}
          <div className="mt-8 pt-6 border-t border-white/5">
            {selectedBadge ? (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-4 bg-[#1a1c23] p-4 rounded-2xl border border-white/5"
              >
                {(() => {
                  const b = BADGES.find(x => x.id === selectedBadge)!;
                  return (
                    <>
                      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 ${b.isUnlocked ? `bg-gradient-to-br ${b.color} text-white` : 'bg-slate-800 text-slate-500'}`}>
                         {b.icon}
                      </div>
                      <div>
                        <h4 className="font-bold text-white mb-1 flex items-center gap-2">
                          {b.title}
                          {b.type === 'legendary' && <span className="text-[10px] bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full uppercase tracking-wider">Efsanevi</span>}
                          {b.type === 'epic' && <span className="text-[10px] bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full uppercase tracking-wider">Destansı</span>}
                        </h4>
                        <p className="text-sm text-slate-400 font-medium">{b.description}</p>
                      </div>
                    </>
                  );
                })()}
              </motion.div>
            ) : (
              <div className="text-center p-4 text-slate-500 font-medium">
                Detayını görmek için bir rozete tıkla
              </div>
            )}
          </div>
          
        </div>

      </div>
    </div>
  );
};
