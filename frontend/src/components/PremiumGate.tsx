import React from 'react';
import { motion } from 'framer-motion';
import { Crown, Lock, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/useAuthStore';
import { Button } from '@/components/ui/button';

interface PremiumGateProps {
  children: React.ReactNode;
  featureName: string;
  description?: string;
}

export const PremiumGate: React.FC<PremiumGateProps> = ({ 
  children, 
  featureName, 
  description = "Bu harika özelliği keşfetmek için Premium maceracı olun!" 
}) => {
  const isPremium = useAuthStore((state) => state.isPremium);
  const navigate = useNavigate();

  if (isPremium) {
    return <>{children}</>;
  }

  return (
    <div className="relative min-h-[400px] w-full rounded-3xl overflow-hidden border border-white/5 bg-black/20">
      {/* Blurred Content Background */}
      <div className="absolute inset-0 blur-xl opacity-20 pointer-events-none select-none grayscale">
        {children}
      </div>

      {/* Overlay Content */}
      <div className="absolute inset-0 flex items-center justify-center p-6 bg-gradient-to-b from-transparent via-black/40 to-black/80">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full bg-[#0f1115]/90 border border-magical-purple/30 backdrop-blur-md p-8 rounded-3xl text-center shadow-[0_0_50px_-12px_var(--magical-purple)]"
        >
          <div className="inline-flex p-4 bg-magical-purple/20 rounded-2xl mb-6 relative">
            <Lock className="w-10 h-10 text-magical-purple" />
            <motion.div
              animate={{ rotate: [0, 15, -15, 0] }}
              transition={{ repeat: Infinity, duration: 4 }}
              className="absolute -top-2 -right-2 p-1.5 bg-amber-500 rounded-lg shadow-lg"
            >
              <Crown className="w-4 h-4 text-white" />
            </motion.div>
          </div>

          <h3 className="text-2xl font-black text-white mb-3">
             {featureName} <br />
             <span className="text-magical-purple">Kilitli!</span>
          </h3>
          
          <p className="text-slate-400 mb-8 text-sm leading-relaxed">
            {description}
          </p>

          <div className="space-y-3">
            <Button
              onClick={() => navigate('/subscription')}
              className="w-full h-14 bg-gradient-to-r from-magical-purple to-magical-rose hover:opacity-90 text-white font-black text-lg rounded-xl shadow-lg shadow-magical-purple/20"
            >
              PREMİUM'A GEÇ <Sparkles className="ml-2 w-5 h-5" />
            </Button>
            
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
              İptal edilebilir • Ömür boyu masal garantisi
            </p>
          </div>

          <div className="mt-8 pt-6 border-t border-white/5 grid grid-cols-2 gap-4">
            <div className="text-left">
              <p className="text-white font-bold text-xs">Sınırsız Masal</p>
              <p className="text-slate-500 text-[10px]">Her gün yeni maceralar</p>
            </div>
            <div className="text-left border-l border-white/5 pl-4">
              <p className="text-white font-bold text-xs">Ses Klonlama</p>
              <p className="text-slate-500 text-[10px]">Kendi sesinle oku</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
