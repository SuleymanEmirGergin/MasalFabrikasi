/**
 * Merkezi API hook'ları — tüm backend endpoint'lerine type-safe erişim.
 * baseURL: http://localhost:8000/api/v1  (VITE_API_URL'den okunur)
 */
import { useState, useCallback } from 'react';
import api from './client';
import axios from 'axios';

// ─── Tipler ─────────────────────────────────────────────────────────────────

export interface ClonedVoice {
  id: string;
  name: string;
  preview_url?: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: string;
  explanation?: string;
}

export interface Quiz {
  quiz_id: string;
  story_id: string;
  questions: QuizQuestion[];
}

export interface QuizResult {
  score: number;
  total: number;
  correct_answers: number;
  feedback?: string;
}

export interface ParentalStats {
  total_stories_read: number;
  total_words_encountered: number;
  unique_vocab_exposure: number;
  top_themes: { name: string; count: number }[];
  recent_analyses: {
    story_title: string;
    score: number;
    themes: string[];
    date: string;
  }[];
}

export interface PrivacySettings {
  analytics_consent: boolean;
  marketing_emails: boolean;
  data_sharing: boolean;
  profile_visibility: string;
}

// ─── Hata yardımcısı ────────────────────────────────────────────────────────
function extractError(err: unknown, fallback = 'Bir hata oluştu'): string {
  if (axios.isAxiosError(err)) {
    return err.response?.data?.detail || err.message || fallback;
  }
  if (err instanceof Error) return err.message;
  return fallback;
}

// ─── Voice Cloning ──────────────────────────────────────────────────────────

export function useVoiceCloning() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listVoices = useCallback(async (): Promise<ClonedVoice[]> => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ClonedVoice[]>('/voice-cloning/list');
      return res.data;
    } catch (err) {
      const msg = extractError(err, 'Sesler yüklenemedi');
      setError(msg);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const cloneVoice = useCallback(async (name: string, audioBlob: Blob): Promise<{ voice_id: string; name: string } | null> => {
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append('name', name);
      form.append('files', audioBlob, 'recording.webm');
      const res = await api.post<{ voice_id: string; name: string; message: string }>(
        '/voice-cloning/clone',
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      return res.data;
    } catch (err) {
      const msg = extractError(err, 'Ses klonlanamadı');
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteVoice = useCallback(async (voiceId: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/voice-cloning/${voiceId}`);
      return true;
    } catch (err) {
      const msg = extractError(err, 'Ses silinemedi');
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, listVoices, cloneVoice, deleteVoice };
}

// ─── Quiz ────────────────────────────────────────────────────────────────────

export function useQuiz() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateQuiz = useCallback(async (
    storyId: string,
    numQuestions = 5,
    difficulty = 'medium'
  ): Promise<Quiz | null> => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<Quiz>(`/stories/${storyId}/generate-quiz`, {
        num_questions: numQuestions,
        difficulty,
      });
      return res.data;
    } catch (err) {
      const msg = extractError(err, 'Quiz oluşturulamadı');
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const submitQuiz = useCallback(async (
    quizId: string,
    userId: string,
    answers: { question_index: number; answer: string }[]
  ): Promise<QuizResult | null> => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<QuizResult>(
        `/quizzes/${quizId}/submit?user_id=${userId}`,
        { answers }
      );
      return res.data;
    } catch (err) {
      const msg = extractError(err, 'Quiz gönderilemedi');
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, generateQuiz, submitQuiz };
}

// ─── Parental Dashboard ──────────────────────────────────────────────────────

export function useParentalStats(userId: string | undefined) {
  const [data, setData] = useState<ParentalStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ParentalStats>(`/parental/${userId}/stats`);
      setData(res.data);
    } catch (err) {
      const msg = extractError(err, 'İstatistikler yüklenemedi');
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  return { data, loading, error, fetchStats };
}

// ─── GDPR / Privacy ─────────────────────────────────────────────────────────

export function usePrivacy() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getPrivacySettings = useCallback(async (): Promise<PrivacySettings | null> => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<{ privacy_settings: PrivacySettings }>('/gdpr/privacy-settings');
      return res.data.privacy_settings;
    } catch (err) {
      const msg = extractError(err, 'Gizlilik ayarları yüklenemedi');
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const updatePrivacySettings = useCallback(async (settings: Partial<PrivacySettings>): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.put('/gdpr/privacy-settings', settings);
      return true;
    } catch (err) {
      const msg = extractError(err, 'Ayarlar güncellenemedi');
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const exportData = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/gdpr/data-export-zip', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data as BlobPart]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `masal_fabrikasi_verilerim_${new Date().toISOString().slice(0, 10)}.zip`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const msg = extractError(err, 'Veriler indirilemedi');
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const requestDeletion = useCallback(async (): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.delete('/gdpr/data-deletion');
      return true;
    } catch (err) {
      const msg = extractError(err, 'Silme isteği gönderilemedi');
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const withdrawConsent = useCallback(async (consentType: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.post(`/gdpr/consent-withdrawal?consent_type=${encodeURIComponent(consentType)}`);
      return true;
    } catch (err) {
      const msg = extractError(err, 'İzin geri çekilemedi');
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, getPrivacySettings, updatePrivacySettings, exportData, requestDeletion, withdrawConsent };
}

// ─── Character Chat ──────────────────────────────────────────────────────────

export function useCharacterChat() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (
    characterId: string,
    message: string,
    history: { role: string; content: string }[] = []
  ): Promise<string | null> => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<{ response: string }>('/character-chat/chat', {
        character_id: characterId,
        message,
        history,
        use_wiro: false
      });
      return res.data.response;
    } catch (err) {
      const msg = extractError(err, 'Mesaj gönderilemedi');
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, sendMessage };
}
