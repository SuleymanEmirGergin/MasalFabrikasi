from typing import Dict, Optional
import os
import uuid
from datetime import datetime
from app.core.config import settings
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None
import json


class AudioRecordingService:
    def __init__(self):
        self.recordings_path = os.path.join(settings.STORAGE_PATH, "recordings")
        self.recordings_metadata_file = os.path.join(settings.STORAGE_PATH, "recordings_metadata.json")
        self._ensure_directory()
        self._ensure_metadata_file()
    
    def _ensure_directory(self):
        """Kayıtlar dizinini oluşturur."""
        os.makedirs(self.recordings_path, exist_ok=True)
    
    def _ensure_metadata_file(self):
        """Metadata dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.recordings_metadata_file):
            with open(self.recordings_metadata_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def save_recording(
        self,
        audio_data: bytes,
        user_id: str,
        recording_name: str,
        character_id: Optional[str] = None,
        story_id: Optional[str] = None
    ) -> Dict:
        """
        Ses kaydını kaydeder.
        
        Args:
            audio_data: Ses dosyası verisi (bytes)
            user_id: Kullanıcı ID'si
            recording_name: Kayıt adı
            character_id: Karakter ID'si (karakter sesi için)
            story_id: Hikâye ID'si (hikâye seslendirmesi için)
        
        Returns:
            Kayıt objesi
        """
        recording_id = str(uuid.uuid4())
        recording_path = os.path.join(self.recordings_path, f"{recording_id}.mp3")
        
        # Ses dosyasını kaydet
        with open(recording_path, 'wb') as f:
            f.write(audio_data)
        
        # Metadata kaydet
        recording = {
            "recording_id": recording_id,
            "user_id": user_id,
            "recording_name": recording_name,
            "character_id": character_id,
            "story_id": story_id,
            "file_path": f"/storage/recordings/{recording_id}.mp3",
            "created_at": datetime.now().isoformat(),
            "duration": self._get_audio_duration(recording_path)
        }
        
        self._save_metadata(recording)
        
        return recording
    
    def _get_audio_duration(self, file_path: str) -> float:
        """Ses dosyasının süresini alır (saniye)."""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Milisaniyeden saniyeye
        except:
            return 0.0
    
    def _save_metadata(self, recording: Dict):
        """Metadata'yı kaydeder."""
        with open(self.recordings_metadata_file, 'r', encoding='utf-8') as f:
            recordings = json.load(f)
        
        recordings.append(recording)
        
        with open(self.recordings_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(recordings, f, ensure_ascii=False, indent=2)
    
    def get_user_recordings(self, user_id: str) -> list:
        """Kullanıcının kayıtlarını getirir."""
        try:
            with open(self.recordings_metadata_file, 'r', encoding='utf-8') as f:
                recordings = json.load(f)
            return [r for r in recordings if r.get('user_id') == user_id]
        except:
            return []
    
    def get_recording(self, recording_id: str) -> Optional[Dict]:
        """Kaydı getirir."""
        try:
            with open(self.recordings_metadata_file, 'r', encoding='utf-8') as f:
                recordings = json.load(f)
            return next((r for r in recordings if r.get('recording_id') == recording_id), None)
        except:
            return None
    
    def delete_recording(self, recording_id: str) -> bool:
        """Kaydı siler."""
        recording = self.get_recording(recording_id)
        if not recording:
            return False
        
        # Dosyayı sil
        file_path = os.path.join(settings.STORAGE_PATH, recording['file_path'].replace('/storage/', ''))
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        # Metadata'dan sil
        with open(self.recordings_metadata_file, 'r', encoding='utf-8') as f:
            recordings = json.load(f)
        
        recordings = [r for r in recordings if r.get('recording_id') != recording_id]
        
        with open(self.recordings_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(recordings, f, ensure_ascii=False, indent=2)
        
        return True
    
    async def edit_recording(
        self,
        recording_id: str,
        trim_start: Optional[float] = None,
        trim_end: Optional[float] = None,
        volume_adjust: Optional[float] = None,
        fade_in: Optional[float] = None,
        fade_out: Optional[float] = None
    ) -> Dict:
        """
        Ses kaydını düzenler.
        
        Args:
            recording_id: Kayıt ID'si
            trim_start: Başlangıçtan kesme (saniye)
            trim_end: Sondan kesme (saniye)
            volume_adjust: Ses seviyesi ayarı (-20 ile +20 dB arası)
            fade_in: Fade in süresi (saniye)
            fade_out: Fade out süresi (saniye)
        
        Returns:
            Düzenlenmiş kayıt objesi
        """
        recording = self.get_recording(recording_id)
        if not recording:
            raise ValueError("Kayıt bulunamadı")
        
        file_path = os.path.join(settings.STORAGE_PATH, recording['file_path'].replace('/storage/', ''))
        
        if not os.path.exists(file_path):
            raise ValueError("Ses dosyası bulunamadı")
        
        # Ses dosyasını yükle
        audio = AudioSegment.from_file(file_path)
        
        # Trim
        if trim_start:
            start_ms = int(trim_start * 1000)
            audio = audio[start_ms:]
        
        if trim_end:
            end_ms = int(trim_end * 1000)
            audio = audio[:-end_ms]
        
        # Ses seviyesi
        if volume_adjust:
            audio = audio + volume_adjust  # dB cinsinden
        
        # Fade in/out
        if fade_in:
            audio = audio.fade_in(int(fade_in * 1000))
        
        if fade_out:
            audio = audio.fade_out(int(fade_out * 1000))
        
        # Yeni dosyayı kaydet
        new_recording_id = str(uuid.uuid4())
        new_file_path = os.path.join(self.recordings_path, f"{new_recording_id}.mp3")
        audio.export(new_file_path, format="mp3")
        
        # Yeni kayıt metadata
        new_recording = {
            "recording_id": new_recording_id,
            "user_id": recording.get('user_id'),
            "recording_name": f"{recording.get('recording_name')} (Düzenlenmiş)",
            "character_id": recording.get('character_id'),
            "story_id": recording.get('story_id'),
            "file_path": f"/storage/recordings/{new_recording_id}.mp3",
            "created_at": datetime.now().isoformat(),
            "duration": len(audio) / 1000.0,
            "edited_from": recording_id
        }
        
        self._save_metadata(new_recording)
        
        return new_recording

