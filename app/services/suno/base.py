from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class SunoProvider(ABC):
    """Abstract Base Class for Suno Music Generation Providers."""

    @abstractmethod
    def generate_music(self, prompt: str, tags: str, title: str, mv: str = "chirp-v3-5") -> List[str]:
        """
        Initiate music generation.
        Returns a list of Clip IDs (usually 2).
        """
        pass

    @abstractmethod
    def get_status(self, clip_ids: List[str]) -> List[Dict]:
        """
        Check status of clips.
        Returns list of clip objects with status, audio_url, etc.
        """
        pass
