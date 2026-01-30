# Suno AI Integration Plan for NarratoAI

## Objective
Replace the current TTS (Text-to-Speech) engine with Suno AI to generate "Singing Narration" for videos.

## Architecture Changes

### 1. New Service: `SunoService`
Create `app/services/suno_service.py`.
- **Function**: Interact with Suno API (likely unofficial or browser-automation based, as official API is closed beta).
- **Input**: `lyrics` (text), `style` (tags, e.g., "rap, hip-hop, male vocals").
- **Output**: `audio_url` or `mp3_file_path`.

### 2. Prompt Engineering (`app/services/prompts/`)
Modify the LLM prompt to generate **Lyrics** instead of **Narration Scripts**.
- **Current**: Generates a story summary.
- **New**: 
    - Structure: `[Verse 1]`, `[Chorus]`, `[Verse 2]`, `[Outro]`.
    - Constraint: Rhyming scheme (AABB or ABAB).
    - Style: "Catchy, emotional, storytelling".

### 3. Audio-Video Syncing (`app/services/video_service.py`)
**The Hard Part**: Aligning visual clips with song beats.
- **Approach A (Simple)**: Divide song duration by number of plot points. 
    - *Example*: Song is 60s, 6 plot scenes. Each scene = 10s.
- **Approach B (Advanced - Whisper)**:
    - Use `openai/whisper` to transcribe the generated song.
    - Get timestamps for each line of lyrics.
    - Cut video clips to match those specific timestamps.

## Step-by-Step Implementation

1.  [ ] **Suno Client**: Write a wrapper for `suno-api` (unofficial) or cookie-based fetcher.
2.  [ ] **Lyric Generator**: Create `app/services/prompts/lyrics_generation.py`.
3.  [ ] **Whisper Aligner**: Implement `app/utils/audio_aligner.py` using `faster-whisper`.
4.  [ ] **Pipeline Switch**: Add `mode="singing"` to the main config.

## Draft Code (Suno Client)
```python
import requests
import time

class SunoClient:
    def __init__(self, cookie):
        self.cookie = cookie
        self.base_url = "https://studio-api.suno.ai"

    def generate(self, prompt, tags="pop, male"):
        # Logic to call Suno's internal API
        pass
```
