import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Library, Flame, Clock, Heart, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Author {
  username: string;
  id: string;
}

interface PublicStory {
  id: string;
  title: string;
  theme: string;
  image_url: string | null;
  like_count: number;
  view_count: number;
  created_at: string;
  author: Author;
  isLikedByMe?: boolean;
}

const DUMMY_FEED: PublicStory[] = [
  {
    id: 's1',
    title: 'Kayıp Kar Tanesi',
    theme: 'Cesaret',
    image_url: 'https://images.unsplash.com/photo-1548624328-3e4b31a8afdd?auto=format&fit=crop&q=80&w=800',
    like_count: 342,
    view_count: 1205,
    created_at: '2026-03-20T10:00:00Z',
    author: { username: 'Zeynep Y.', id: 'u1' }
  },
  {
    id: 's2',
    title: 'Gezegenlerin Oyunu',
    theme: 'Uzay',
    image_url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=800',
    like_count: 890,
    view_count: 3100,
    created_at: '2026-03-18T14:30:00Z',
    author: { username: 'Ali B.', id: 'u2' }
  },
  {
    id: 's3',
    title: 'Küçük Dinozorun Sırrı',
    theme: 'Arkadaşlık',
    image_url: 'https://images.unsplash.com/photo-1518349619113-03114f06ac3a?auto=format&fit=crop&q=80&w=800',
    like_count: 124,
    view_count: 450,
    created_at: '2026-03-21T09:15:00Z',
    author: { username: 'Ayşe Çocuk', id: 'u3' }
  }
];

type SortType = 'popular' | 'latest';

export const CommunityPage = () => {
  const [stories, setStories] = useState<PublicStory[]>([]);
  const [sortBy, setSortBy] = useState<SortType>('popular');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    
    const fetchStories = async () => {
      // Simüle API çağrısı
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 600));
      
      if (!mounted) return;
      
      const sorted = [...DUMMY_FEED].sort((a, b) => {
        if (sortBy === 'popular') return b.like_count - a.like_count;
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
      
      setStories(sorted);
      setIsLoading(false);
    };

    fetchStories();
    return () => { mounted = false; };
  }, [sortBy]);

  const handleLike = (storyId: string) => {
    setStories(prev => prev.map(s => {
      if (s.id === storyId) {
        const isCurrentlyLiked = s.isLikedByMe;
        return {
          ...s,
          like_count: isCurrentlyLiked ? s.like_count - 1 : s.like_count + 1,
          isLikedByMe: !isCurrentlyLiked
        };
      }
      return s;
    }));
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-magical-purple/20 rounded-xl">
            <Library className="w-8 h-8 text-magical-purple" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-magical-purple to-magical-rose bg-clip-text text-transparent">
              Topluluk Kütüphanesi
            </h1>
            <p className="text-slate-400">Diğer çocukların yarattığı en güzel masalları keşfedin.</p>
          </div>
        </div>

        {/* Tab Selection */}
        <div className="flex bg-black/40 border border-white/10 p-1 rounded-xl self-start md:self-auto">
          <button
            onClick={() => setSortBy('popular')}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
              sortBy === 'popular'
                ? 'bg-magical-purple text-white shadow-lg'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Flame className={`w-4 h-4 ${sortBy === 'popular' ? 'fill-current' : ''}`} /> Popüler
          </button>
          <button
            onClick={() => setSortBy('latest')}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
              sortBy === 'latest'
                ? 'bg-emerald-500 text-white shadow-lg'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Clock className="w-4 h-4" /> En Yeniler
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative min-h-[400px]">
        <AnimatePresence mode="popLayout">
          {isLoading ? (
            <motion.div 
              key="loader"
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center col-span-full"
            >
              <div className="w-8 h-8 border-4 border-magical-purple border-t-transparent rounded-full animate-spin"></div>
            </motion.div>
          ) : (
            stories.map((story, index) => (
              <motion.div
                key={story.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="group bg-white/5 border border-white/10 hover:border-magical-purple/50 rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-[0_0_30px_-5px_var(--magical-purple)]"
              >
                {/* Image Area */}
                <div className="relative h-48 overflow-hidden bg-black/40">
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent z-10" />
                  {story.image_url ? (
                    <img 
                      src={story.image_url} 
                      alt={story.title} 
                      className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-700"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Library className="w-12 h-12 text-slate-700" />
                    </div>
                  )}
                  
                  {/* Floating Theme Badge */}
                  <div className="absolute top-4 left-4 z-20">
                    <span className="px-3 py-1 bg-black/60 backdrop-blur-md rounded-full text-xs font-semibold text-white border border-white/20">
                      {story.theme}
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className="text-xl font-bold text-white mb-2 line-clamp-1 group-hover:text-magical-purple transition-colors">
                    {story.title}
                  </h3>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-[10px] font-bold text-white">
                      {story.author.username.charAt(0)}
                    </div>
                    <span className="text-sm text-slate-400">Yazar: <span className="text-slate-300">{story.author.username}</span></span>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-white/10">
                    <div className="flex items-center gap-4 text-slate-400">
                      <button 
                        onClick={(e) => { e.preventDefault(); handleLike(story.id); }}
                        className={`flex items-center gap-1.5 transition-colors ${story.isLikedByMe ? 'text-rose-500' : 'hover:text-rose-400'}`}
                      >
                        <Heart className={`w-4 h-4 ${story.isLikedByMe ? 'fill-current' : ''}`} />
                        <span className="text-sm font-medium">{story.like_count}</span>
                      </button>
                      <div className="flex items-center gap-1.5 cursor-default hover:text-slate-300 transition-colors">
                        <Eye className="w-4 h-4" />
                        <span className="text-sm font-medium">{story.view_count}</span>
                      </div>
                    </div>
                    <Link to={`/read/${story.id}?from=community`} className="px-4 py-1.5 rounded-lg bg-white/5 hover:bg-magical-purple text-white text-sm font-medium transition-all">
                      Oku
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
