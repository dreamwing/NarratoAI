import time
import requests
import logging
from typing import List, Dict, Optional
from .base import SunoProvider
from app.config import config

logger = logging.getLogger(__name__)

class OpenAIHKSunoProvider(SunoProvider):
    """
    Suno Provider using OpenAI-HK relay API.
    Doc: https://www.openai-hk.com/docs/lab/suno-v3.html
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.suno.get("api_key")
        self.base_url = "https://api.openai-hk.com/sunoapi"
        if not self.api_key:
            raise ValueError("SUNO_API_KEY is not set in config.toml [suno] section.")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_music(self, prompt: str, tags: str, title: str, mv: str = "chirp-v3-5") -> List[str]:
        """
        Sends generation request. Returns list of clip IDs.
        """
        url = f"{self.base_url}/generate"
        payload = {
            "prompt": prompt,
            "tags": tags,
            "title": title,
            "mv": mv
        }

        try:
            logger.info(f"Sending Suno generation request: {title}")
            response = requests.post(url, json=payload, headers=self._headers(), timeout=15)
            response.raise_for_status()
            
            data = response.json()
            clips = data.get("clips", [])
            
            if not clips:
                logger.error(f"Suno API returned no clips: {data}")
                raise RuntimeError("No clips returned from Suno API")
                
            clip_ids = [clip["id"] for clip in clips]
            logger.info(f"Generation started. Clip IDs: {clip_ids}")
            return clip_ids

        except requests.Timeout:
            logger.error("Suno API request timed out.")
            raise
        except Exception as e:
            logger.error(f"Suno API failed: {e}")
            raise

    def get_status(self, clip_ids: List[str]) -> List[Dict]:
        """
        Check status of clips.
        """
        ids_str = ",".join(clip_ids)
        url = f"{self.base_url}/feed/{ids_str}"
        
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to check Suno status: {e}")
            return []
