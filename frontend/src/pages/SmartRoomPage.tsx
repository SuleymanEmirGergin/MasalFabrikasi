import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Lightbulb,
  Wifi,
  WifiOff,
  TreePine,
  Waves,
  Rocket,
  Castle,
  Sun,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Atmosphere {
  id: string;
  name: string;
  icon: React.ElementType;
  description: string;
  gradient: string;
  glowColor: string;
  palette: string[];
  ambientText: string;
}

const ATMOSPHERES: Atmosphere[] = [
  {
    id: 'forest',
    name: 'Büyülü Orman',
    icon: TreePine,
    description: 'Uğultulu rüzgar, nemli yosunlar ve parlayan ateş böcekleri.',
    gradient: 'from-emerald-900/40 to-green-800/20',
    glowColor: 'rgba(52, 211, 153, 0.3)',
    palette: ['#064e3b', '#065f46', '#047857', '#10b981', '#6ee7b7'],
    ambientText: '🌲 Orman sesleri aktif',
  },
  {
    id: 'ocean',
    name: 'Deniz Altı',
    icon: Waves,
    description: 'Derin mavi sular, biolüminesans balıklar ve sessiz akıntılar.',
    gradient: 'from-blue-900/40 to-cyan-800/20',
    glowColor: 'rgba(34, 211, 238, 0.3)',
    palette: ['#0c4a6e', '#0369a1', '#0284c7', '#38bdf8', '#7dd3fc'],
    ambientText: '🌊 Dalga sesi aktif',
  },
  {
    id: 'space',
    name: 'Uzay Macerası',
    icon: Rocket,
    description: 'Yıldız tozu, gezegen halkaları ve sessiz evrenin büyüsü.',
    gradient: 'from-indigo-900/40 to-purple-900/20',
    glowColor: 'rgba(139, 92, 246, 0.3)',
    palette: ['#1e1b4b', '#312e81', '#4338ca', '#818cf8', '#c7d2fe'],
    ambientText: '🚀 Kozmik sesler aktif',
  },
  {
    id: 'castle',
    name: 'Sihirli Kale',
    icon: Castle,
    description: 'Meşale ışığı, gece yarısı büyüleri ve antik büyücü odaları.',
    gradient: 'from-amber-900/40 to-orange-800/20',
    glowColor: 'rgba(251, 191, 36, 0.3)',
    palette: ['#78350f', '#92400e', '#b45309', '#f59e0b', '#fcd34d'],
    ambientText: '🏰 Meşale çıtırtısı aktif',
  },
  {
    id: 'desert',
    name: 'Sihirli Çöl',
    icon: Sun,
    description: 'Sıcak kumlar, yıldızlı çöl geceleri ve gizemli vaahalar.',
    gradient: 'from-rose-900/40 to-orange-700/20',
    glowColor: 'rgba(251, 113, 133, 0.3)',
    palette: ['#881337', '#9f1239', '#be185d', '#f43f5e', '#fb7185'],
    ambientText: '🌅 Çöl rüzgarı aktif',
  },
];

type BridgeState = 'disconnected' | 'connecting' | 'connected';

// Stable particle positions computed once, outside component
const PARTICLES = Array.from({ length: 6 }, (_, i) => ({
  width: [64, 88, 52, 72, 96, 60][i],
  height: [48, 72, 88, 56, 64, 80][i],
  left: [10, 25, 45, 62, 78, 88][i] + '%',
  top: [15, 60, 30, 75, 20, 55][i] + '%',
}));

export const SmartRoomPage = () => {
  const [selectedAtmosphere, setSelectedAtmosphere] = useState<Atmosphere>(ATMOSPHERES[0]);
  const [bridgeState, setBridgeState] = useState<BridgeState>('disconnected');
  const [activeColor, setActiveColor] = useState<string | null>(null);
  const [lightIntensity, setLightIntensity] = useState(70);

  const connectBridge = async () => {
    setBridgeState('connecting');
    await new Promise((r) => setTimeout(r, 2000));
    setBridgeState('connected');
    setActiveColor(selectedAtmosphere.palette[2]);
  };

  const disconnectBridge = () => {
    setBridgeState('disconnected');
    setActiveColor(null);
  };

  const applyColor = (color: string) => {
    if (bridgeState !== 'connected') return;
    setActiveColor(color);
  };

  const applyAtmosphere = (atm: Atmosphere) => {
    setSelectedAtmosphere(atm);
    if (bridgeState === 'connected') {
      setActiveColor(atm.palette[2]);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <div className="p-3 bg-amber-500/20 rounded-xl">
          <Lightbulb className="w-8 h-8 text-amber-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
            Akıllı Oda & Atmosfer
          </h1>
          <p className="text-slate-400 mt-0.5">
            Masalın dünyasını odasına taşı — ışıklar hikayeyle dans etsin.
          </p>
        </div>
      </motion.div>

      {/* Live Preview Bar */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedAtmosphere.id}
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.98 }}
          transition={{ duration: 0.4 }}
          className={`relative overflow-hidden rounded-2xl border border-white/10 p-8 bg-gradient-to-br ${selectedAtmosphere.gradient} backdrop-blur-sm`}
          style={{ boxShadow: `0 0 60px ${selectedAtmosphere.glowColor}` }}
        >
          <div className="absolute inset-0 pointer-events-none opacity-20">
            {PARTICLES.map((p, i) => (
              <motion.div
                key={i}
                className="absolute rounded-full"
                style={{
                  width: p.width,
                  height: p.height,
                  background: selectedAtmosphere.palette[i % selectedAtmosphere.palette.length],
                  left: p.left,
                  top: p.top,
                  filter: 'blur(20px)',
                }}
                animate={{ opacity: [0.3, 0.7, 0.3], scale: [1, 1.2, 1] }}
                transition={{ duration: 3 + i, repeat: Infinity, delay: i * 0.5 }}
              />
            ))}
          </div>

          <div className="relative z-10 flex items-center gap-6">
            <div className="p-5 bg-black/30 rounded-2xl border border-white/10">
              <selectedAtmosphere.icon className="w-12 h-12 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{selectedAtmosphere.name}</h2>
              <p className="text-slate-300 mt-1 max-w-lg">{selectedAtmosphere.description}</p>
              {bridgeState === 'connected' && (
                <motion.span
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 inline-flex items-center gap-2 text-sm text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20"
                >
                  <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                  {selectedAtmosphere.ambientText}
                </motion.span>
              )}
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Atmosphere Selection */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-bold text-white">Atmosfer Seç</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {ATMOSPHERES.map((atm, i) => {
              const isSelected = selectedAtmosphere.id === atm.id;
              return (
                <motion.button
                  key={atm.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.07 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => applyAtmosphere(atm)}
                  className={`relative p-5 rounded-xl border-2 text-left transition-all duration-300 overflow-hidden ${
                    isSelected
                      ? 'border-white/40 bg-white/10'
                      : 'border-white/5 bg-white/3 hover:border-white/20 hover:bg-white/5'
                  }`}
                  style={isSelected ? { boxShadow: `0 0 20px ${atm.glowColor}` } : {}}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <atm.icon
                      className={`w-6 h-6 ${isSelected ? 'text-white' : 'text-slate-400'}`}
                    />
                    <span className={`font-bold ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                      {atm.name}
                    </span>
                    {isSelected && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="ml-auto"
                      >
                        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                      </motion.div>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-2">{atm.description}</p>
                  {/* Palette dots */}
                  <div className="flex gap-1 mt-3">
                    {atm.palette.map((color) => (
                      <span
                        key={color}
                        className="w-4 h-4 rounded-full border border-white/10"
                        style={{ background: color }}
                      />
                    ))}
                  </div>
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Right: IoT Panel */}
        <div className="space-y-5">
          {/* Bridge Connection */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-6"
          >
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              {bridgeState === 'connected' ? (
                <Wifi className="w-5 h-5 text-emerald-400" />
              ) : (
                <WifiOff className="w-5 h-5 text-slate-500" />
              )}
              Philips Hue Köprüsü
            </h3>

            {bridgeState === 'disconnected' && (
              <div className="space-y-3">
                <p className="text-sm text-slate-400">
                  Akıllı ampullerinizi kontrol etmek için Hue Bridge'e bağlanın.
                </p>
                <Button
                  onClick={connectBridge}
                  className="w-full bg-amber-500 hover:bg-amber-400 text-black font-bold"
                >
                  <Wifi className="w-4 h-4 mr-2" />
                  Köprüye Bağlan
                </Button>
              </div>
            )}

            {bridgeState === 'connecting' && (
              <div className="flex flex-col items-center gap-3 py-4">
                <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
                <p className="text-sm text-slate-400">Bridge aranıyor...</p>
              </div>
            )}

            {bridgeState === 'connected' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <div className="flex items-center gap-2 text-sm text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>Bağlı — 3 ampul tespit edildi</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={disconnectBridge}
                  className="w-full border-white/10 text-slate-400 hover:text-red-400 hover:border-red-400/30"
                >
                  Bağlantıyı Kes
                </Button>
              </motion.div>
            )}
          </motion.div>

          {/* Color Palette */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-6"
          >
            <h3 className="text-base font-bold text-white mb-4">Renk Paleti</h3>
            <div className="grid grid-cols-5 gap-2">
              {selectedAtmosphere.palette.map((color) => (
                <motion.button
                  key={color}
                  whileHover={{ scale: 1.15 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => applyColor(color)}
                  disabled={bridgeState !== 'connected'}
                  className={`relative aspect-square rounded-xl border-2 transition-all ${
                    activeColor === color
                      ? 'border-white scale-110'
                      : 'border-transparent hover:border-white/40'
                  } ${bridgeState !== 'connected' ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}`}
                  style={{ background: color }}
                  title={bridgeState !== 'connected' ? 'Önce Bridge\'e bağlanın' : color}
                >
                  {activeColor === color && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute inset-0 flex items-center justify-center"
                    >
                      <CheckCircle2 className="w-4 h-4 text-white drop-shadow-xl" />
                    </motion.div>
                  )}
                </motion.button>
              ))}
            </div>

            {/* Intensity Slider */}
            <div className="mt-5">
              <div className="flex justify-between text-xs text-slate-400 mb-2">
                <span>Parlaklık</span>
                <span className="font-mono text-white">{lightIntensity}%</span>
              </div>
              <input
                type="range"
                min={10}
                max={100}
                value={lightIntensity}
                onChange={(e) => setLightIntensity(Number(e.target.value))}
                disabled={bridgeState !== 'connected'}
                className="w-full accent-amber-400 disabled:opacity-40"
              />
            </div>

            {activeColor && bridgeState === 'connected' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4 p-3 rounded-xl border border-white/10"
                style={{
                  background: `${activeColor}22`,
                  borderColor: `${activeColor}44`,
                  boxShadow: `0 0 20px ${activeColor}33`,
                }}
              >
                <p className="text-xs text-center text-slate-300">
                  Aktif Renk:{' '}
                  <span className="font-mono font-bold" style={{ color: activeColor }}>
                    {activeColor.toUpperCase()}
                  </span>
                </p>
              </motion.div>
            )}

            {bridgeState !== 'connected' && (
              <p className="text-xs text-center text-slate-500 mt-4 italic">
                Renk kontrolü için Bridge'e bağlanın
              </p>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
};
