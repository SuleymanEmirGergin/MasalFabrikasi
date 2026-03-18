import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/useAuthStore';
import { MainLayout } from './components/MainLayout';
import { useThemeStore } from './store/useThemeStore';

const LoginPage = lazy(() => import('./pages/LoginPage').then((m) => ({ default: m.LoginPage })));
const DashboardPage = lazy(() => import('./pages/DashboardPage').then((m) => ({ default: m.DashboardPage })));
const StoryCreatorPage = lazy(() => import('./pages/StoryCreatorPage').then((m) => ({ default: m.StoryCreatorPage })));
const StoryViewerPage = lazy(() => import('./pages/StoryViewerPage').then((m) => ({ default: m.StoryViewerPage })));
const CharactersPage = lazy(() => import('./pages/CharactersPage').then((m) => ({ default: m.CharactersPage })));
const MarketPage = lazy(() => import('./pages/MarketPage').then((m) => ({ default: m.MarketPage })));
const SettingsPage = lazy(() => import('./pages/SettingsPage').then((m) => ({ default: m.SettingsPage })));
const ProfilePage = lazy(() => import('./pages/ProfilePage').then((m) => ({ default: m.ProfilePage })));
const MagicCanvasPage = lazy(() => import('./pages/MagicCanvasPage').then((m) => ({ default: m.MagicCanvasPage })));
const InteractiveStoryPage = lazy(() => import('./pages/InteractiveStoryPage').then((m) => ({ default: m.InteractiveStoryPage })));
const CharacterChatPage = lazy(() => import('./pages/CharacterChatPage').then((m) => ({ default: m.CharacterChatPage })));
const QuizPage = lazy(() => import('./pages/QuizPage').then((m) => ({ default: m.QuizPage })));
const GamificationPage = lazy(() => import('./pages/GamificationPage').then((m) => ({ default: m.GamificationPage })));
const ParentalDashboardPage = lazy(() => import('./pages/ParentalDashboardPage').then((m) => ({ default: m.ParentalDashboardPage })));
const VoiceCloningPage = lazy(() => import('./pages/VoiceCloningPage').then((m) => ({ default: m.VoiceCloningPage })));
const CommunityPage = lazy(() => import('./pages/CommunityPage').then((m) => ({ default: m.CommunityPage })));
const SubscriptionPage = lazy(() => import('./pages/SubscriptionPage').then((m) => ({ default: m.SubscriptionPage })));
const BedtimeModePage = lazy(() => import('./pages/BedtimeModePage').then((m) => ({ default: m.BedtimeModePage })));
const SocialPage = lazy(() => import('./pages/SocialPage').then((m) => ({ default: m.SocialPage })));
const SmartRoomPage = lazy(() => import('./pages/SmartRoomPage').then((m) => ({ default: m.SmartRoomPage })));
const StoryMapPage = lazy(() => import('./pages/StoryMapPage').then((m) => ({ default: m.StoryMapPage })));
const PrivacySettingsPage = lazy(() => import('./pages/PrivacySettingsPage').then((m) => ({ default: m.PrivacySettingsPage })));

function PageFallback() {
  return (
    <div className="min-h-screen bg-[#02010a] flex items-center justify-center text-slate-400">
      <span className="animate-pulse">Yükleniyor…</span>
    </div>
  );
}

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? (
    <MainLayout>{children}</MainLayout>
  ) : (
    <Navigate to="/login" />
  );
};

function App() {
  const { theme } = useThemeStore();

  React.useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  return (
    <Router>
      <Suspense fallback={<PageFallback />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Routes */}
        <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        
        {/* Functional Routes */}
        <Route path="/create" element={<ProtectedRoute><StoryCreatorPage /></ProtectedRoute>} />
        <Route path="/story" element={<ProtectedRoute><StoryViewerPage /></ProtectedRoute>} />
        <Route path="/characters" element={<ProtectedRoute><CharactersPage /></ProtectedRoute>} />
        <Route path="/story-map" element={<ProtectedRoute><StoryMapPage /></ProtectedRoute>} />
        <Route path="/chat/:characterId" element={<ProtectedRoute><CharacterChatPage /></ProtectedRoute>} />
        <Route path="/market" element={<ProtectedRoute><MarketPage /></ProtectedRoute>} />
        <Route path="/magic-canvas" element={<ProtectedRoute><MagicCanvasPage /></ProtectedRoute>} />
        <Route path="/interactive" element={<ProtectedRoute><InteractiveStoryPage /></ProtectedRoute>} />
        <Route path="/quiz" element={<ProtectedRoute><QuizPage /></ProtectedRoute>} />
        <Route path="/gamification" element={<ProtectedRoute><GamificationPage /></ProtectedRoute>} />
        <Route path="/parental" element={<ProtectedRoute><ParentalDashboardPage /></ProtectedRoute>} />
        <Route path="/voice-cloning" element={<ProtectedRoute><VoiceCloningPage /></ProtectedRoute>} />
        <Route path="/community" element={<ProtectedRoute><CommunityPage /></ProtectedRoute>} />
        <Route path="/subscription" element={<ProtectedRoute><SubscriptionPage /></ProtectedRoute>} />
        <Route path="/bedtime" element={<ProtectedRoute><BedtimeModePage /></ProtectedRoute>} />
        <Route path="/social" element={<ProtectedRoute><SocialPage /></ProtectedRoute>} />
        <Route path="/gamification" element={<ProtectedRoute><GamificationPage /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
        <Route path="/smart-room" element={<ProtectedRoute><SmartRoomPage /></ProtectedRoute>} />
        <Route path="/privacy" element={<ProtectedRoute><PrivacySettingsPage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        
          {/* Redirect unknown to home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Suspense>
    </Router>
  );
}

export default App;
