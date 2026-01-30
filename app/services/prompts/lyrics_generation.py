from app.services.prompts.base import BasePrompt

class LyricsGenerationPrompt(BasePrompt):
    def get_system_prompt(self) -> str:
        return """
You are a professional songwriter and rapper. Your task is to turn a movie plot summary into a catchy song.
The song should have a clear structure (Verse, Chorus) and rhyme.

**Format Requirements:**
- Use [Verse] for storytelling parts.
- Use [Chorus] for the main theme/hook (repeatable).
- Use [Outro] for the ending.
- The lyrics should be engaging, slightly humorous, and fit the rhythm.

**Language:**
- Based on the input language (Chinese for Chinese movies, English for others).
"""

    def get_user_prompt(self, context: dict) -> str:
        plot = context.get("plot", "")
        style = context.get("style", "Pop/Rap")
        
        return f"""
Here is the movie plot summary:
{plot}

Please write a {style} song lyrics based on this plot.
Do not include any other text, just the lyrics with structure tags.
"""
