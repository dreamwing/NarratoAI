import os
from uuid import uuid4
from loguru import logger
from typing import Dict, List, Optional, Tuple

from app.services import material


class VideoService:
    @staticmethod
    async def crop_video(
        video_path: str,
        video_script: List[dict]
    ) -> Tuple[str, Dict[str, str]]:
        """
        裁剪视频服务
        
        Args:
            video_path: 视频文件路径
            video_script: 视频脚本列表
            
        Returns:
            Tuple[str, Dict[str, str]]: (task_id, 裁剪后的视频片段字典)
            视频片段字典格式: {timestamp: video_path}
        """
        try:
            task_id = str(uuid4())
            
            # 从脚本中提取时间戳列表
            time_list = [scene['timestamp'] for scene in video_script]
            
            # 调用裁剪服务
            subclip_videos = material.clip_videos(
                task_id=task_id,
                timestamp_terms=time_list,
                origin_video=video_path
            )
            
            if subclip_videos is None:
                raise ValueError("裁剪视频失败")
                
            # 更新脚本中的视频路径
            for scene in video_script:
                try:
                    scene['path'] = subclip_videos[scene['timestamp']]
                except KeyError as err:
                    logger.error(f"更新视频路径失败: {err}")
                    
            logger.debug(f"裁剪视频成功，共生成 {len(time_list)} 个视频片段")
            logger.debug(f"视频片段路径: {subclip_videos}")
            
            return task_id, subclip_videos
            
        except Exception as e:
            logger.exception("裁剪视频失败")
            raise

    @staticmethod
    async def generate_music_video(
        video_path: str,
        audio_path: str,
        lyrics_text: str,
        suno_service
    ) -> List[dict]:
        """
        Generate video script aligned with music lyrics using Whisper.
        """
        logger.info("🎵 Starting Music Video Generation Pipeline...")
        
        # 1. Get aligned timestamps using Whisper
        # aligned_lyrics = [{'text': 'Hello', 'start': 0.0, 'end': 1.5, ...}]
        aligned_lyrics = suno_service.get_lyrics_timestamp(audio_path, lyrics_text)
        
        if not aligned_lyrics:
            logger.warning("⚠️ Whisper alignment failed or no lyrics found. Falling back to simple segmentation.")
            # Fallback: simple equal segmentation if whisper fails
            # TODO: Implement simple fallback
            return []

        # 2. Convert to video script format
        video_script = []
        
        # We need to map each lyric line to a video clip from the source video
        # Strategy: Randomly pick scenes or sequentially pick scenes from source video?
        # Let's try: Sequentially cut clips from the source video that match the lyric duration.
        
        # Get source video duration
        from moviepy.editor import VideoFileClip
        try:
            source_clip = VideoFileClip(video_path)
            source_duration = source_clip.duration
            source_clip.close()
        except Exception:
            source_duration = 3600 # Assume long enough if check fails
        
        current_video_time = 0.0
        
        for i, segment in enumerate(aligned_lyrics):
            start_time = segment['start']
            end_time = segment['end']
            duration = end_time - start_time
            
            if duration < 0.5: continue # Skip too short segments
            
            # Select a clip from source video
            # Ensure we don't go past the end of the source video
            clip_start = current_video_time
            clip_end = clip_start + duration
            
            if clip_end > source_duration:
                # Loop back to beginning if source video is shorter than song
                current_video_time = 0.0
                clip_start = 0.0
                clip_end = duration
            
            # Create script item
            # Format: '00:00:10,000-00:00:15,000'
            from app.services.material import format_timestamp
            timestamp_str = f"{format_timestamp(clip_start)}-{format_timestamp(clip_end)}"
            
            video_script.append({
                "line_no": i + 1,
                "narration": segment['text'], # Lyric text
                "timestamp": timestamp_str,
                "duration": duration,
                "path": "" # Will be filled by crop_video
            })
            
            current_video_time = clip_end

        return video_script
 