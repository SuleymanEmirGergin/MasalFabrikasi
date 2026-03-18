import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MicVocal,
  UploadCloud,
  Play,
  Square,
  Trash2,
  Volume2,
  CheckCircle2,
  ChevronRight,
  Mic,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useVoiceCloning, type ClonedVoice } from '@/api/hooks';
import { PremiumGate } from '@/components/PremiumGate';

const READING_TEXTS = [
  'Bir varmış bir yokmuş, uzak diyarlarda büyülü bir orman varmış. Bu ormanda konuşan hayvanlar yaşarmış.',
  'Küçük prenses her gün penceresinden yıldızlara bakardı. Onlara hikayeler anlatır, dilekler dilerdi.',
  'Denizin altında, mercanların arasında, mavi ışıltılı bir saray yükselirdi. Bu sarayda şarkı söyleyen balıklar yaşardı.',
];

const STEPS = ['İsim Ver', 'Kayıt Al', 'Tamamla'];

// Stable waveform bar heights (avoid Math.random in render)
const WAVEFORM_BARS = [60, 80, 45, 90, 55, 75, 40, 85, 65, 50, 70, 38, 88, 62, 78];

export const VoiceCloningPage = () => {
  const [step, setStep] = useState(0);
  const [voiceName, setVoiceName] = useState('');
  const [selectedText, setSelectedText] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [voices, setVoices] = useState<ClonedVoice[]>([]);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const timerRef = useRef<number | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const { loading, listVoices, cloneVoice, deleteVoice } = useVoiceCloning();

  // Fetch voices on mount
  useEffect(() => {
    listVoices().then(setVoices);
  }, [listVoices]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];
      const mr = new MediaRecorder(stream);
      mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setRecordedBlob(blob);
        stream.getTracks().forEach((t) => t.stop());
        setStep(2);
      };
      mr.start();
      mediaRecorderRef.current = mr;
      setIsRecording(true);
      setRecordingTime(0);
      timerRef.current = window.setInterval(() => setRecordingTime((p) => p + 1), 1000);
    } catch {
      alert('Mikrofon erişimi reddedildi. Lütfen tarayıcı izinlerini kontrol edin.');
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (timerRef.current) window.clearInterval(timerRef.current);
    mediaRecorderRef.current?.stop();
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setRecordedBlob(file);
    setStep(2);
  };

  const handleFinish = async () => {
    if (!voiceName.trim() || !recordedBlob) return;
    const result = await cloneVoice(voiceName.trim(), recordedBlob);
    if (result) {
      setVoices((prev) => [{ id: result.voice_id, name: result.name }, ...prev]);
      setVoiceName('');
      setRecordedBlob(null);
      setStep(0);
      setRecordingTime(0);
    }
  };

  const handleDelete = async (id: string) => {
    const ok = await deleteVoice(id);
    if (ok) setVoices((prev) => prev.filter((v) => v.id !== id));
  };

  const formatTime = (s: number) =>
    `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`;

  return (
    <PremiumGate 
      featureName="Sihirli Seslendirme" 
      description="Masalları kendi sesinle veya sevdiklerinin sesiyle dinletmek için Premium'a yüksel!"
    >
      <div className="max-w-5xl mx-auto space-y-8 pb-12">
        {/* Header */}
        <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-4"
        >
          <div className="p-3 bg-violet-500/20 rounded-xl">
                <MicVocal className="w-8 h-8 text-violet-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-rose-400 bg-clip-text text-transparent">
              Sihirli Seslendirme
            </h1>
            <p className="text-slate-400 mt-0.5">Masalları kendi sesinden dinletmek için sesini klonla.</p>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Stepper + Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Stepper */}
            <div className="flex items-center gap-2">
              {STEPS.map((label, i) => (
                <div key={i} className="flex items-center gap-2 flex-1">
                  <div
                    className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold border-2 transition-all ${
                      i < step
                        ? 'bg-violet-500 border-violet-500 text-white'
                        : i === step
                        ? 'border-violet-400 text-violet-400 bg-violet-500/10'
                        : 'border-white/10 text-slate-600 bg-transparent'
                    }`}
                  >
                        {i < step ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
                  </div>
                  <span
                    className={`text-xs font-medium ${
                      i <= step ? 'text-slate-300' : 'text-slate-600'
                    }`}
                  >
                        {label}
                  </span>
                  {i < STEPS.length - 1 && (
                        <ChevronRight className="w-4 h-4 text-slate-700 shrink-0 ml-auto" />
                  )}
                </div>
              ))}
            </div>

            <AnimatePresence mode="wait">
              {/* Step 0: Name */}
              {step === 0 && (
                <motion.div
                  key="step0"
                  initial={{ opacity: 0, x: 30 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -30 }}
                  className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-5"
                >
                  <h2 className="text-lg font-bold text-white">Sesin için bir isim seç</h2>
                  <input
                    type="text"
                    value={voiceName}
                    onChange={(e) => setVoiceName(e.target.value)}
                    placeholder="Örn: Annemin Sesi"
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all"
                  />
                  <Button
                    onClick={() => setStep(1)}
                    disabled={!voiceName.trim()}
                    className="w-full bg-violet-600 hover:bg-violet-500 text-white font-bold disabled:opacity-40"
                  >
                    Devam Et
                  </Button>
                </motion.div>
              )}

              {/* Step 1: Record */}
              {step === 1 && (
                <motion.div
                  key="step1"
                  initial={{ opacity: 0, x: 30 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -30 }}
                  className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-6"
                >
                  <h2 className="text-lg font-bold text-white">Örnek metni oku</h2>

                  {/* Text Selector */}
                  <div className="space-y-2">
                        {READING_TEXTS.map((text, i) => (
                          <button
                            key={i}
                            onClick={() => setSelectedText(i)}
                            className={`w-full text-left p-4 rounded-xl border transition-all text-sm ${
                              selectedText === i
                                ? 'border-violet-500/50 bg-violet-500/10 text-violet-200'
                                : 'border-white/5 bg-black/20 text-slate-400 hover:border-white/20'
                            }`}
                          >
                            <span className="text-xs font-bold text-slate-500 block mb-1">Metin {i + 1}</span>
                            {text}
                          </button>
                        ))}
                  </div>

                  {/* Waveform */}
                  <AnimatePresence>
                        {isRecording && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="flex items-end justify-center gap-1 h-16 bg-black/30 rounded-xl px-4"
                          >
                            {WAVEFORM_BARS.map((h, i) => (
                              <motion.div
                                key={i}
                                className="w-2 rounded-full bg-gradient-to-t from-violet-600 to-rose-400"
                                animate={{ height: [`${h * 0.4}%`, `${h}%`, `${h * 0.5}%`] }}
                                transition={{
                                  duration: 0.6 + i * 0.05,
                                  repeat: Infinity,
                                  repeatType: 'mirror',
                                  delay: i * 0.04,
                                }}
                              />
                            ))}
                          </motion.div>
                        )}
                  </AnimatePresence>

                  {/* Record controls */}
                  <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={isRecording ? stopRecording : startRecording}
                          disabled={loading}
                          className={`flex flex-col items-center justify-center py-5 rounded-xl border-2 transition-all ${
                            isRecording
                              ? 'bg-rose-500/10 border-rose-500/50 text-rose-400'
                              : 'bg-black/20 border-white/10 text-slate-300 hover:border-violet-500/50 hover:bg-violet-500/5'
                          }`}
                        >
                          {isRecording ? (
                            <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1 }}>
                                  <Square className="w-8 h-8 mb-2 fill-current" />
                            </motion.div>
                          ) : (
                            <Mic className="w-8 h-8 mb-2" />
                          )}
                          <span className="text-sm font-medium">
                            {isRecording ? `Durdur (${formatTime(recordingTime)})` : 'Mikrofonla Kaydet'}
                          </span>
                        </button>

                        <button
                          onClick={() => fileInputRef.current?.click()}
                          disabled={isRecording || loading}
                          className="flex flex-col items-center justify-center py-5 bg-black/20 border-2 border-white/10 rounded-xl text-slate-300 hover:border-violet-500/50 hover:bg-violet-500/5 transition-all disabled:opacity-40"
                        >
                          {loading ? (
                            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                                  <UploadCloud className="w-8 h-8 mb-2 text-violet-400" />
                            </motion.div>
                          ) : (
                            <UploadCloud className="w-8 h-8 mb-2" />
                          )}
                          <span className="text-sm font-medium">{loading ? 'Yükleniyor...' : 'Ses Dosyası Yükle'}</span>
                          <span className="text-xs text-slate-500 mt-1">MP3, WAV veya M4A</span>
                          <input type="file" ref={fileInputRef} className="hidden" accept="audio/*" onChange={handleFileUpload} />
                        </button>
                  </div>

                  <p className="text-xs text-slate-500 italic">
                        * En az 1 dakika temiz, gürültüsüz ses önerilir.
                  </p>
                </motion.div>
              )}

              {/* Step 2: Finish */}
              {step === 2 && (
                <motion.div
                  key="step2"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  className="bg-white/5 border border-emerald-500/20 rounded-2xl p-8 text-center space-y-5"
                >
                  <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto">
                        <CheckCircle2 className="w-10 h-10 text-emerald-400" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">Ses Alındı!</h2>
                    <p className="text-slate-400 text-sm mt-1">
                          <span className="text-violet-300 font-semibold">{voiceName}</span> klonlanmaya hazır.
                          Sunucuda işlenip birkaç dakikada hazır olacak.
                    </p>
                  </div>
                  <Button
                    onClick={handleFinish}
                    className="bg-violet-600 hover:bg-violet-500 text-white font-bold px-8"
                  >
                    Sese Ekle & Bitir
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Mevcut Sesler */}
          <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col"
          >
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <Volume2 className="w-5 h-5 text-emerald-400" />
                  Klonlanmış Seslerim
                  <span className="ml-auto text-xs text-slate-500 font-normal">{voices.length} ses</span>
            </h2>

            {voices.length === 0 ? (
                  <div className="flex-1 flex flex-col items-center justify-center text-center p-6 bg-black/20 rounded-xl border border-white/5 border-dashed">
                    <MicVocal className="w-10 h-10 text-slate-600 mb-3" />
                    <p className="text-slate-500 text-sm">Henüz ses yok.</p>
                  </div>
            ) : (
                  <div className="space-y-3 flex-1 overflow-y-auto">
                    {voices.map((voice, i) => (
                      <motion.div
                        key={voice.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="group flex items-center gap-3 p-3 bg-black/20 border border-white/5 hover:border-white/10 rounded-xl transition-all"
                      >
                        <button className="w-9 h-9 shrink-0 rounded-full bg-violet-500/20 text-violet-400 flex items-center justify-center hover:bg-violet-500 hover:text-white transition-all">
                              <Play className="w-3.5 h-3.5 ml-0.5" />
                        </button>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-slate-200 text-sm truncate">{voice.name}</p>
                          <p className="text-xs text-slate-500">Kullanıma Hazır</p>
                        </div>
                        <button
                          onClick={() => handleDelete(voice.id)}
                          className="p-1.5 text-slate-600 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                        >
                              <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </motion.div>
                    ))}
                  </div>
            )}
          </motion.div>
        </div>
      </div>
    </PremiumGate>
  );
};
