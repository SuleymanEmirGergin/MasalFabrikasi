import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { MagicCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  BookOpen, 
  Download,
  Share2,
  Maximize2,
  Type,
  Moon,
  Sun
} from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';

export const StoryViewerPage = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [fontSize, setFontSize] = useState(18);
  const [theme, setTheme] = useState<'dark' | 'sepia'>('dark');
  const [speechRate, setSpeechRate] = useState(1);
  const [progress, setProgress] = useState(0);
  
  const synth = useRef<SpeechSynthesis | null>(null);
  const utterance = useRef<SpeechSynthesisUtterance | null>(null);

  // Dummy story data
  const story = {
    title: "Cesur Tavşan ve Kristal Havuç",
    author: "Masal Fabrikası AI",
    date: "22 Mayıs 2024",
    content: `Bir varmış bir yokmuş, uzak diyarların en yeşil ormanında pofuduk kuyruğu ve meraklı gözleriyle tanınan Cesur Tavşan yaşarmış. Cesur Tavşan, diğer tavşanlar gibi sadece lahana kovalamaz, gökyüzündeki yıldızların sırlarını merak edermiş.

Bir sabah, ormanın en yaşlı meşesi ona bir sır fısıldamış: "Altın Vadi'nin derinliklerinde, sadece kalbi sevgi dolu olanların görebileceği Kristal Havuç parlıyor. Onu bulan, ormana sonsuz bahar getirecek."

Cesur Tavşan, çantasını hazırlamış ve yola koyulmuş. Dereleri aşmış, tepelerden geçmiş. Yolculuğu sırasında şarkı söyleyen nehirlerle ve dans eden çiçeklerle karşılaşmış. Her adımında doğanın mucizelerine bir kez daha hayran kalmış.

Birden karşısına uykucu bir ayı çıkmış. Ayı yolu kapatmış, horul horul uyuyormuş. Cesur Tavşan korkmak yerine, ayının yanına kıvrılmış ve en sevdiği ninniyi mırıldanmaya başlamış. Ayı o kadar güzel bir rüyaya dalmış ki, bir gülümsemeyle yana çekilmiş.

Sonunda Altın Vadi'ye vardığında, mağaranın ortasında tam da meşenin dediği gibi parlayan o muazzam Kristal Havuç'u görmüş. Ama o ne? Havuç, ışığını sadece tavşan ona dokunduğunda değil, ormandaki tüm dostlarını düşündüğünde yaymaya başlamış.

Cesur Tavşan anlamış ki, gerçek sihir paylaşmaktaydı. Havucu aldığı gibi ormanına geri dönmüş. O günden sonra ormanda hiç kış yaşanmamış, her yer her zaman çiçek açmış ve tüm hayvanlar barış içinde yaşamışlar.`,
    tags: ["Macera", "Dostluk", "Sihir"],
    audioUrl: "#"
  };

  useEffect(() => {
    synth.current = window.speechSynthesis;
    return () => {
      synth.current?.cancel();
    };
  }, []);

  useEffect(() => {
    if (utterance.current) {
      utterance.current.rate = speechRate;
    }
  }, [speechRate]);

  const handleTogglePlay = () => {
    if (!synth.current) return;

    if (isPlaying) {
      synth.current.pause();
      setIsPlaying(false);
    } else {
      if (synth.current.paused) {
        synth.current.resume();
        setIsPlaying(true);
      } else {
        // Start from beginning
        const u = new SpeechSynthesisUtterance(story.content);
        u.lang = 'tr-TR';
        u.rate = speechRate;
        
        u.onend = () => {
          setIsPlaying(false);
          setProgress(0);
        };

        u.onboundary = (event) => {
          const totalLength = story.content.length;
          const currentPos = event.charIndex;
          setProgress((currentPos / totalLength) * 100);
        };

        utterance.current = u;
        synth.current.speak(u);
        setIsPlaying(true);
      }
    }
  };

  return (
    <div className={`min-h-[calc(100vh-4rem)] transition-colors duration-500 ${
      theme === 'sepia' ? 'bg-[#f4ecd8] text-[#433422]' : 'bg-transparent text-white'
    }`}>
      <div className="max-w-4xl mx-auto py-10 px-4 pb-32">
        {/* Header Actions */}
        <div className="flex justify-between items-center mb-8">
          <Button variant="ghost" size="icon" onClick={() => window.history.back()}>
            <SkipBack className="w-5 h-5" />
          </Button>
          
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="icon" 
              className="rounded-full border-white/10 bg-white/5 hover:bg-white/10"
              onClick={() => setFontSize(f => Math.min(f + 2, 28))}
            >
              <Type className="w-4 h-4" />
            </Button>
            <Button 
              variant="outline" 
              size="icon" 
              className="rounded-full border-white/10 bg-white/5 hover:bg-white/10"
              onClick={() => setTheme(t => t === 'dark' ? 'sepia' : 'dark')}
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>
            <Button 
              variant="outline" 
              size="icon" 
              className="rounded-full border-white/10 bg-white/5 hover:bg-white/10"
            >
              <Share2 className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Story Content */}
        <motion.div
           initial={{ opacity: 0, y: 20 }}
           animate={{ opacity: 1, y: 0 }}
           transition={{ duration: 0.8 }}
        >
          <div className="text-center mb-12">
            <div className="flex justify-center gap-2 mb-4">
              {story.tags.map(tag => (
                <Badge key={tag} variant="secondary" className="bg-magical-purple/20 text-magical-purple border-magical-purple/30">
                  {tag}
                </Badge>
              ))}
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-magical-purple to-magical-rose bg-clip-text text-transparent">
              {story.title}
            </h1>
            <p className={`text-sm ${theme === 'sepia' ? 'text-stone-600' : 'text-slate-400'}`}>
              {story.author} • {story.date}
            </p>
          </div>

          <MagicCard className={`p-8 md:p-12 leading-relaxed shadow-2xl border-none ${
            theme === 'sepia' ? 'bg-[#faf3e0] text-[#433422]' : 'bg-slate-900/60'
          }`}>
            <div 
              style={{ fontSize: `${fontSize}px` }}
              className="whitespace-pre-line transition-all duration-300 font-serif"
            >
              {story.content}
            </div>
            
            <div className="mt-12 pt-8 border-t border-white/5 flex justify-center">
              <div className="flex items-center gap-4 text-magical-rose">
                <div className="w-2 h-2 rounded-full bg-magical-rose animate-pulse" />
                <span className="text-sm font-medium tracking-widest uppercase">Son</span>
                <div className="w-2 h-2 rounded-full bg-magical-rose animate-pulse" />
              </div>
            </div>
          </MagicCard>
        </motion.div>
      </div>

      {/* Floating Audio Player */}
      <motion.div 
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className="fixed bottom-6 left-4 right-4 md:left-auto md:right-8 md:w-[400px] z-50"
      >
        <MagicCard className="bg-slate-900/90 border-white/10 shadow-magical-purple p-4 backdrop-blur-2xl">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-magical-purple to-magical-rose flex items-center justify-center shadow-lg">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1 overflow-hidden">
              <h4 className="text-sm font-semibold truncate text-white">{story.title}</h4>
              <p className="text-xs text-slate-400">
                {isPlaying ? 'Masalcı AI Seslendiriyor...' : 'Hazır'}
              </p>
            </div>
            <div className="flex gap-1">
              <Button size="icon" variant="ghost" className="text-white hover:bg-white/10">
                <SkipBack className="w-4 h-4" />
              </Button>
              <Button 
                size="icon" 
                className="bg-white text-slate-900 hover:bg-slate-200 rounded-full"
                onClick={handleTogglePlay}
              >
                {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
              </Button>
              <Button size="icon" variant="ghost" className="text-white hover:bg-white/10">
                <SkipForward className="w-4 h-4" />
              </Button>
            </div>
          </div>
          
          <div className="mt-4 flex items-center gap-3">
            <span className="text-[10px] text-slate-400 font-mono">
              {Math.floor(progress).toString().padStart(2, '0')}%
            </span>
            <Slider 
              value={[progress]} 
              max={100} 
              step={0.1} 
              className="flex-1"
            />
            <span className="text-[10px] text-slate-400 font-mono">100%</span>
          </div>

          <div className="mt-4 flex justify-between items-center border-t border-white/5 pt-3">
             <div className="flex items-center gap-2 group">
                <Volume2 className="w-4 h-4 text-slate-400 group-hover:text-white transition-colors" />
                <Slider defaultValue={[70]} max={100} step={1} className="w-20" />
             </div>
             
             <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/10">
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-tighter">Hız</span>
                <select 
                  className="bg-transparent text-[10px] text-white outline-none cursor-pointer"
                  value={speechRate}
                  onChange={(e) => {
                    setSpeechRate(parseFloat(e.target.value));
                    if (isPlaying) {
                      synth.current?.cancel();
                      setIsPlaying(false);
                    }
                  }}
                >
                  <option value="0.5" className="bg-slate-900">0.5x</option>
                  <option value="0.8" className="bg-slate-900">0.8x</option>
                  <option value="1" className="bg-slate-900">1.0x</option>
                  <option value="1.2" className="bg-slate-900">1.2x</option>
                  <option value="1.5" className="bg-slate-900">1.5x</option>
                </select>
             </div>

             <div className="flex gap-2">
                <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-white">
                  <Download className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-white">
                  <Maximize2 className="w-4 h-4" />
                </Button>
             </div>
          </div>
        </MagicCard>
      </motion.div>
    </div>
  );
};
