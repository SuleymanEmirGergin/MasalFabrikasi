import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, updateProfile, sendPasswordResetEmail } from 'firebase/auth';
import { useAuthStore } from '@/store/useAuthStore';
import { useTranslation } from '@/hooks/useTranslation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Sparkles, Wand2 } from 'lucide-react';
import { getFirebaseAuth, isFirebaseConfigured } from '@/lib/firebase';

export const LoginPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [forgotPassword, setForgotPassword] = useState(false);
  const [forgotSent, setForgotSent] = useState(false);

  const firebaseReady = isFirebaseConfigured();
  const auth = getFirebaseAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!auth || !email.trim() || !password) return;
    setLoading(true);
    try {
      const userCred = await signInWithEmailAndPassword(auth, email.trim(), password);
      const token = await userCred.user.getIdToken();
      setAuth(
        { name: userCred.user.displayName || email.trim(), email: userCred.user.email || email.trim() },
        token
      );
      navigate('/', { replace: true });
    } catch (err: unknown) {
      const message = err && typeof err === 'object' && 'code' in err
        ? (err as { code: string }).code === 'auth/invalid-credential' || (err as { code: string }).code === 'auth/wrong-password'
          ? t('login.invalidCredentials')
          : (err as { message?: string }).message || t('login.invalidCredentials')
        : t('login.invalidCredentials');
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!auth || !email.trim() || !password) return;
    if (password.length < 6) {
      setError(t('login.passwordTooShort'));
      return;
    }
    setLoading(true);
    try {
      const userCred = await createUserWithEmailAndPassword(auth, email.trim(), password);
      if (displayName.trim()) {
        await updateProfile(userCred.user, { displayName: displayName.trim() });
      }
      const token = await userCred.user.getIdToken();
      setAuth(
        { name: displayName.trim() || userCred.user.email || email.trim(), email: userCred.user.email || email.trim() },
        token
      );
      navigate('/', { replace: true });
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'code' in err
        ? (err as { code: string }).code === 'auth/email-already-in-use'
          ? t('login.emailAlreadyInUse')
          : (err as { message?: string }).message || t('login.signUpError')
        : t('login.signUpError');
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setError('');
    setAuth({ name: 'Emir', email: 'emir@example.com' }, 'demo-token');
    navigate('/', { replace: true });
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!auth || !email.trim()) {
      setError(t('login.emailRequired'));
      return;
    }
    setLoading(true);
    try {
      await sendPasswordResetEmail(auth, email.trim());
      setForgotSent(true);
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'code' in err
        ? (err as { code: string }).code === 'auth/user-not-found'
          ? t('login.emailNotFound')
          : (err as { message?: string }).message || t('login.emailSendFailed')
        : t('login.emailSendFailed');
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-[#02010a] relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-magical-indigo/20 blur-[120px] rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-magical-rose/20 blur-[120px] rounded-full" />
      
      <Card className="w-full max-w-md bg-white/5 border-white/10 backdrop-blur-xl shadow-2xl relative z-10">
        <CardHeader className="text-center space-y-1">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-magical-violet/20 rounded-2xl border border-magical-violet/30">
              <Sparkles className="w-10 h-10 text-magical-violet" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-magical-indigo to-magical-rose bg-clip-text text-transparent">
            {t('login.title')}
          </CardTitle>
          <CardDescription className="text-slate-400">
            {t('login.subtitle')}
          </CardDescription>
        </CardHeader>
        <form onSubmit={isSignUp ? handleSignUp : handleLogin}>
          <CardContent className="space-y-4">
            {error && (
              <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                {error}
              </div>
            )}
            {isSignUp && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 ml-1">{t('login.nameOptional')}</label>
                <Input 
                  type="text" 
                  placeholder={t('login.namePlaceholder')} 
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="bg-white/5 border-white/10 focus:border-magical-indigo transition-all"
                  autoComplete="name"
                />
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 ml-1">{t('login.email')}</label>
              <Input 
                type="email" 
                placeholder={t('login.emailPlaceholder')} 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-white/5 border-white/10 focus:border-magical-indigo transition-all"
                autoComplete="email"
              />
            </div>
            {!forgotPassword && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 ml-1">{t('login.password')}</label>
                <Input 
                  type="password" 
                  placeholder={isSignUp ? t('login.passwordMin') : t('login.passwordPlaceholder')} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-white/5 border-white/10 focus:border-magical-indigo transition-all"
                  autoComplete={isSignUp ? 'new-password' : 'current-password'}
                />
                {firebaseReady && !isSignUp && (
                  <button
                    type="button"
                    onClick={() => { setForgotPassword(true); setError(''); setForgotSent(false); }}
                    className="text-xs text-magical-indigo hover:text-magical-violet transition-colors"
                  >
                    {t('login.forgotPassword')}
                  </button>
                )}
              </div>
            )}
            {forgotPassword && (
              <p className="text-sm text-slate-400">
                {t('login.forgotPasswordHint')}
              </p>
            )}
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            {forgotSent ? (
              <>
                <p className="text-sm text-green-400 text-center">{t('login.forgotPasswordSuccess')}</p>
                <button type="button" onClick={() => { setForgotPassword(false); setForgotSent(false); }} className="text-sm text-magical-indigo hover:text-magical-violet">{t('login.backToSignIn')}</button>
              </>
            ) : forgotPassword ? (
              <>
                <Button type="button" onClick={handleForgotPassword} disabled={!email.trim() || loading} className="w-full h-12 bg-gradient-to-r from-magical-indigo to-magical-violet hover:opacity-90 font-semibold">
                  {loading ? t('login.forgotPasswordSending') : t('login.forgotPasswordSend')}
                </Button>
                <button type="button" onClick={() => { setForgotPassword(false); setError(''); }} className="text-sm text-magical-indigo hover:text-magical-violet">{t('login.backToSignIn')}</button>
              </>
            ) : (
            <>
            <Button 
              type="submit"
              className="w-full h-12 bg-gradient-to-r from-magical-indigo to-magical-violet hover:opacity-90 transition-all font-semibold"
              disabled={!firebaseReady || loading || !email.trim() || !password || (isSignUp && password.length < 6)}
            >
              {loading ? (isSignUp ? t('login.signUpLoading') : t('login.signInLoading')) : (isSignUp ? t('login.signUp') : t('login.signIn'))}
            </Button>
            <button
              type="button"
              onClick={() => { setIsSignUp(!isSignUp); setError(''); }}
              className="text-sm text-magical-indigo hover:text-magical-violet transition-colors"
            >
              {isSignUp ? t('login.hasAccount') : t('login.noAccount')}
            </button>
            </>
            )}
          </CardFooter>
        </form>
        <div className="relative w-full py-2 px-6">
          <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-white/10" /></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-transparent px-2 text-slate-500">{t('common.or')}</span></div>
        </div>
        <CardFooter className="flex flex-col space-y-4 pt-0">
          <Button 
            variant="outline" 
            className="w-full h-12 border-white/10 bg-transparent hover:bg-white/5 text-white transition-all group"
            onClick={handleDemoLogin}
          >
            <Wand2 className="w-4 h-4 mr-2 group-hover:animate-pulse" />
            {t('login.demoContinue')}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};
