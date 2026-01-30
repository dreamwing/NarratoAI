import requests
import time
import json
import re
from loguru import logger

class SunoClient:
    """
    Unofficial client for Suno.ai
    Requires a valid cookie ('__client_oid', 'suno_session', etc.) from a logged-in browser session.
    """
    
    BASE_URL = "https://studio-api.suno.ai"
    
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie,
            "Origin": "https://suno.com",
            "Referer": "https://suno.com/",
        }
        self.sid = None 
        # Extract session ID if possible, or just rely on cookie
        
    def generate_music(self, prompt: str, tags: str = "", title: str = "", make_instrumental: bool = False, wait_for_completion: bool = True):
        """
        Trigger music generation.
        Returns a list of clip IDs (usually 2).
        """
        url = f"{self.BASE_URL}/api/generate/v2/"
        
        payload = {
            "prompt": prompt,
            "tags": tags,
            "title": title,
            "make_instrumental": make_instrumental,
            "wait_audio": False 
        }
        
        logger.info(f"🎵 Suno Request: {title} [{tags}]")
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            # Suno returns a list of clips. usually 2.
            clips = data.get("clips", [])
            clip_ids = [c["id"] for c in clips]
            logger.success(f"✅ Generation started. Clip IDs: {clip_ids}")
            
            if wait_for_completion:
                return self._wait_for_audio(clip_ids)
            return clip_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to generate music: {e}")
            logger.error(f"Response: {resp.text if 'resp' in locals() else 'N/A'}")
            raise

    def _wait_for_audio(self, clip_ids: list, max_retries=60, sleep_sec=5):
        """
        Poll status until audio is ready.
        """
        completed_clips = {}
        
        for i in range(max_retries):
            # Check all clips
            # API to get feed/specific clips: GET /api/feed/?ids=...
            ids_str = ",".join(clip_ids)
            url = f"{self.BASE_URL}/api/feed/?ids={ids_str}"
            
            try:
                resp = requests.get(url, headers=self.headers)
                data = resp.json()
                
                for clip in data:
                    c_id = clip["id"]
                    status = clip.get("status")
                    
                    if status == "streaming" or status == "complete":
                        if c_id not in completed_clips:
                            audio_url = clip.get("audio_url")
                            if audio_url:
                                logger.info(f"✨ Clip {c_id} is ready: {audio_url}")
                                completed_clips[c_id] = audio_url
                    
                    elif status == "error":
                        logger.error(f"❌ Clip {c_id} failed.")
                        completed_clips[c_id] = None # Mark as failed
                
                # If all requested clips are accounted for
                if len(completed_clips) == len(clip_ids):
                    return completed_clips
                
                logger.debug(f"⏳ Waiting for audio... ({i+1}/{max_retries})")
                time.sleep(sleep_sec)
                
            except Exception as e:
                logger.warning(f"⚠️ Error polling status: {e}")
                time.sleep(sleep_sec)
                
        raise TimeoutError("Suno generation timed out.")

    def download_audio(self, url: str, save_path: str):
        """Download MP3 from the URL"""
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            logger.success(f"💾 Saved to {save_path}")
        else:
            logger.error(f"❌ Download failed: {r.status_code}")

