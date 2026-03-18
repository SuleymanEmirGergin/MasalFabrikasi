import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, Compass, Mountain, Trees, Castle, Waves, Sword, Sparkles, Map as MapIcon, X } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Link } from 'react-router-dom';

interface Hero {
  id: string;
  name: string;
  type: string;
  biome: string;
  x: number;
  y: number;
}

interface Biome {
  id: string;
  label: string;
  icon: any;
  color: string;
  bg: string;
  glow: string;
  description: string;
}

const HERO_BIOMES: Biome[] = [
  { 
    id: 'enchanted-forest', 
    label: 'Zümrüt Ormanı', 
    icon: Trees, 
    color: 'text-emerald-400', 
    bg: 'bg-emerald-500/20',
    glow: 'rgba(16, 185, 129, 0.15)',
    description: 'Kadim ağaçların fısıldadığı, yaprakların gümüş gibi parladığı sonsuz bir yeşillik. Burada zaman, çiçeklerin açışına göre akar.'
  },
  { 
    id: 'crystal-mountains', 
    label: 'Gökkuşağı Zirveleri', 
    icon: Mountain, 
    color: 'text-sky-400', 
    bg: 'bg-sky-500/20',
    glow: 'rgba(56, 189, 248, 0.15)',
    description: 'Bulutların üzerinde yükselen, buzdan kulelerin gökyüzüne dokunduğu devasa zirveler. Her adımda bir kar tanesi hikaye anlatır.'
  },
  { 
    id: 'royal-castle', 
    label: 'Altın Şafak Kalesi', 
    icon: Castle, 
    color: 'text-amber-400', 
    bg: 'bg-amber-500/20',
    glow: 'rgba(251, 191, 36, 0.15)',
    description: 'Güneşin hiç batmadığı, kulelerin saf altından inşa edildiği görkemli bir krallık. Adalet ve cesaretin sarsılmaz evi.'
  },
  { 
    id: 'mystic-seas', 
    label: 'Sonsuz Yakut Denizi', 
    icon: Waves, 
    color: 'text-indigo-400', 
    bg: 'bg-indigo-500/20',
    glow: 'rgba(99, 102, 241, 0.15)',
    description: 'Derinliklerinde kayıp şehirlerin uyuduğu, ay ışığının dalgalarda dans ettiği efsunlu sular. Bilgeliğin ve sırların kaynağı.'
  },
];

// Seeded/Fixed particle positions to avoid render purity issues
const PARTICLE_DATA = [
  { x: 20, yOffset: 5, duration: 2.1 },
  { x: 50, yOffset: 12, duration: 2.8 },
  { x: 80, yOffset: -3, duration: 2.4 }
];

export const StoryMapPage = () => {
  const [selectedHero, setSelectedHero] = useState<Hero | null>(null);
  const [activeBiome, setActiveBiome] = useState<Biome | null>(null);

  const heroes = useMemo<Hero[]>(() => [
    { id: '1', name: 'Alp Arslan', type: 'Knight', biome: 'royal-castle', x: 25, y: 35 },
    { id: '2', name: 'Zümrüt Prenses', type: 'Fairy', biome: 'enchanted-forest', x: 65, y: 25 },
    { id: '3', name: 'Kaptan Maviş', type: 'Explorer', biome: 'mystic-seas', x: 40, y: 70 },
    { id: '4', name: 'Gümüş Kanat', type: 'Dragon', biome: 'crystal-mountains', x: 75, y: 65 },
  ], []);

  return (
    <div className="relative h-[calc(100vh-8rem)] overflow-hidden rounded-[2.5rem] bg-[#02010a] border border-white/5 shadow-[0_0_100px_rgba(0,0,0,0.8)]">
      {/* --- LAYER 1: Deep Magical Nebula --- */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-40">
        <motion.div 
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
            opacity: [0.3, 0.5, 0.3]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          className="absolute -top-1/4 -left-1/4 w-full h-full bg-[radial-gradient(circle_at_center,rgba(124,58,237,0.15),transparent_60%)] blur-[100px]" 
        />
        <motion.div 
          animate={{ 
            scale: [1.2, 1, 1.2],
            rotate: [90, 0, 90],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
          className="absolute -bottom-1/4 -right-1/4 w-full h-full bg-[radial-gradient(circle_at_center,rgba(167,139,250,0.1),transparent_60%)] blur-[100px]" 
        />
      </div>

      {/* --- LAYER 2: Ancient Star Map Lines --- */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <svg className="w-full h-full">
          <circle cx="50%" cy="50%" r="20%" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" strokeDasharray="4 8" />
          <circle cx="50%" cy="50%" r="40%" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="8 16" />
          <line x1="0" y1="50%" x2="100%" y2="50%" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
          <line x1="50%" y1="0" x2="50%" y2="100%" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
        </svg>
      </div>

      {/* Header Overlay */}
      <header className="absolute top-8 left-8 z-30 flex items-center gap-6">
        <Link to="/">
          <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
            <Button variant="ghost" size="icon" className="bg-white/5 hover:bg-white/10 backdrop-blur-xl rounded-2xl border border-white/10 w-12 h-12">
              <ChevronLeft className="w-6 h-6 text-white" />
            </Button>
          </motion.div>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 bg-indigo-500/20 rounded-lg">
              <Compass className="w-7 h-7 text-indigo-400" />
            </span>
            Masal Diyarı
          </h1>
          <p className="text-slate-400/80 text-sm mt-1">Efsanelerin ve kahramanların evi...</p>
        </div>
      </header>

      {/* --- MAIN WORLD CANVAS --- */}
      <div className="relative w-full h-full flex items-center justify-center p-8 lg:p-16">
        <div className="relative w-full h-full rounded-[2rem] bg-white/[0.02] border border-white/5 shadow-inner overflow-hidden">
          
          {/* Biome atmospheric atmospheric glows */}
          {heroes.map((hero) => {
            const biome = HERO_BIOMES.find(b => b.id === hero.biome) || HERO_BIOMES[0];
            return (
              <motion.div
                key={`glow-${hero.id}`}
                className="absolute w-[400px] h-[400px] blur-[80px] pointer-events-none rounded-full"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.1, 0.2, 0.1]
                }}
                transition={{ duration: 8, repeat: Infinity }}
                style={{ 
                  left: `${hero.x}%`, 
                  top: `${hero.y}%`,
                  transform: 'translate(-50%, -50%)',
                  background: `radial-gradient(circle, ${biome.glow}, transparent 70%)`
                }}
              />
            );
          })}

          {/* Connectors (Constellation effect) */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20">
             {heroes.map((hero, i) => {
               if (i === 0) return null;
               const prevHero = heroes[i-1];
               return (
                 <motion.line
                   key={`line-${hero.id}`}
                   x1={`${prevHero.x}%`} y1={`${prevHero.y}%`}
                   x2={`${hero.x}%`} y2={`${hero.y}%`}
                   stroke="url(#constellation-grad)"
                   strokeWidth="1"
                   strokeDasharray="4 4"
                   initial={{ pathLength: 0 }}
                   animate={{ pathLength: 1 }}
                   transition={{ duration: 2 }}
                 />
               );
             })}
             <defs>
               <linearGradient id="constellation-grad" x1="0" y1="0" x2="1" y2="1">
                 <stop offset="0%" stopColor="#7c3aed" stopOpacity="0.5" />
                 <stop offset="100%" stopColor="#ec4899" stopOpacity="0.5" />
               </linearGradient>
             </defs>
          </svg>

          {/* Hero Kingdoms (Pins) */}
          {heroes.map((hero) => {
            const biome = HERO_BIOMES.find(b => b.id === hero.biome) || HERO_BIOMES[0];
            const Icon = biome.icon;
            
            return (
              <motion.div
                key={hero.id}
                className="absolute"
                style={{ left: `${hero.x}%`, top: `${hero.y}%`, transform: 'translate(-50%, -50%)' }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: 'spring', delay: 1 + (parseInt(hero.id) * 0.1) }}
              >
                <div 
                  className="relative cursor-pointer group"
                  onClick={() => setSelectedHero(hero)}
                >
                  {/* Outer Floating Ring */}
                  <motion.div 
                    animate={{ rotate: 360 }}
                    transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
                    className="absolute -inset-6 border border-white/5 rounded-full border-dashed opacity-50 group-hover:opacity-100 transition-opacity"
                  />

                  {/* Pin Orb */}
                  <motion.div
                    whileHover={{ scale: 1.1, y: -5 }}
                    className="relative flex flex-col items-center gap-3"
                  >
                    <div className={`w-16 h-16 rounded-[1.5rem] ${biome.bg} backdrop-blur-md border border-white/10 flex items-center justify-center shadow-[0_10px_40px_rgba(0,0,0,0.5)] group-hover:border-white/30 transition-all duration-300 overflow-hidden`}>
                      <Icon className={`w-8 h-8 ${biome.color} group-hover:scale-110 transition-transform`} />
                      
                      {/* Inner Shine */}
                      <div className="absolute inset-0 bg-gradient-to-tr from-white/10 via-transparent to-transparent pointer-events-none" />
                      
                      {/* Floating Particles */}
                      <div className="absolute inset-0 pointer-events-none">
                        {particles.map((p, idx) => (
                          <motion.div
                            key={idx}
                            className="absolute w-1 h-1 bg-white rounded-full opacity-20"
                            animate={{ 
                              y: [-10, 40], 
                              opacity: [0, 1, 0],
                              x: [p.x, p.x + (p.yOffset - 10)]
                            }}
                            transition={{ duration: p.duration, repeat: Infinity }}
                            style={{ left: `${p.x}%` }}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Name Tag */}
                    <div className="flex flex-col items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0">
                      <p className="text-xs font-bold text-white tracking-widest uppercase">{hero.name}</p>
                      <div className="w-8 h-0.5 bg-indigo-500 rounded-full" />
                    </div>
                  </motion.div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* --- EPIC SIDEBAR --- */}
      <AnimatePresence>
        {selectedHero && (
          <motion.div
            initial={{ x: 500 }}
            animate={{ x: 0 }}
            exit={{ x: 500 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute top-8 right-8 bottom-8 w-[22rem] z-40 bg-black/40 backdrop-blur-3xl border border-white/10 rounded-[2rem] p-8 shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col overflow-hidden"
          >
            {/* Close Button */}
            <button 
              onClick={() => setSelectedHero(null)}
              className="absolute top-6 right-6 p-2 bg-white/5 hover:bg-white/10 rounded-xl transition-all border border-white/5"
            >
              <X className="w-5 h-5 text-slate-400 hover:text-white" />
            </button>

            <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-8">
              {/* Header */}
              <div className="text-center pt-4">
                <motion.div 
                  layoutId={`icon-${selectedHero.id}`}
                  className={`w-24 h-24 mx-auto rounded-[2rem] ${HERO_BIOMES.find(b => b.id === selectedHero.biome)?.bg} flex items-center justify-center border border-white/20 shadow-2xl mb-4 relative overflow-hidden`}
                >
                   {(() => {
                     const biome = HERO_BIOMES.find(b => b.id === selectedHero.biome);
                     const Icon = biome?.icon || Castle;
                     return <Icon className={`w-12 h-12 ${biome?.color}`} />;
                   })()}
                   <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/40 to-transparent" />
                </motion.div>
                <h3 className="text-2xl font-bold text-white tracking-tight leading-none mb-2">{selectedHero.name}</h3>
                <p className="text-magical-indigo text-xs font-bold uppercase tracking-[0.2em]">
                  {HERO_BIOMES.find(b => b.id === selectedHero.biome)?.label}
                </p>
              </div>

              {/* Lore Section */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Star className="w-3 h-3 text-magical-indigo fill-magical-indigo" />
                  <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em]">Krallık Efsanesi</h4>
                  <div className="h-px flex-1 bg-white/5" />
                </div>
                <div className="relative p-5 rounded-2xl bg-gradient-to-b from-white/[0.03] to-transparent border border-white/5">
                  <Sparkles className="absolute top-2 right-2 w-4 h-4 text-white/5" />
                  <p className="text-sm leading-relaxed text-slate-300 italic font-light">
                    {HERO_BIOMES.find(b => b.id === selectedHero.biome)?.description}
                  </p>
                </div>
              </div>

              {/* Timeline / Adventures */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <BookOpen className="w-3 h-3 text-magical-indigo" />
                  <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em]">Son Maceralar</h4>
                  <div className="h-px flex-1 bg-white/5" />
                </div>
                <div className="space-y-3">
                  {[1, 2].map((i) => (
                    <motion.div 
                      key={i}
                      whileHover={{ x: 5 }}
                      className="flex items-center gap-4 p-4 bg-white/5 rounded-2xl border border-white/5 hover:bg-white/[0.07] hover:border-violet-500/30 transition-all cursor-pointer group"
                    >
                      <div className="w-12 h-12 rounded-xl bg-violet-500/10 flex items-center justify-center text-violet-400 group-hover:bg-violet-500 group-hover:text-white transition-all shadow-inner">
                        <BookOpen className="w-6 h-6" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-white truncate group-hover:text-magical-rose transition-colors">Ejderha ile Dans {i}</p>
                        <p className="text-[10px] text-slate-500 mt-1">2 gün önce okundu</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>

            <Button className="w-full bg-magical-indigo hover:bg-magical-violet text-white font-bold py-7 rounded-2xl shadow-xl shadow-magical-indigo/10 mt-6 group overflow-hidden relative">
              <span className="relative z-10 flex items-center justify-center gap-3">
                Tüm Maceraları Gör
                <ChevronLeft className="w-4 h-4 rotate-180 group-hover:translate-x-1 transition-transform" />
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-magical-indigo to-magical-violet opacity-0 group-hover:opacity-100 transition-opacity" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Status Bar */}
      <motion.div 
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="absolute bottom-8 left-8 z-30 flex items-center gap-3 px-5 py-2.5 bg-black/40 backdrop-blur-2xl rounded-2xl border border-white/10 group cursor-default"
      >
        <div className="relative w-2.5 h-2.5">
          <div className="absolute inset-0 rounded-full bg-emerald-500 animate-ping opacity-75" />
          <div className="relative w-2.5 h-2.5 rounded-full bg-emerald-500" />
        </div>
        <span className="text-[11px] font-bold text-slate-300 uppercase tracking-widest">Canlı Dünya: <span className="text-white">Aktif</span></span>
        <div className="w-px h-3 bg-white/10 mx-1" />
        <Sparkles className="w-3 h-3 text-amber-400 group-hover:scale-125 transition-transform" />
      </motion.div>
    </div>
  );
};

const X = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);
