import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BrainCircuit,
  CheckCircle2,
  XCircle,
  Trophy,
  ArrowRight,
  Sparkles,
  RefreshCcw,
  Clock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const DEMO_QUIZ = {
  id: 'demo-quiz-1',
  title: 'Cesur Tavşan ve Sihirli Orman',
  questions: [
    {
      id: 'q1',
      text: 'Cesur Tavşan ormanda ilk olarak kiminle karşılaştı?',
      options: ['Bilge Baykuş', 'Kurnaz Tilki', 'Minik Sincap', 'Yaşlı Kaplumbağa'],
      correct_answer: 'Bilge Baykuş',
    },
    {
      id: 'q2',
      text: "Ormanın kalbindeki sihirli nesne neydi?",
      options: ['Altın Meşe Palamudu', 'Parlayan Kristal', 'Gümüş Elma', 'Uçan Halı'],
      correct_answer: 'Parlayan Kristal',
    },
    {
      id: 'q3',
      text: 'Tavşan hangi özelliğini kullanarak zorluğu aştı?',
      options: ['Çok hızlı koşması', 'Cesareti', 'Görünmezliği', 'Şarkı söylemesi'],
      correct_answer: 'Cesareti',
    },
  ],
};

const QUESTION_TIME = 15; // seconds per question
const MOTIVATIONAL = ['🎉 Harika!', '⭐ Mükemmel!', '🔥 Süpersin!', '✨ Bravo!'];
const WRONG_MSG = ['😅 Olmadı!', '💪 Dene yine!', '🤔 Eh...', '💭 Neredeyse!'];

// Stable confetti positions
const CONFETTI = Array.from({ length: 20 }, (_, i) => ({
  left: (i * 5.2) % 100,
  color: ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'][i % 5],
  delay: (i * 0.12) % 2,
  dur: 1.5 + (i % 4) * 0.3,
}));

type QuizState = 'INTRO' | 'PLAYING' | 'FINISHED';

export const QuizPage = () => {
  const [quizState, setQuizState] = useState<QuizState>('INTRO');
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isRevealed, setIsRevealed] = useState(false);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(QUESTION_TIME);
  const [showConfetti, setShowConfetti] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const currentQuestion = DEMO_QUIZ.questions[currentIdx];
  const total = DEMO_QUIZ.questions.length;
  const progress = ((currentIdx) / total) * 100;

  useEffect(() => {
    if (quizState !== 'PLAYING' || isRevealed) return;
    setTimeLeft(QUESTION_TIME);
    timerRef.current = window.setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          handleReveal(null); // time out
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current!);
    // eslint-disable-next-line
  }, [currentIdx, quizState]);

  const handleReveal = (option: string | null) => {
    if (isRevealed) return;
    clearInterval(timerRef.current!);
    setSelectedAnswer(option);
    setIsRevealed(true);

    const isCorrect = option === currentQuestion.correct_answer;
    if (isCorrect) {
      setScore((s) => s + 1);
      setFeedbackMsg(MOTIVATIONAL[Math.floor((currentIdx) % MOTIVATIONAL.length)]);
    } else {
      setFeedbackMsg(WRONG_MSG[Math.floor((currentIdx) % WRONG_MSG.length)]);
    }
  };

  const handleNext = () => {
    setFeedbackMsg(null);
    if (currentIdx + 1 >= total) {
      setShowConfetti(true);
      setQuizState('FINISHED');
      setTimeout(() => setShowConfetti(false), 3000);
    } else {
      setCurrentIdx((i) => i + 1);
      setSelectedAnswer(null);
      setIsRevealed(false);
    }
  };

  const handleRestart = () => {
    setQuizState('INTRO');
    setCurrentIdx(0);
    setScore(0);
    setSelectedAnswer(null);
    setIsRevealed(false);
    setFeedbackMsg(null);
    setShowConfetti(false);
  };

  const timerPct = (timeLeft / QUESTION_TIME) * 100;
  const timerColor =
    timeLeft > 8 ? 'from-emerald-500 to-emerald-400' : timeLeft > 4 ? 'from-amber-500 to-amber-400' : 'from-rose-500 to-rose-400';

  return (
    <div className="max-w-2xl mx-auto space-y-8 pb-12 relative">
      {/* Confetti */}
      <AnimatePresence>
        {showConfetti && (
          <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
            {CONFETTI.map((c, i) => (
              <motion.div
                key={i}
                initial={{ y: -20, opacity: 1, x: `${c.left}vw` }}
                animate={{ y: '105vh', opacity: 0, rotate: 360 * (i % 2 === 0 ? 1 : -1) }}
                transition={{ duration: c.dur, delay: c.delay, ease: 'easeIn' }}
                className="absolute top-0 w-3 h-3 rounded-sm"
                style={{ background: c.color }}
              />
            ))}
          </div>
        )}
      </AnimatePresence>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4">
        <div className="p-3 bg-amber-500/20 rounded-xl">
          <BrainCircuit className="w-8 h-8 text-amber-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
            Eğlenceli Sınavlar
          </h1>
          <p className="text-slate-400 mt-0.5">Masalı ne kadar iyi okudun? Şimdi test et!</p>
        </div>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* INTRO */}
        {quizState === 'INTRO' && (
          <motion.div
            key="intro"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-10 text-center space-y-6"
          >
            <div className="w-20 h-20 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto">
              <Sparkles className="w-10 h-10 text-amber-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{DEMO_QUIZ.title}</h2>
              <p className="text-slate-400 mt-2 text-sm">
                {total} soru · Soru başına {QUESTION_TIME} saniye
              </p>
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              {[
                { label: 'Sorular', value: total.toString() },
                { label: 'Süre', value: `${QUESTION_TIME}s` },
                { label: 'Puan', value: '10x' },
              ].map((item) => (
                <div key={item.label} className="bg-black/20 rounded-xl p-4 border border-white/5">
                  <p className="text-2xl font-bold text-white">{item.value}</p>
                  <p className="text-xs text-slate-500 mt-1">{item.label}</p>
                </div>
              ))}
            </div>
            <Button
              onClick={() => { setQuizState('PLAYING'); setCurrentIdx(0); setScore(0); }}
              className="bg-amber-500 hover:bg-amber-400 text-black font-bold px-10 py-6 text-lg"
            >
              Başla! <ArrowRight className="w-5 h-5 ml-2 inline" />
            </Button>
          </motion.div>
        )}

        {/* PLAYING */}
        {quizState === 'PLAYING' && (
          <motion.div
            key={`q-${currentIdx}`}
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -40 }}
            className="space-y-5"
          >
            {/* Progress & Timer bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-slate-400">
                <span>{currentIdx + 1} / {total}</span>
                <span className="flex items-center gap-1 font-mono font-bold" style={{ color: timeLeft <= 4 ? '#f87171' : '#94a3b8' }}>
                  <Clock className="w-3.5 h-3.5" />
                  {timeLeft}s
                </span>
              </div>
              {/* Timer */}
              <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full rounded-full bg-gradient-to-r ${timerColor}`}
                  animate={{ width: `${timerPct}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              {/* Progress */}
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
              </div>
            </div>

            {/* Question */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <p className="text-xl font-bold text-white leading-snug">{currentQuestion.text}</p>
            </div>

            {/* Options */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {currentQuestion.options.map((option, i) => {
                const isSelected = selectedAnswer === option;
                const isCorrect = option === currentQuestion.correct_answer;
                let cls = 'bg-black/20 border-white/10 text-slate-300 hover:border-amber-500/40 hover:bg-amber-500/5';
                if (isRevealed) {
                  if (isCorrect) cls = 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300';
                  else if (isSelected) cls = 'bg-rose-500/20 border-rose-500/50 text-rose-300';
                  else cls = 'bg-black/10 border-white/5 text-slate-600 opacity-60';
                }
                return (
                  <motion.button
                    key={option}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.06 }}
                    whileTap={!isRevealed ? { scale: 0.97 } : {}}
                    disabled={isRevealed}
                    onClick={() => handleReveal(option)}
                    className={`text-left p-4 rounded-xl border-2 transition-all font-medium text-sm flex items-center gap-3 ${cls}`}
                  >
                    <span className="w-6 h-6 shrink-0 rounded-full border border-current flex items-center justify-center text-xs font-bold">
                      {String.fromCharCode(65 + i)}
                    </span>
                    {option}
                    {isRevealed && isCorrect && <CheckCircle2 className="w-4 h-4 ml-auto shrink-0" />}
                    {isRevealed && isSelected && !isCorrect && <XCircle className="w-4 h-4 ml-auto shrink-0" />}
                  </motion.button>
                );
              })}
            </div>

            {/* Feedback & Next */}
            <AnimatePresence>
              {isRevealed && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center justify-between bg-white/5 border border-white/10 rounded-xl px-5 py-4"
                >
                  <span className="text-lg font-bold">{feedbackMsg}</span>
                  <Button onClick={handleNext} className="bg-amber-500 hover:bg-amber-400 text-black font-bold">
                    {currentIdx + 1 >= total ? 'Bitir 🏆' : 'Sonraki'}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* FINISHED */}
        {quizState === 'FINISHED' && (
          <motion.div
            key="finished"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-10 text-center space-y-6"
          >
            <div className="w-20 h-20 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto">
              <Trophy className="w-10 h-10 text-amber-400" />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">
                {score === total ? '🏆 Mükemmel!' : score >= total / 2 ? '⭐ İyi İş!' : '💪 Daha iyisini yapabilirsin!'}
              </h2>
              <p className="text-slate-400 mt-2">
                <span className="text-4xl font-black text-white">{score}</span>
                <span className="text-slate-400"> / {total} doğru</span>
              </p>
            </div>
            <div className="flex gap-3 justify-center">
              <Button variant="outline" onClick={handleRestart} className="border-white/10 text-slate-300">
                <RefreshCcw className="w-4 h-4 mr-2" /> Tekrar Oyna
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
