import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Map, ChevronRight, CornerDownRight, ShieldCheck, HeartPulse, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface StoryNode {
  id: string;
  text: string;
  image: string;
  choices?: {
    text: string;
    nextNodeId: string;
    icon?: React.ReactNode;
    color?: string;
  }[];
  isEnd?: boolean;
}

const STORY_DATA: Record<string, StoryNode> = {
  'start': {
    id: 'start',
    text: "Güneş yavaşça batarken, Eko adlı küçük ejderha ormanın derinliklerinde garip bir parıltı gördü. Bu parıltı, daha önce hiç görmediği mavi bir taştan geliyordu. Eko heyecanla taşa doğru yaklaştı ama aniden çalılıkların arkasından bir hışırtı duydu.",
    image: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&q=80&w=1200',
    choices: [
      { text: "Hemen mavi taşı alıp kaç!", nextNodeId: 'take_stone', color: 'from-amber-500 to-orange-500', icon: <Sparkles className="w-5 h-5"/> },
      { text: "Çalılıkların arkasında nelerin saklandığına bak.", nextNodeId: 'check_bushes', color: 'from-indigo-500 to-purple-500', icon: <ShieldCheck className="w-5 h-5"/> }
    ]
  },
  'take_stone': {
    id: 'take_stone',
    text: "Eko, alevlerini kullanarak taşı hızlıca kaptı ve gökyüzüne doğru uçmaya başladı. Taş elinde parıl parıl parlıyordu. Havada güvenle süzülürken mavi taşın bir harita olduğunu fark etti. Bu harita onu Kayıp Bulutlar Ülkesi'ne götürüyordu!",
    image: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&q=80&w=1200',
    choices: [
      { text: "Haritayı takip et ve maceraya atıl.", nextNodeId: 'cloud_country_end', color: 'from-cyan-500 to-blue-500', icon: <Map className="w-5 h-5"/> }
    ]
  },
  'check_bushes': {
    id: 'check_bushes',
    text: "Eko cesaretini topladı ve yavaşça çalılıklara doğru ilerledi. Bir de ne görsün? Orada kanadı incinmiş yavru bir Anka Kuşu duruyordu. Anka kuşu korkuyla Eko'ya bakıyordu. Mavi taş aslında Anka kuşunun yuvasından düşmüştü.",
    image: 'https://images.unsplash.com/photo-1444459094717-a39f1e3e0903?auto=format&fit=crop&q=80&w=1200',
    choices: [
      { text: "Mavi taşı ona geri ver ve dost ol.", nextNodeId: 'friendship_end', color: 'from-emerald-500 to-teal-500', icon: <HeartPulse className="w-5 h-5"/> }
    ]
  },
  'cloud_country_end': {
    id: 'cloud_country_end',
    text: "Eko, haritanın rehberliğinde bulutların üzerine çıktı. Orada efsanevi Pamuk Ejderhalarla tanıştı. Bu, serüveninin sadece ilk adımıydı ancak mavi taş onu yeni evine getirmişti.",
    image: 'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?auto=format&fit=crop&q=80&w=1200',
    isEnd: true
  },
  'friendship_end': {
    id: 'friendship_end',
    text: "Eko taşı dikkatlice Anka kuşunun yanına bıraktı. Kuş aniden parlamaya başladı ve iyileşti! İkisi o günden sonra en iyi arkadaş oldular ve gökyüzünde birlikte uçtular.",
    image: 'https://images.unsplash.com/photo-1535339450886-2580556157e7?auto=format&fit=crop&q=80&w=1200',
    isEnd: true
  }
};

export const InteractiveStoryPage = () => {
  const [currentNodeId, setCurrentNodeId] = useState<string>('start');
  const currentNode = STORY_DATA[currentNodeId];
  const [history, setHistory] = useState<string[]>(['start']);

  const handleChoice = (nextNodeId: string) => {
    setHistory([...history, nextNodeId]);
    setCurrentNodeId(nextNodeId);
  };

  const handleRestart = () => {
    setHistory(['start']);
    setCurrentNodeId('start');
  };

  return (
    <div className="max-w-4xl mx-auto py-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-black bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent flex items-center gap-3">
            <Map className="w-8 h-8 text-indigo-400" />
            İnteraktif Hikaye
          </h1>
          <p className="text-slate-400 mt-2">Seçimlerinle hikayenin kaderini sen belirle!</p>
        </div>
        
        {/* Progress Dots */}
        <div className="flex items-center gap-2">
          {history.map((id, idx) => (
            <div key={`${id}-${idx}`} className="flex items-center gap-2">
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="w-3 h-3 rounded-full bg-indigo-500 shadow-[0_0_10px_var(--tw-shadow-color)] shadow-indigo-500/50" 
              />
              {idx < history.length - 1 && <div className="w-4 h-0.5 bg-indigo-500/30" />}
            </div>
          ))}
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentNodeId}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.4 }}
          className="bg-[#0f1115] border border-white/10 rounded-3xl overflow-hidden shadow-2xl"
        >
          {/* Story Visual */}
          <div className="h-64 sm:h-80 w-full relative">
            <div className="absolute inset-0 bg-gradient-to-t from-[#0f1115] via-transparent to-transparent z-10" />
            <img 
              src={currentNode.image} 
              alt="Story scene" 
              className="w-full h-full object-cover"
            />
            
            {/* Tag */}
            <div className="absolute top-6 right-6 z-20 px-4 py-1.5 rounded-full bg-black/50 backdrop-blur-md border border-white/10 text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              Bölüm {history.length}
            </div>
          </div>

          <div className="p-8 sm:p-12 -mt-16 relative z-20">
            <p className="text-xl sm:text-2xl text-slate-200 leading-relaxed font-medium mb-12 drop-shadow-lg">
              {currentNode.text}
            </p>

            {currentNode.isEnd ? (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="text-center p-8 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/30"
              >
                <div className="w-16 h-16 bg-indigo-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Star className="w-8 h-8 text-indigo-400 fill-current" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">Hikayenin Sonu</h3>
                <p className="text-slate-400 mb-6">Maceran burada sona erdi. Acaba diğer yolları seçseydin neler yaşanırdı?</p>
                <Button 
                  onClick={handleRestart}
                  className="bg-white text-black hover:bg-slate-200 rounded-xl px-8"
                >
                  Baştan Başla
                </Button>
              </motion.div>
            ) : (
              <div className="space-y-4">
                <h4 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2 mb-6">
                  <CornerDownRight className="w-4 h-4" /> Ne yapacaksın?
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {currentNode.choices?.map((choice, idx) => (
                    <motion.button
                      key={idx}
                      whileHover={{ scale: 1.02, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleChoice(choice.nextNodeId)}
                      className={`h-full text-left p-6 rounded-2xl bg-gradient-to-br ${choice.color || 'from-slate-800 to-slate-900'} hover:shadow-xl hover:shadow-indigo-500/20 transition-all border border-white/10 flex flex-col justify-between gap-4 group`}
                    >
                      <div className="p-3 bg-white/10 rounded-xl w-fit group-hover:bg-white/20 transition-colors">
                        {choice.icon || <ChevronRight className="w-5 h-5 text-white" />}
                      </div>
                      <span className="text-lg font-bold text-white group-hover:text-white/90">
                        {choice.text}
                      </span>
                    </motion.button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};
