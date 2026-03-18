import { useCallback } from 'react';
import { useLocaleStore } from '@/store/useLocaleStore';
import { getTranslation } from '@/lib/translations';

export function useTranslation() {
  const locale = useLocaleStore((s) => s.locale);
  const t = useCallback(
    (key: string) => getTranslation(locale, key),
    [locale]
  );
  return { t, locale };
}
