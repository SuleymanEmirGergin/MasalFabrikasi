import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, Sparkles, MessageSquare, History } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTranslation } from '@/hooks/useTranslation';

export const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const stats = [
    { icon: BookOpen, labelKey: 'dashboard.myStories', value: '12', color: 'bg-blue-500/20 text-blue-400' },
    { icon: MessageSquare, labelKey: 'dashboard.myCharacters', value: '8', color: 'bg-magical-violet/20 text-magical-violet' },
    { icon: Sparkles, labelKey: 'dashboard.magicPoints', value: '500', color: 'bg-magical-rose/20 text-magical-rose' },
    { icon: History, labelKey: 'dashboard.recentDrafts', value: '3', color: 'bg-emerald-500/20 text-emerald-400' },
  ];
  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div>
        <h1 className="text-4xl font-bold mb-2">{t('dashboard.welcome')}, <span className="text-magical-indigo">{t('dashboard.welcomeName')}!</span></h1>
        <p className="text-slate-400">{t('dashboard.todayQuestion')}</p>
      </div>

      {/* Quick Stats/Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <Card key={i} className="bg-white/5 border-white/10 hover:border-white/20 transition-all cursor-pointer group">
            <CardContent className="p-6 flex items-center space-x-4">
              <div className={`p-3 rounded-2xl ${stat.color} transition-transform group-hover:scale-110`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-slate-400 font-medium">{t(stat.labelKey)}</p>
                <p className="text-2xl font-bold">{stat.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Featured Action */}
      <Card className="bg-gradient-to-r from-magical-indigo/20 via-magical-violet/20 to-magical-rose/20 border-white/10 overflow-hidden relative group">
        <div className="absolute inset-0 bg-white/5 backdrop-blur-3xl -z-10" />
        <CardHeader className="p-10 space-y-4">
          <CardTitle className="text-3xl font-bold">{t('dashboard.startNewStory')}</CardTitle>
          <p className="text-slate-300 max-w-xl text-lg">
            {t('dashboard.startNewStoryDesc')}
          </p>
          <div className="pt-4">
            <Button className="bg-white text-black hover:bg-slate-200 h-12 px-8 rounded-xl font-bold text-base shadow-xl group transition-all">
              <Sparkles className="w-5 h-5 mr-2 animate-pulse group-hover:rotate-12 transition-transform" />
              {t('dashboard.startMagic')}
            </Button>
          </div>
        </CardHeader>
        <div className="absolute right-[-50px] bottom-[-20px] opacity-10 group-hover:opacity-20 transition-opacity">
           <BookOpen className="w-80 h-80 rotate-12" />
        </div>
      </Card>
      
      {/* Recent Activity Mockup */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="bg-white/5 border-white/10">
          <CardHeader>
            <CardTitle>{t('dashboard.recentStories')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2, 3].map((_, i) => (
              <div key={i} className="flex items-center space-x-4 p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer border border-transparent hover:border-white/10">
                <div className="w-16 h-16 rounded-lg bg-slate-800 flex-shrink-0" />
                <div className="flex-1">
                  <h4 className="font-semibold">{t('dashboard.storyTitleExample')}</h4>
                  <p className="text-sm text-slate-500">{t('dashboard.recentStoryDateExample')}</p>
                </div>
                <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white"><History className="w-5 h-5" /></Button>
              </div>
            ))}
          </CardContent>
        </Card>
        
        <Card className="bg-white/5 border-white/10">
          <CardHeader>
            <CardTitle>{t('dashboard.magicStats')}</CardTitle>
          </CardHeader>
          <CardContent className="h-64 flex items-center justify-center border-t border-white/5">
            <p className="text-slate-500 text-sm">{t('dashboard.statsPlaceholder')}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
