import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Lock, Play, ShieldAlert } from 'lucide-react';
import { useParentalStore } from '@/store/useParentalStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export const ScreenTimeMonitor: React.FC = () => {
  const { 
    timeUsedToday, 
    screenTimeLimit, 
    lastResetDate, 
    pin,
    addTimeUsed, 
    resetTimeUsed
  } = useParentalStore();

  const [isLocked, setIsLocked] = useState(false);
  const [showPinEntry, setShowPinEntry] = useState(false);
  const [enteredPin, setEnteredPin] = useState('');
  const [error, setError] = useState(false);

  // Daily Reset & Tracking
  useEffect(() => {
    const checkReset = () => {
      const today = new Date().toISOString().split('T')[0];
      if (lastResetDate !== today) {
        resetTimeUsed();
      }
    };

    checkReset();
    
    const interval = setInterval(() => {
      const limitInSeconds = screenTimeLimit * 60;
      
      if (timeUsedToday < limitInSeconds) {
        addTimeUsed(1);
        if (isLocked) setIsLocked(false);
      } else {
        setIsLocked(true);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [timeUsedToday, screenTimeLimit, lastResetDate, addTimeUsed, resetTimeUsed, isLocked]);

  const handleUnlock = (e: React.FormEvent) => {
    e.preventDefault();
    if (enteredPin === pin) {
      // Give 30 more minutes as a bonus if parent unlocks
      const newLimit = screenTimeLimit + 30;
      useParentalStore.getState().setScreenTimeLimit(newLimit);
      setIsLocked(false);
      setShowPinEntry(false);
      setEnteredPin('');
      setError(false);
    } else {
      setError(true);
      setTimeout(() => setError(false), 2000);
    }
  };

  return (
    <AnimatePresence>
      {isLocked && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-[#02010a] flex flex-col items-center justify-center p-6 text-center"
        >
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-magical-purple/20 blur-[120px] rounded-full animate-pulse" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-magical-blue/20 blur-[120px] rounded-full animate-pulse delay-1000" />
          </div>

          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            className="max-w-md w-full space-y-8 relative"
          >
            <div className="relative inline-block">
              <div className="p-8 bg-gradient-to-br from-magical-purple/20 to-magical-blue/20 rounded-full mb-4">
                <Moon className="w-20 h-20 text-magical-purple animate-bounce" />
              </div>
              <div className="absolute -top-2 -right-2 p-3 bg-magical-rose rounded-2xl shadow-lg border-2 border-[#02010a]">
                <Lock className="w-6 h-6 text-white" />
              </div>
            </div>

            <div className="space-y-4">
              <h2 className="text-4xl font-black text-white leading-tight">
                Günün Masal Saati <br />
                <span className="bg-gradient-to-r from-magical-purple to-magical-blue bg-clip-text text-transparent">Sona Erdi!</span>
              </h2>
              <p className="text-slate-400 text-lg">
                Harika bir macera dolu gündü! Şimdi dinlenme ve gerçek rüyalar görme vakti. Masal Fabrikası yarın sabah yine burada olacak.
              </p>
            </div>

            <div className="pt-8">
              {!showPinEntry ? (
                <Button 
                  onClick={() => setShowPinEntry(true)}
                  variant="outline"
                  className="bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10 py-6 px-8 rounded-2xl text-sm font-bold tracking-widest uppercase transition-all"
                >
                  EBEVEYN GİRİŞİ (EK SÜRE)
                </Button>
              ) : (
                <motion.form 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  onSubmit={handleUnlock}
                  className="space-y-4"
                >
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">EBEVEYN PIN KODUNU GİRİN</label>
                    <Input
                      type="password"
                      value={enteredPin}
                      onChange={(e) => setEnteredPin(e.target.value)}
                      placeholder="****"
                      autoFocus
                      className={`h-16 text-center text-3xl font-black tracking-[1em] bg-white/5 border-white/10 rounded-2xl ${error ? 'border-rose-500 animate-shake' : 'focus:border-magical-purple'}`}
                    />
                  </div>
                  <div className="flex gap-4">
                    <Button 
                      type="button"
                      onClick={() => setShowPinEntry(false)}
                      variant="ghost"
                      className="flex-1 h-14 rounded-2xl text-slate-500"
                    >
                      Vazgeç
                    </Button>
                    <Button 
                      type="submit"
                      className="flex-1 h-14 bg-gradient-to-r from-magical-purple to-magical-blue hover:opacity-90 rounded-2xl font-bold"
                    >
                      KİLİDİ AÇ <Play className="ml-2 w-4 h-4 fill-current" />
                    </Button>
                  </div>
                  {error && (
                    <p className="text-rose-500 text-sm font-medium flex items-center justify-center gap-2">
                      <ShieldAlert className="w-4 h-4" /> Hatalı PIN kodu!
                    </p>
                  )}
                </motion.form>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
