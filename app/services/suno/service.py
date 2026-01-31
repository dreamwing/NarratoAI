import time
import logging
from typing import List, Dict, Optional
from .base import SunoProvider
from .openai_hk import OpenAIHKSunoProvider
from app.config import config

logger = logging.getLogger(__name__)

class SunoService:
    def __init__(self, provider_type: str = "openai-hk"):
        # Allow override from config
        self.provider_type = config.suno.get("provider", provider_type)
        self.provider: SunoProvider = self._get_provider(self.provider_type)

    def _get_provider(self, provider_type: str) -> SunoProvider:
        if provider_type == "openai-hk":
            return OpenAIHKSunoProvider()
        else:
            raise ValueError(f"Unknown Suno provider: {provider_type}")

    def generate_song(self, prompt: str, tags: str, title: str, wait: bool = True) -> Dict:
        """
        High-level function to generate a song.
        If wait=True, it polls until completion.
        Returns the best completed clip (with audio_url).
        """
        clip_ids = self.provider.generate_music(prompt, tags, title)
        
        if not wait:
            return {"status": "submitted", "clip_ids": clip_ids}
        
        # Polling logic
        logger.info(f"Waiting for Suno generation (Clips: {clip_ids})...")
        max_attempts = 30 # 30 * 10s = 5 mins
        
        for attempt in range(max_attempts):
            time.sleep(10)
            status_list = self.provider.get_status(clip_ids)
            
            # Check for completion
            completed_clips = [c for c in status_list if c.get('status') == 'complete' or c.get('audio_url')]
            
            if completed_clips:
                logger.info("Suno generation complete!")
                # Return the first one for now
                return completed_clips[0]
                
            # Log progress
            statuses = [c.get('status') for c in status_list]
            logger.debug(f"Poll #{attempt+1}: {statuses}")
            
        raise TimeoutError("Suno generation timed out after 5 minutes.")
