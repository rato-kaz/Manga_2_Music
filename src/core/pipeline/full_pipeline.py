"""
Full Pipeline Integration: Manga to Audio.

This module integrates all stages:
1. Visual analysis (MAGI-V2)
2. Semantic extraction
3. Timeline generation
4. Audio generation (BGM + SFX)
5. TTS generation
6. Final audio mixing
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional
import json

from src.infrastructure.logger import get_logger

# Import all modules
from src.core.pipeline.pipeline_generate_json import (
    generate_json_for_chapter,
    prepare_images,
    load_magiv2,
    read_image,
)
from src.core.pipeline.pipeline_enhanced import (
    enhance_json_with_reading_order,
    enhance_json_with_character_reid,
    enhance_json_with_manpu,
    enhance_json_with_onomatopoeia,
    enhance_json_with_speaker_diarization,
)
from src.core.semantic.semantic_extractor import extract_semantic_contexts_for_chapter
from src.core.semantic.timeline_generator import generate_timeline_for_chapter
from src.core.audio.audio_generator import (
    generate_audio_for_chapter,
    MusicGenWrapper,
    AudioGenWrapper,
)
from src.core.audio.audio_mixer import mix_chapter_audio, AudioMixer
from src.core.tts.tts_engine import (
    generate_speech_for_chapter,
    VoiceProfileManager,
    StyleBertVITS2Wrapper,
)

logger = get_logger(__name__)


def process_manga_chapter(
    chapter_images: List[Path],
    manga_name: str,
    chapter_number: int,
    output_dir: Path,
    *,
    # Model options
    device: str = "cuda",
    text_language: str = "ja",
    # Enhancement flags
    enable_reading_order: bool = True,
    enable_character_reid: bool = True,
    enable_manpu: bool = True,
    enable_onomatopoeia: bool = True,
    enable_speaker_diarization: bool = True,
    # Audio generation flags
    enable_bgm: bool = True,
    enable_sfx: bool = True,
    enable_tts: bool = True,
    # Output options
    save_intermediate_json: bool = True,
) -> Dict:
    """
    Process a manga chapter through the full pipeline.
    
    Args:
        chapter_images: List of image paths for the chapter
        manga_name: Name of the manga
        chapter_number: Chapter number
        output_dir: Output directory for all files
        device: Device to use ('cpu' or 'cuda')
        text_language: Language code
        enable_*: Flags to enable/disable features
        save_intermediate_json: Whether to save intermediate JSON
    
    Returns:
        Dictionary with output paths and metadata
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing chapter {chapter_number} of {manga_name}")
    logger.info(f"Total pages: {len(chapter_images)}")
    
    # Stage 1: Visual Analysis (MAGI-V2)
    logger.info("Stage 1: Visual Analysis")
    import torch
    device_obj = torch.device(device)
    model = load_magiv2(device_obj)
    
    pages, arrays = prepare_images(chapter_images, max_long_edge=1600)
    
    # Generate base JSON
    chapter_entries = generate_json_for_chapter(
        model=model,
        device=device_obj,
        manga_name=manga_name,
        chapter_label=f"Chapter_{chapter_number}",
        chapter_number=chapter_number,
        images=chapter_images,
        text_language=text_language,
    )
    
    # Stage 2: Enhancements
    if enable_reading_order:
        logger.info("Stage 2a: Reading Order Resolution")
        chapter_entries = enhance_json_with_reading_order(chapter_entries, pages)
    
    if enable_character_reid:
        logger.info("Stage 2b: Character Re-ID")
        chapter_entries = enhance_json_with_character_reid(chapter_entries, pages)
    
    if enable_manpu:
        logger.info("Stage 2c: Manpu Detection")
        chapter_entries = enhance_json_with_manpu(chapter_entries, pages)
    
    if enable_onomatopoeia:
        logger.info("Stage 2d: Onomatopoeia Classification")
        chapter_entries = enhance_json_with_onomatopoeia(chapter_entries, pages)
    
    if enable_speaker_diarization:
        logger.info("Stage 2e: Speaker Diarization")
        chapter_entries = enhance_json_with_speaker_diarization(chapter_entries, pages)
    
    # Stage 3: Semantic Extraction
    logger.info("Stage 3: Semantic Extraction")
    chapter_entries = extract_semantic_contexts_for_chapter(chapter_entries)
    
    # Stage 4: Timeline Generation
    logger.info("Stage 4: Timeline Generation")
    timeline_entries = generate_timeline_for_chapter(chapter_entries, text_language)
    
    # Save intermediate JSON
    if save_intermediate_json:
        json_path = output_dir / "chapter_metadata.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(chapter_entries, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved metadata to {json_path}")
    
    # Stage 5: Audio Generation
    audio_output_dir = output_dir / "audio"
    audio_output_dir.mkdir(parents=True, exist_ok=True)
    
    music_gen = None
    audio_gen = None
    
    if enable_bgm or enable_sfx:
        logger.info("Stage 5: Audio Generation")
        
        if enable_bgm:
            music_gen = MusicGenWrapper(device=device)
        if enable_sfx:
            audio_gen = AudioGenWrapper(device=device)
        
        audio_map = generate_audio_for_chapter(
            chapter_entries,
            audio_output_dir,
            music_gen=music_gen if enable_bgm else None,
            audio_gen=audio_gen if enable_sfx else None,
        )
    
    # Stage 6: TTS Generation
    tts_output_dir = output_dir / "speech"
    tts_output_dir.mkdir(parents=True, exist_ok=True)
    
    if enable_tts:
        logger.info("Stage 6: TTS Generation")
        voice_manager = VoiceProfileManager(output_dir / "voice_profiles.json")
        tts_engine = StyleBertVITS2Wrapper(device=device)
        
        speech_map = generate_speech_for_chapter(
            chapter_entries,
            tts_output_dir,
            voice_manager=voice_manager,
            tts_engine=tts_engine,
        )
    
    # Stage 7: Final Audio Mixing
    logger.info("Stage 7: Audio Mixing")
    mixer = AudioMixer()
    final_audio_path = output_dir / "final_audio.wav"
    
    mix_chapter_audio(
        chapter_entries,
        final_audio_path,
        mixer=mixer,
    )
    
    logger.info(f"Pipeline completed successfully. Output: {final_audio_path}")
    
    # Return summary
    return {
        "chapter_number": chapter_number,
        "manga_name": manga_name,
        "metadata_json": str(output_dir / "chapter_metadata.json") if save_intermediate_json else None,
        "final_audio": str(final_audio_path),
        "audio_dir": str(audio_output_dir),
        "speech_dir": str(tts_output_dir) if enable_tts else None,
        "num_pages": len(chapter_entries),
        "num_panels": sum(len(page.get("content", [])) for page in chapter_entries),
    }


def process_manga_volume(
    manga_root: Path,
    output_root: Path,
    max_chapters: Optional[int] = None,
    **kwargs,
) -> List[Dict]:
    """
    Process entire manga volume (multiple chapters).
    
    Args:
        manga_root: Root directory containing chapter folders
        output_root: Root output directory
        max_chapters: Maximum chapters to process
        **kwargs: Additional arguments passed to process_manga_chapter
    
    Returns:
        List of processing results
    """
    from pipeline_generate_json import list_chapter_image_paths
    
    chapter_map = list_chapter_image_paths(manga_root)
    manga_name = manga_root.name
    
    results: List[Dict] = []
    
    for idx, (chapter_label, image_paths) in enumerate(sorted(chapter_map.items())):
        if max_chapters is not None and idx >= max_chapters:
            break
        
        chapter_number = idx + 1
        chapter_output_dir = output_root / f"chapter_{chapter_number}"
        
        result = process_manga_chapter(
            image_paths,
            manga_name,
            chapter_number,
            chapter_output_dir,
            **kwargs,
        )
        
        results.append(result)
    
    return results

