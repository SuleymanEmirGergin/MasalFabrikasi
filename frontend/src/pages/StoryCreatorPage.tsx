import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MagicCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Sparkles, ArrowRight, ArrowLeft, Wand2, User, BookOpen, Music, Loader2 } from 'lucide-react';
import api from '@/api/client';

const genres = [
  { id: 'adventure', label: 'Macera', icon: '🚀', description: 'Bilinmeyene yolculuk ve heyecan dolu anlar.' },
  { id: 'fairy', label: 'Peri Masalı', icon: '🧚', description: 'Büyüleyici dünyalar ve imkansız mucizeler.' },
  { id: 'educational', label: 'Eğitici', icon: '🎓', description: 'Öğrenirken eğlendiren öğretici hikayeler.' },
  { id: 'scary', label: 'Korku/Gizem', icon: '👻', description: 'Hafif ürpertici ve merak uyandırıcı sırlar.' },
];

const FALLBACK_ERROR = 'Hikaye oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.';
const TIMEOUT_ERROR = 'Hikaye oluşturulurken zaman aşımı. Lütfen tekrar deneyin.';

export const StoryCreatorPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    genre: '',
    title: '',
    protagonist: '',
    ageGroup: [5],
    tone: 'magical',
    storyModel: '', // '' = backend default; openai/gpt-oss-20b | openai/gpt-5-nano
  });
  const [isCreating, setIsCreating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const nextStep = () => {
    setErrorMessage(null);
    setStep((prev) => Math.min(prev + 1, 3));
  };
  const prevStep = () => {
    setErrorMessage(null);
    setStep((prev) => Math.max(prev - 1, 1));
  };

  const handleCreateStory = async () => {
    setErrorMessage(null);
    setIsCreating(true);
    const theme = formData.title?.trim() || `${formData.genre} – ${formData.protagonist || 'Kahraman'}`;
    try {
      const body: Record<string, unknown> = {
        theme,
        language: 'tr',
        story_type: formData.genre || 'masal',
        save: true,
        use_async: false,
      };
      if (formData.storyModel) body.model = formData.storyModel;
      const { data } = await api.post('/generate-story', body, { timeout: 120000 });
      if (data?.story_id) {
        window.location.href = `/stories/${data.story_id}`;
      } else if (data?.job_id) {
        window.location.href = `/stories?job=${data.job_id}`;
      }
    } catch (err: unknown) {
      const ax = err as { code?: string; message?: string; response?: { data?: { detail?: string | { msg?: string } }; status?: number } };
      if (ax.code === 'ECONNABORTED' || ax.message?.toLowerCase().includes('timeout')) {
        setErrorMessage(TIMEOUT_ERROR);
      } else if (ax.response?.data?.detail) {
        const d = ax.response.data.detail;
        setErrorMessage(typeof d === 'string' ? d : (Array.isArray(d) && d[0]?.msg) ? d[0].msg : FALLBACK_ERROR);
      } else if (ax.response?.status && ax.response.status >= 500) {
        setErrorMessage('Sunucu geçici olarak yanıt veremiyor. Lütfen biraz sonra tekrar deneyin.');
      } else {
        setErrorMessage(FALLBACK_ERROR);
      }
    } finally {
      setIsCreating(false);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
                <BookOpen className="w-6 h-6 text-magical-rose" />
                Masalın Türünü Seç
              </h2>
              <p className="text-muted-foreground">Sihirli yolculuğun nasıl başlasın istersin?</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {genres.map((g) => (
                <div
                  key={g.id}
                  onClick={() => setFormData({ ...formData, genre: g.id })}
                  className={`p-4 rounded-xl border-2 transition-all cursor-pointer group ${
                    formData.genre === g.id
                      ? 'border-magical-indigo bg-magical-indigo/10'
                      : 'border-white/5 bg-white/5 hover:border-white/20'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-4xl group-hover:scale-110 transition-transform">{g.icon}</span>
                    <div>
                      <h3 className="font-bold text-white">{g.label}</h3>
                      <p className="text-xs text-muted-foreground">{g.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        );
      case 2:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
             <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
                <User className="w-6 h-6 text-magical-indigo" />
                Karakterini Yarat
              </h2>
              <p className="text-muted-foreground">Masalın kahramanı kim olacak?</p>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-white">Kahramanın İsmi</Label>
                <Input
                  placeholder="Örn: Cesur Aslan Simbal"
                  value={formData.protagonist}
                  onChange={(e) => setFormData({ ...formData, protagonist: e.target.value })}
                  className="bg-white/5 border-white/10 text-white"
                />
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Label className="text-white">Hedef Yaş Grubu</Label>
                  <Badge variant="outline" className="text-magical-rose border-magical-rose/30">
                    {formData.ageGroup[0]} Yaş
                  </Badge>
                </div>
                <Slider
                  value={formData.ageGroup}
                  onValueChange={(val) => setFormData({ ...formData, ageGroup: val })}
                  max={15}
                  min={3}
                  step={1}
                  className="py-4"
                />
              </div>
            </div>
          </motion.div>
        );
      case 3:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
                <Wand2 className="w-6 h-6 text-magical-violet" />
                Son Dokunuşlar
              </h2>
              <p className="text-muted-foreground">Sihrin tonunu ve modunu ayarla.</p>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <Label className="text-white">Masalın Başlığı (Opsiyonel)</Label>
                <Input
                  placeholder="Yapay zeka senin için bulabilir..."
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="bg-white/5 border-white/10 text-white"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-white">Anlatım Tarzı</Label>
                <Select
                  value={formData.tone}
                  onValueChange={(val: string) => setFormData({ ...formData, tone: val })}
                >
                  <SelectTrigger className="bg-white/5 border-white/10 text-white">
                    <SelectValue placeholder="Bir mod seç" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-white/10 text-white">
                    <SelectItem value="magical">Sihirli & Epik</SelectItem>
                    <SelectItem value="fun">Eğlenceli & Komik</SelectItem>
                    <SelectItem value="calm">Sakin & Huzurlu</SelectItem>
                    <SelectItem value="mysterious">Gizemli & Meraklı</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label className="text-white">Hikaye Modeli (isteğe bağlı)</Label>
                <Select
                  value={formData.storyModel || 'default'}
                  onValueChange={(val: string) => setFormData({ ...formData, storyModel: val === 'default' ? '' : val })}
                >
                  <SelectTrigger className="bg-white/5 border-white/10 text-white">
                    <SelectValue placeholder="Varsayılan" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-white/10 text-white">
                    <SelectItem value="default">Varsayılan (sunucu ayarı)</SelectItem>
                    <SelectItem value="openai/gpt-oss-20b">gpt-oss-20b</SelectItem>
                    <SelectItem value="openai/gpt-5-nano">gpt-5-nano</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="pt-4 p-4 rounded-xl bg-magical-rose/5 border border-magical-rose/10">
              <p className="text-xs text-magical-rose/80 flex items-center gap-2">
                <Music className="w-3 h-3" />
                Arka planda dinlendirici bir masal müziği de oluşturulacak.
              </p>
            </div>
          </motion.div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4">
      {/* Background Orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-1/4 -right-20 w-96 h-96 bg-magical-indigo/20 rounded-full blur-[120px]" />
        <div className="absolute -bottom-20 -left-20 w-96 h-96 bg-magical-rose/10 rounded-full blur-[120px]" />
      </div>

      <div className="mb-10 flex justify-between items-center bg-white/5 p-4 rounded-2xl border border-white/10">
        <div className="flex gap-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`h-2 w-12 rounded-full transition-all duration-500 ${
                s <= step ? 'bg-magical-rose' : 'bg-white/10'
              }`}
            />
          ))}
        </div>
        <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
          Adım {step} / 3
        </span>
      </div>

      <MagicCard className="bg-slate-900/40 border-white/10 backdrop-blur-xl p-8 relative overflow-hidden group">
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-transparent via-magical-rose/50 to-transparent opacity-50" />
        
        <AnimatePresence mode="wait">
          {renderStep()}
        </AnimatePresence>

        <div className="flex justify-between mt-10">
          <Button
            variant="ghost"
            onClick={prevStep}
            disabled={step === 1}
            className="text-white hover:bg-white/5"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Geri
          </Button>

          {step < 3 ? (
            <Button
              onClick={nextStep}
              className="bg-magical-indigo hover:bg-magical-indigo/80 text-white px-8"
              disabled={step === 1 && !formData.genre}
            >
              Devam Et <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleCreateStory}
              disabled={isCreating}
              className="bg-gradient-to-r from-magical-indigo to-magical-violet hover:opacity-90 text-white px-8 shadow-lg shadow-magical-indigo/20"
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 ml-2 animate-spin" />
                  Oluşturuluyor...
                </>
              ) : (
                <>Sihri Başlat <Sparkles className="w-4 h-4 ml-2" /></>
              )}
            </Button>
          )}
        </div>
        {errorMessage && (
          <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-200 text-sm" role="alert">
            {errorMessage}
          </div>
        )}
      </MagicCard>
    </div>
  );
};
