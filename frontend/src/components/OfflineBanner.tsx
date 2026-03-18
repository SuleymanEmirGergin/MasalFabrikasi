import React, { useState, useEffect } from 'react';
import { WifiOff } from 'lucide-react';
import { useTranslation } from '@/hooks/useTranslation';

/**
 * Shows a banner when the app is offline (navigator.onLine === false).
 * Hides automatically when back online and shows a short "back online" message.
 */
export const OfflineBanner: React.FC = () => {
  const { t } = useTranslation();
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );
  const [showBackOnline, setShowBackOnline] = useState(false);

  useEffect(() => {
    let backOnlineTimer: ReturnType<typeof setTimeout>;
    const handleOnline = () => {
      setIsOnline(true);
      setShowBackOnline(true);
      backOnlineTimer = setTimeout(() => setShowBackOnline(false), 3000);
    };
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      clearTimeout(backOnlineTimer);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline && !showBackOnline) return null;

  if (showBackOnline) {
    return (
      <div
        role="status"
        aria-live="polite"
        className="fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-lg bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-sm shadow-lg"
      >
        {t('common.backOnline')}
      </div>
    );
  }

  return (
    <div
      role="alert"
      className="fixed top-0 left-0 right-0 z-50 px-4 py-2 bg-amber-500/20 border-b border-amber-500/30 text-amber-200 text-sm text-center flex items-center justify-center gap-2"
    >
      <WifiOff className="w-4 h-4 shrink-0" aria-hidden />
      <span>{t('common.offline')}</span>
    </div>
  );
};
