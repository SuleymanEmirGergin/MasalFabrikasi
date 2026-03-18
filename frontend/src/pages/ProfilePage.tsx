import React from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuthStore } from '@/store/useAuthStore';
import { useTranslation } from '@/hooks/useTranslation';

export const ProfilePage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-magical-indigo to-magical-rose bg-clip-text text-transparent flex items-center gap-3">
          <User className="w-8 h-8 text-magical-violet" />
          {t('profile.title')}
        </h1>
        <p className="text-slate-400 mt-1">{t('profile.subtitle')}</p>
      </div>

      <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-magical-indigo to-magical-violet border-2 border-white/20 flex items-center justify-center shrink-0">
              <span className="text-white text-2xl font-bold">{user?.name?.charAt(0) || '?'}</span>
            </div>
            <div>
              <CardTitle className="text-xl text-white">{user?.name || t('common.user')}</CardTitle>
              <CardDescription className="text-slate-400">{user?.email || '—'}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10">
            <User className="w-5 h-5 text-magical-indigo shrink-0" />
            <div>
              <p className="text-xs text-slate-500">{t('profile.name')}</p>
              <p className="text-white font-medium">{user?.name || '—'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10">
            <Mail className="w-5 h-5 text-magical-indigo shrink-0" />
            <div>
              <p className="text-xs text-slate-500">{t('profile.email')}</p>
              <p className="text-white font-medium">{user?.email || '—'}</p>
            </div>
          </div>
          <Button
            variant="outline"
            className="w-full h-12 border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300"
            onClick={handleLogout}
          >
            <LogOut className="w-5 h-5 mr-3" />
            {t('profile.logout')}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};
