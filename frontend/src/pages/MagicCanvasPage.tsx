import { useRef, useState } from 'react';
import { DrawingCanvas, type DrawingCanvasRef } from '@/components/DrawingCanvas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { motion, AnimatePresence } from 'framer-motion';
import { Wand2, Eraser, Loader2, Download, Pencil, ImagePlus, Sparkles } from 'lucide-react';
import api from '@/api/client';
import { AxiosError } from 'axios';

const STYLES = [
  { id: 'anime', label: '🎌 Anime', prompt: 'anime style, vibrant, detailed' },
  { id: 'watercolor', label: '🎨 Suluboya', prompt: 'watercolor painting, soft, artistic' },
  { id: 'pixel', label: '👾 Piksel', prompt: 'pixel art, retro game style, 8-bit' },
  { id: 'realistic', label: '📷 Gerçekçi', prompt: 'photorealistic, detailed, cinematic' },
  { id: 'fairy', label: '✨ Peri Masalı', prompt: 'fairy tale illustration, dreamy, magical glow' },
  { id: 'oil', label: '🖼️ Yağlıboya', prompt: 'oil painting, impressionist, textured' },
];

const LOADING_MSGS = [
  'Sihir tozu saçılıyor ✨',
  'Renkler uçuyor 🎨',
  'Pikseller dans ediyor 💃',
  'Hayal gücü şekilleniyor 🌟',
];

export const MagicCanvasPage = () => {
  const canvasRef = useRef<DrawingCanvasRef>(null);
  const [tab, setTab] = useState<'draw' | 'upload'>('draw');
  const [prompt, setPrompt] = useState<string>('');
  const [selectedStyle, setSelectedStyle] = useState<string>('fairy');
  const [isGenerating, setIsGenerating] = useState(false);
  const [loadingMsgIdx, setLoadingMsgIdx] = useState(0);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleClear = () => {
    canvasRef.current?.clear();
    setResultImage(null);
    setUploadPreview(null);
    setUploadFile(null);
    setError(null);
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadFile(file);
    const url = URL.createObjectURL(file);
    setUploadPreview(url);
    setResultImage(null);
    setError(null);
  };

  const handleGenerate = async () => {
    setError(null);
    setResultImage(null);

    // Start loading message cycle
    let msgIdx = 0;
    const msgInterval = setInterval(() => {
      msgIdx = (msgIdx + 1) % LOADING_MSGS.length;
      setLoadingMsgIdx(msgIdx);
    }, 1500);

    setIsGenerating(true);
    try {
      const style = STYLES.find((s) => s.id === selectedStyle);
      const stylePrompt = style ? style.prompt : '';
      const fullPrompt = [prompt.trim(), stylePrompt].filter(Boolean).join(', ');

      let file: File | null = null;
      if (tab === 'draw') {
        const canvas = canvasRef.current;
        if (!canvas || canvas.isEmpty()) {
          setError('Lütfen önce bir çizim yapın!');
          return;
        }
        file = await canvas.getFile();
      } else {
        if (!uploadFile) {
          setError('Lütfen bir görsel yükleyin!');
          return;
        }
        file = uploadFile;
      }
      if (!fullPrompt) {
        setError('Lütfen bir açıklama yazın!');
        return;
      }
      if (!file) throw new Error('Dosya alınamadı');

      const formData = new FormData();
      formData.append('file', file);
      formData.append('prompt', fullPrompt);

      const response = await api.post('/magic-canvas/generate', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResultImage(response.data.generated_image);
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || 'Sihir yaparken bir hata oluştu.');
      } else if ((err as Error)?.message !== 'Lütfen') {
        setError('Beklenmeyen bir hata oluştu.');
      }
    } finally {
      clearInterval(msgInterval);
      setIsGenerating(false);
      setLoadingMsgIdx(0);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <div className="p-3 bg-violet-500/20 rounded-xl">
          <Wand2 className="w-8 h-8 text-violet-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            Büyülü Tuval
          </h1>
          <p className="text-slate-400 mt-0.5">Çiz veya görsel yükle — yapay zeka büyüsünü yapsın!</p>
        </div>
      </motion.div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-center"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tabs */}
      <div className="flex gap-2 bg-white/5 p-1.5 rounded-xl w-fit border border-white/10">
        {[
          { id: 'draw', icon: Pencil, label: 'Çizim Yap' },
          { id: 'upload', icon: ImagePlus, label: 'Görsel Yükle' },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id as 'draw' | 'upload')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.id
                ? 'bg-violet-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Input Section */}
        <Card className="p-4 bg-white/5 border-white/10 backdrop-blur-sm space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="font-semibold text-lg text-white">
              {tab === 'draw' ? 'Çizim Alanı' : 'Görsel Yükle'}
            </h2>
            <Button variant="ghost" size="sm" onClick={handleClear} className="text-slate-400 hover:text-white">
              <Eraser className="w-4 h-4 mr-2" />
              Temizle
            </Button>
          </div>

          <AnimatePresence mode="wait">
            {tab === 'draw' ? (
              <motion.div
                key="draw"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="aspect-square w-full rounded-xl overflow-hidden border border-white/20 shadow-inner"
              >
                <DrawingCanvas ref={canvasRef} />
              </motion.div>
            ) : (
              <motion.label
                key="upload"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center aspect-square w-full rounded-xl border-2 border-dashed border-white/20 hover:border-violet-500/50 bg-black/20 hover:bg-violet-500/5 transition-all cursor-pointer overflow-hidden"
              >
                {uploadPreview ? (
                  <img src={uploadPreview} alt="Preview" className="w-full h-full object-cover" />
                ) : (
                  <>
                    <ImagePlus className="w-12 h-12 text-slate-600 mb-3" />
                    <span className="text-slate-400 text-sm">Görsel seçmek için tıkla</span>
                    <span className="text-slate-600 text-xs mt-1">JPG, PNG, WEBP</span>
                  </>
                )}
                <input type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
              </motion.label>
            )}
          </AnimatePresence>

          {/* Style Chips */}
          <div>
            <p className="text-xs font-medium text-slate-400 mb-2 flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Stil Seç
            </p>
            <div className="flex flex-wrap gap-2">
              {STYLES.map((style) => (
                <button
                  key={style.id}
                  onClick={() => setSelectedStyle(style.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    selectedStyle === style.id
                      ? 'bg-violet-600 border-violet-500 text-white'
                      : 'bg-black/20 border-white/10 text-slate-400 hover:border-white/30'
                  }`}
                >
                  {style.label}
                </button>
              ))}
            </div>
          </div>

          {/* Prompt */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Açıklama (isteğe bağlı)</label>
            <Input
              placeholder="Örn: Uçan mor bir ejderha"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="bg-black/20 border-white/10 text-white placeholder:text-slate-500"
            />
          </div>

          <Button
            className="w-full bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:opacity-90 transition-opacity font-bold"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <Loader2 className="w-5 h-5 animate-spin mr-2" />
            ) : (
              <Wand2 className="w-5 h-5 mr-2" />
            )}
            {isGenerating ? 'Sihir Yapılıyor...' : 'Sihir Yap!'}
          </Button>
        </Card>

        {/* Result Section */}
        <Card className="p-4 bg-white/5 border-white/10 backdrop-blur-sm space-y-4 flex flex-col">
          <h2 className="font-semibold text-lg text-white">Sihirli Sonuç</h2>

          <div className="flex-1 aspect-square w-full rounded-xl overflow-hidden border border-white/10 border-dashed flex items-center justify-center bg-black/20 relative group">
            {resultImage ? (
              <>
                <motion.img
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  src={resultImage}
                  alt="Magic Result"
                  className="w-full h-full object-cover rounded-xl"
                />
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-xl">
                  <a href={resultImage} download="sihirli_tuval.png" target="_blank" rel="noreferrer">
                    <Button variant="secondary" className="rounded-full">
                      <Download className="w-4 h-4 mr-2" />
                      İndir
                    </Button>
                  </a>
                </div>
              </>
            ) : isGenerating ? (
              <div className="text-center space-y-6 px-8">
                {/* Animated rings */}
                <div className="relative w-24 h-24 mx-auto">
                  <motion.div
                    className="absolute inset-0 rounded-full border-4 border-violet-500/30"
                    animate={{ scale: [1, 1.4, 1], opacity: [0.8, 0, 0.8] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  <motion.div
                    className="absolute inset-2 rounded-full border-4 border-fuchsia-500/40"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.8, 0, 0.8] }}
                    transition={{ duration: 2, repeat: Infinity, delay: 0.4 }}
                  />
                  <div className="absolute inset-4 rounded-full bg-violet-600/30 flex items-center justify-center">
                    <Wand2 className="w-6 h-6 text-violet-300" />
                  </div>
                </div>
                <AnimatePresence mode="wait">
                  <motion.p
                    key={loadingMsgIdx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="text-violet-300 font-medium text-sm"
                  >
                    {LOADING_MSGS[loadingMsgIdx]}
                  </motion.p>
                </AnimatePresence>
              </div>
            ) : (
              <div className="text-center text-slate-600">
                <Wand2 className="w-12 h-12 mx-auto mb-2 opacity-20" />
                <p className="text-sm">Çizimini yap ve sihri başlat!</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
