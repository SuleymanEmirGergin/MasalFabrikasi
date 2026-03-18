import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Star, Music, CloudMoon, Timer, Play, Pause, Volume2 } from 'lucide-react';

interface NightStory {
  id: string;
  title: string;
  duration: string;
  type: 'story' | 'sound';
  cover: string;
}

const NIGH_STORIES: NightStory[] = [
  { id: '1', title: 'Uyku Ormanının Sakinleri', duration: '12:45', type: 'story', cover: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&q=80&w=800' },
  { id: '2', title: 'Gökyüzü Gemisi Rüyası', duration: '15:20', type: 'story', cover: 'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?auto=format&fit=crop&q=80&w=800' },
  { id: '3', title: 'Hafif Yağmur Sesi', duration: '60:00', type: 'sound', cover: 'https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&q=80&w=800' },
  { id: '4', title: 'Okyanus Dalgaları', duration: '45:00', type: 'sound', cover: 'https://images.unsplash.com/photo-1439405326854-014607f694d7?auto=format&fit=crop&q=80&w=800' },
];

export const BedtimeModePage = () => {
  const [activeTab, setActiveTab] = useState<'story' | 'sound'>('story');
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [sleepTimer, setSleepTimer] = useState<number | null>(null);

  // Background stars generation
  const [stars] = useState<{x: number, y: number, size: number, delay: number, duration: number}[]>(() => 
    Array.from({ length: 50 }).map(() => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2 + 1,
      delay: Math.random() * 3,
      duration: 3 + Math.random() * 2
    }))
  );

  const togglePlay = (id: string) => {
    if (playingId === id) {
      setPlayingId(null);
    } else {
      setPlayingId(id);
    }
  };

  const storiesToShow = NIGH_STORIES.filter(s => s.type === activeTab);

  return (
    <div className="relative min-h-[85vh] rounded-3xl overflow-hidden bg-[#0a0f1d] text-slate-200 p-8 shadow-2xl animate-in fade-in duration-1000">
      {/* Dynamic Star Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/40 via-[#0a0f1d] to-[#0a0f1d]" />
        {stars.map((star, i) => (
          <motion.div
            key={i}
            className="absolute bg-white rounded-full opacity-60"
            style={{
              left: `${star.x}%`,
              top: `${star.y}%`,
              width: star.size,
              height: star.size,
            }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: star.duration,
              repeat: Infinity,
              delay: star.delay,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 backdrop-blur-md">
              <Moon className="w-8 h-8 text-indigo-300" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white tracking-wide">
                Uyku Vakti
              </h1>
              <p className="text-indigo-200/60 mt-1">Sakinleş ve tatlı rüyalara dal...</p>
            </div>
          </div>

          <div className="flex items-center gap-2 p-1.5 bg-black/40 border border-white/5 rounded-2xl backdrop-blur-md">
            <button
              onClick={() => setActiveTab('story')}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'story'
                  ? 'bg-indigo-500/20 text-indigo-200 shadow-inner'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <CloudMoon className="w-4 h-4" /> Masallar
            </button>
            <button
              onClick={() => setActiveTab('sound')}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'sound'
                  ? 'bg-indigo-500/20 text-indigo-200 shadow-inner'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Music className="w-4 h-4" /> Rahatlatıcı Sesler
            </button>
          </div>
        </div>

        {/* Player UI if something is playing */}
        <AnimatePresence>
          {playingId && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-gradient-to-r from-indigo-900/40 to-slate-900/40 border border-indigo-500/20 rounded-3xl p-6 backdrop-blur-xl shadow-2xl flex flex-col md:flex-row items-center gap-6"
            >
              <div className="w-20 h-20 rounded-2xl overflow-hidden shrink-0 shadow-lg">
                <img src={NIGH_STORIES.find(s => s.id === playingId)?.cover} alt="cover" className="w-full h-full object-cover" />
              </div>
              
              <div className="flex-1 text-center md:text-left">
                <div className="flex items-center justify-center md:justify-start gap-2 mb-1">
                  <Volume2 className="w-4 h-4 text-indigo-400" />
                  <span className="text-xs font-semibold text-indigo-400 uppercase tracking-widest">Şu An Çalıyor</span>
                </div>
                <h3 className="text-xl font-bold text-white">
                  {NIGH_STORIES.find(s => s.id === playingId)?.title}
                </h3>
                
                {/* Visualizer bars */}
                <div className="flex items-center justify-center md:justify-start gap-1 mt-4 h-6">
                  {[1,2,3,4,5,6,7].map((i) => (
                    <motion.div
                      key={i}
                      className="w-1.5 bg-indigo-500 rounded-full"
                      animate={{ height: ['20%', '100%', '40%', '80%', '20%'] }}
                      transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.1 }}
                    />
                  ))}
                </div>
              </div>

              <div className="flex flex-col items-center gap-4 shrink-0 border-t md:border-t-0 md:border-l border-white/10 pt-4 md:pt-0 md:pl-6 w-full md:w-auto">
                <div className="flex items-center gap-3 w-full justify-center">
                  <button 
                    onClick={() => setSleepTimer(sleepTimer === 15 ? null : 15)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${sleepTimer === 15 ? 'bg-indigo-500/20 border-indigo-500 text-indigo-200' : 'border-white/10 text-slate-400 hover:text-white'}`}
                  >
                    <Timer className="w-3.5 h-3.5" /> 15 Dk
                  </button>
                  <button 
                    onClick={() => setSleepTimer(sleepTimer === 30 ? null : 30)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${sleepTimer === 30 ? 'bg-indigo-500/20 border-indigo-500 text-indigo-200' : 'border-white/10 text-slate-400 hover:text-white'}`}
                  >
                    <Timer className="w-3.5 h-3.5" /> 30 Dk
                  </button>
                </div>
                
                <button 
                  onClick={() => togglePlay(playingId)}
                  className="w-12 h-12 rounded-full bg-white text-[#0a0f1d] flex items-center justify-center hover:scale-105 transition-transform"
                >
                  <Pause className="w-5 h-5 fill-current" />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Content Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <AnimatePresence mode="popLayout">
            {storiesToShow.map((story) => (
              <motion.div
                key={story.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className={`group relative rounded-2xl overflow-hidden cursor-pointer border transition-all duration-500 ${playingId === story.id ? 'border-indigo-500 shadow-[0_0_30px_-5px_var(--tw-shadow-color)] shadow-indigo-500/30' : 'border-white/5 hover:border-white/20'}`}
                onClick={() => togglePlay(story.id)}
              >
                <div className="absolute inset-0 bg-black/60 group-hover:bg-black/40 transition-colors z-10" />
                <img src={story.cover} alt={story.title} className="w-full h-48 object-cover transform group-hover:scale-110 transition-transform duration-700" />
                
                <div className="absolute inset-0 z-20 p-5 flex flex-col justify-end bg-gradient-to-t from-[#0a0f1d] via-[#0a0f1d]/80 to-transparent">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-indigo-300 flex items-center gap-1">
                      <Star className="w-3 h-3" /> {story.duration}
                    </span>
                    <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm group-hover:bg-white group-hover:text-black transition-colors">
                      {playingId === story.id ? (
                        <Pause className="w-4 h-4" />
                      ) : (
                        <Play className="w-4 h-4 ml-0.5" />
                      )}
                    </button>
                  </div>
                  <h3 className="text-lg font-bold text-white/90 group-hover:text-white transition-colors">
                    {story.title}
                  </h3>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};
