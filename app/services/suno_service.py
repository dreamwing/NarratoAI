import os
import time
from loguru import logger
from app.utils.utils import get_project_dir

class SunoService:
    def __init__(self):
        self.songs_dir = os.path.join(get_project_dir(), "resource", "songs")
        os.makedirs(self.songs_dir, exist_ok=True)

    def generate_song(self, lyrics: str, style: str = "pop") -> str:
        """
        Mock implementation.
        In a real scenario, this would call Suno API.
        Current logic: Save lyrics to file, wait for user to provide mp3.
        """
        logger.info(f"🎵 Generating song with style: {style}")
        
        # 1. Save lyrics for the user to copy
        lyrics_file = os.path.join(self.songs_dir, "current_lyrics.txt")
        with open(lyrics_file, "w", encoding="utf-8") as f:
            f.write(f"Style: {style}\n\n")
            f.write(lyrics)
        
        logger.warning(f"⚠️ AUTO-GENERATION NOT AVAILABLE. Please manually generate song on Suno.")
        logger.warning(f"📄 Lyrics saved to: {lyrics_file}")
        
        # 2. Define expected audio path
        expected_audio_path = os.path.join(self.songs_dir, "current_song.mp3")
        
        # 3. Check if file exists (or wait loop if interactive)
        # For automation flow, we assume the file might be placed there by another process
        # or we just fail if not present.
        
        if os.path.exists(expected_audio_path):
            logger.success(f"✅ Found existing song file: {expected_audio_path}")
            return expected_audio_path
        else:
            logger.error(f"❌ Song file not found at {expected_audio_path}. Please place the generated MP3 there.")
            raise FileNotFoundError(f"Missing {expected_audio_path}")

    def get_lyrics_timestamp(self, audio_path: str, lyrics_text: str):
        """
        Use Whisper to align audio with lyrics.
        Returns a list of dicts: [{'text': line, 'start': 0.0, 'end': 2.5}, ...]
        """
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            logger.error("❌ faster-whisper not installed. Install it to use audio alignment.")
            return []

        logger.info("🎙️ Starting Whisper alignment...")
        
        # Use 'base' or 'small' model for speed on CPU
        model_size = "tiny" 
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        segments, info = model.transcribe(audio_path, beam_size=5, word_timestamps=False)

        aligned_lyrics = []
        for segment in segments:
            aligned_lyrics.append({
                "text": segment.text.strip(),
                "start": segment.start,
                "end": segment.end,
                "duration": segment.end - segment.start
            })
            logger.debug(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

        return aligned_lyrics
