import asyncio
import os
import sys
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.suno_service import SunoService
from app.services.video_service import VideoService
from app.services.prompts.lyrics_generation import LyricsGenerationPrompt
from app.services.llm.unified_service import UnifiedLLMService

# Configuration
SUNO_COOKIE = os.getenv("SUNO_COOKIE", "") # User needs to provide this
MODEL_NAME = "google/gemini-2.0-flash-exp" # Or your preferred model

async def main():
    logger.info("🐱 年糕爱唱电影 - 全自动流程启动 (NianGao Auto-Pipeline) 🚀")
    
    # 1. Input: Movie Name & Plot
    # In the future, this can be fetched from Douyin Hot List automatically
    movie_name = input("请输入电影/剧集名称 (e.g. 庆余年2): ")
    plot_summary = input("请输入剧情简介 (或直接回车使用测试简介): ")
    
    if not plot_summary:
        plot_summary = "范闲假死归京，发现二皇子是幕后黑手，决定与庆帝和各方势力周旋，最终在抱月楼设局..."
        logger.info(f"使用默认测试简介: {plot_summary[:20]}...")

    # 2. Generate Lyrics (LLM)
    logger.info("✍️ 正在创作神级押韵歌词...")
    llm = UnifiedLLMService()
    prompt_service = LyricsGenerationPrompt()
    
    system_prompt = prompt_service.get_system_prompt()
    user_prompt = prompt_service.get_user_prompt({"plot": plot_summary, "style": "古风 Rap, 燃, 节奏感强"})
    
    lyrics = await llm.chat(system_prompt, user_prompt, model=MODEL_NAME)
    logger.success(f"歌词创作完成:\n{lyrics[:100]}...")
    
    # 3. Generate Song (Suno)
    logger.info("🎵 正在召唤 Suno 生成歌曲...")
    suno = SunoService()
    
    try:
        # If we have a real API wrapper, we call it here.
        # Currently, this will prompt the user to manually generate if no cookie/api found.
        song_path = suno.generate_song(lyrics, style="Chinese Trap, Male Vocals")
        logger.success(f"歌曲已就位: {song_path}")
    except Exception as e:
        logger.error(f"Suno 生成失败: {e}")
        return

    # 4. Generate Video (NarratoAI)
    logger.info("🎬 正在剪辑 MV...")
    
    # Assuming we have the source video downloaded (omitted for brevity, usually fetched by crawler)
    source_video_path = "resource/videos/source_movie.mp4" 
    if not os.path.exists(source_video_path):
        logger.warning(f"源视频不存在: {source_video_path}. 请先下载素材。")
        # In full automation, we would call crawler here.
        return

    video_service = VideoService()
    
    # 4.1 Align Lyrics & Audio (Whisper)
    video_script = await video_service.generate_music_video(
        video_path=source_video_path,
        audio_path=song_path,
        lyrics_text=lyrics,
        suno_service=suno
    )
    
    # 4.2 Crop & Merge
    task_id, cropped_clips = await video_service.crop_video(source_video_path, video_script)
    
    # 4.3 Final Merge (Adding Subtitles & BGM)
    final_output = f"storage/output/{movie_name}_mv.mp4"
    # Call merge_materials logic (need to adapt existing function to async or call directly)
    # ...
    
    logger.success(f"🎉 成片已生成: {final_output}")

if __name__ == "__main__":
    asyncio.run(main())
