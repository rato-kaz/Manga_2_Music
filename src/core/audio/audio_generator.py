"""
Audio Generation Module for Manga-to-Music.

This module handles:
- BGM generation using MusicGen
- SFX generation using AudioGen/AudioLDM
- Audio prompt engineering
- Loop generation for seamless playback
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AudioPrompt:
    """Represents an audio generation prompt."""

    scene_type: str
    emotions: List[str]
    intensity: float
    location: Optional[str] = None
    time_of_day: Optional[str] = None
    mood: str = "neutral"
    duration: float = 30.0  # Seconds
    is_loop: bool = True


@dataclass
class GeneratedAudio:
    """Represents a generated audio file."""

    file_path: Path
    duration: float
    audio_type: str  # 'bgm' or 'sfx'
    prompt: AudioPrompt
    is_loop: bool = False


# Music prompt templates based on scene and emotion
MUSIC_PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "battle": {
        "high_intensity": "Industrial techno, distorted bass, high tempo 140bpm, metallic percussion, aggressive, action sequence, cinematic, intense",
        "medium_intensity": "Epic orchestral, dramatic strings, powerful drums, battle theme, heroic, cinematic",
        "low_intensity": "Tense ambient, low strings, building tension, suspenseful, cinematic",
    },
    "romance": {
        "high_intensity": "Romantic piano, emotional strings, passionate, heartfelt, cinematic love theme",
        "medium_intensity": "Soft piano, gentle strings, romantic, sweet, tender, emotional",
        "low_intensity": "Ambient piano, peaceful, calm, romantic atmosphere, gentle",
    },
    "comedy": {
        "high_intensity": "Upbeat jazz, playful, bouncy, comedic, light-hearted, fun",
        "medium_intensity": "Cheerful melody, happy, light, playful, comedic",
        "low_intensity": "Gentle comedy, light-hearted, pleasant, cheerful",
    },
    "drama": {
        "high_intensity": "Emotional orchestral, dramatic, intense, powerful, cinematic drama",
        "medium_intensity": "Melancholic piano, emotional, sad, touching, dramatic",
        "low_intensity": "Quiet piano, contemplative, sad, emotional, gentle",
    },
    "action": {
        "high_intensity": "Fast-paced electronic, energetic, driving beat, action-packed, intense",
        "medium_intensity": "Upbeat rock, energetic, exciting, action theme",
        "low_intensity": "Rhythmic ambient, movement, dynamic, action-oriented",
    },
    "slice_of_life": {
        "high_intensity": "Upbeat acoustic, cheerful, everyday life, pleasant, happy",
        "medium_intensity": "Gentle acoustic, peaceful, daily life, calm, pleasant",
        "low_intensity": "Quiet ambient, peaceful, calm, everyday atmosphere",
    },
    "horror": {
        "high_intensity": "Dark ambient, eerie, tense, horror, suspenseful, scary",
        "medium_intensity": "Creepy atmosphere, unsettling, tense, horror theme",
        "low_intensity": "Subtle tension, quiet, eerie, unsettling",
    },
}


def build_music_prompt(
    scene_context: Dict,
    custom_prompt: Optional[str] = None,
) -> str:
    """
    Build music generation prompt from scene context.

    This implements M2M-Gen style prompt engineering.

    Args:
        scene_context: Scene context dictionary
        custom_prompt: Optional custom prompt override

    Returns:
        Music generation prompt string
    """
    if custom_prompt:
        return custom_prompt

    scene_type = scene_context.get("scene_type", "slice_of_life")
    intensity = scene_context.get("intensity", 0.5)
    location = scene_context.get("location")
    time_of_day = scene_context.get("time_of_day")
    emotions = scene_context.get("emotion_tags", [])

    # Determine intensity level
    if intensity >= 0.7:
        intensity_level = "high_intensity"
    elif intensity >= 0.4:
        intensity_level = "medium_intensity"
    else:
        intensity_level = "low_intensity"

    # Get base prompt
    if scene_type in MUSIC_PROMPT_TEMPLATES:
        base_prompt = MUSIC_PROMPT_TEMPLATES[scene_type].get(
            intensity_level, MUSIC_PROMPT_TEMPLATES[scene_type].get("medium_intensity", "")
        )
    else:
        base_prompt = MUSIC_PROMPT_TEMPLATES["slice_of_life"]["medium_intensity"]

    # Add location context
    if location:
        location_prompts = {
            "indoors": "indoor atmosphere, intimate",
            "outdoors": "outdoor atmosphere, open space",
            "city": "urban, city atmosphere",
            "nature": "natural, nature sounds, peaceful",
            "school": "school atmosphere, youthful",
            "home": "homey, comfortable atmosphere",
        }
        if location in location_prompts:
            base_prompt += f", {location_prompts[location]}"

    # Add time of day
    if time_of_day:
        time_prompts = {
            "night": "nighttime atmosphere, dark",
            "day": "daytime, bright",
            "dawn": "dawn, early morning, peaceful",
            "dusk": "dusk, evening, calm",
        }
        if time_of_day in time_prompts:
            base_prompt += f", {time_prompts[time_of_day]}"

    # Add primary emotion
    if emotions:
        primary_emotion = emotions[0]
        emotion_prompts = {
            "anger": "aggressive, intense",
            "joy": "happy, cheerful",
            "sadness": "melancholic, emotional",
            "love": "romantic, passionate",
            "fear": "tense, suspenseful",
            "excitement": "energetic, exciting",
        }
        if primary_emotion in emotion_prompts:
            base_prompt += f", {emotion_prompts[primary_emotion]}"

    return base_prompt


def build_sfx_prompt(
    onomatopoeia_data: Dict,
) -> str:
    """
    Build SFX generation prompt from onomatopoeia data.

    Args:
        onomatopoeia_data: Onomatopoeia detection data

    Returns:
        SFX generation prompt string
    """
    audio_keywords = onomatopoeia_data.get("audio_keywords", [])
    onomatopoeia_type = onomatopoeia_data.get("onomatopoeia_type", "giongo")

    if not audio_keywords:
        return ""

    # Build prompt from keywords
    prompt = ", ".join(audio_keywords)

    # Add type context
    if onomatopoeia_type == "giongo":
        prompt += ", sound effect, realistic"
    else:  # gitaigo
        prompt += ", ambient, atmosphere, mood"

    return prompt


class MusicGenWrapper:
    """
    Wrapper for MusicGen music generation.

    Note: This is a placeholder implementation.
    In production, this would interface with the actual MusicGen model.
    """

    def __init__(self, model_size: str = "medium", device: str = "cuda"):
        """
        Initialize MusicGen wrapper.

        Args:
            model_size: Model size ('small', 'medium', 'large')
            device: Device to use ('cpu' or 'cuda')
        """
        self.model_size = model_size
        self.device = device
        self.model = None
        # In production, load model here:
        # from audiocraft.models import MusicGen
        # self.model = MusicGen.get_pretrained(f"facebook/musicgen-{model_size}")

    def generate(
        self,
        prompt: str,
        duration: float = 30.0,
        is_loop: bool = True,
    ) -> Optional[GeneratedAudio]:
        """
        Generate music from prompt.

        Args:
            prompt: Music generation prompt
            duration: Duration in seconds
            is_loop: Whether to generate loopable music

        Returns:
            GeneratedAudio object or None
        """
        # Placeholder implementation
        # In production:
        # self.model.set_generation_params(duration=duration)
        # if is_loop:
        #     # Apply LoopGen modifications
        #     audio = self.model.generate_with_loop(prompt)
        # else:
        #     audio = self.model.generate([prompt])
        #
        # # Save to file
        # output_path = Path(f"generated_bgm_{hash(prompt)}.wav")
        # torchaudio.save(str(output_path), audio, sample_rate=32000)

        logger.info(f"Generating {duration}s music: {prompt[:50]}...")

        # Return placeholder
        return GeneratedAudio(
            file_path=Path("placeholder_bgm.wav"),
            duration=duration,
            audio_type="bgm",
            prompt=AudioPrompt(
                scene_type="unknown",
                emotions=[],
                intensity=0.5,
            ),
            is_loop=is_loop,
        )


class AudioGenWrapper:
    """
    Wrapper for AudioGen SFX generation.

    Note: This is a placeholder implementation.
    """

    def __init__(self, device: str = "cuda"):
        """
        Initialize AudioGen wrapper.

        Args:
            device: Device to use
        """
        self.device = device
        self.model = None
        # In production, load model here

    def generate(
        self,
        prompt: str,
        duration: float = 5.0,
    ) -> Optional[GeneratedAudio]:
        """
        Generate SFX from prompt.

        Args:
            prompt: SFX generation prompt
            duration: Duration in seconds

        Returns:
            GeneratedAudio object or None
        """
        logger.info(f"Generating {duration}s SFX: {prompt[:50]}...")

        # Placeholder
        return GeneratedAudio(
            file_path=Path("placeholder_sfx.wav"),
            duration=duration,
            audio_type="sfx",
            prompt=AudioPrompt(
                scene_type="unknown",
                emotions=[],
                intensity=0.5,
            ),
            is_loop=False,
        )


def generate_bgm_for_panel(
    panel_data: Dict,
    music_gen: MusicGenWrapper,
    output_dir: Path,
) -> Optional[GeneratedAudio]:
    """
    Generate BGM for a panel based on scene context.

    Args:
        panel_data: Panel entry with scene_context
        music_gen: MusicGen wrapper instance
        output_dir: Output directory for audio files

    Returns:
        GeneratedAudio object or None
    """
    scene_context = panel_data.get("scene_context", {})
    timeline = panel_data.get("timeline", {})
    duration = timeline.get("duration", 30.0)

    # Build prompt
    prompt = build_music_prompt(scene_context)

    if not prompt:
        return None

    # Generate music
    audio = music_gen.generate(
        prompt=prompt,
        duration=duration,
        is_loop=True,  # BGM should loop
    )

    if audio:
        # Save to output directory
        panel_id = panel_data.get("panel", {}).get("panel_id", 0)
        output_path = output_dir / f"bgm_panel_{panel_id}.wav"
        audio.file_path = output_path

    return audio


def generate_sfx_for_panel(
    panel_data: Dict,
    audio_gen: AudioGenWrapper,
    output_dir: Path,
) -> List[GeneratedAudio]:
    """
    Generate SFX for onomatopoeia in a panel.

    Args:
        panel_data: Panel entry
        audio_gen: AudioGen wrapper instance
        output_dir: Output directory for audio files

    Returns:
        List of GeneratedAudio objects
    """
    onomatopoeia_list = panel_data.get("onomatopoeia", [])
    generated_sfx: List[GeneratedAudio] = []

    for idx, onomatopoeia in enumerate(onomatopoeia_list):
        prompt = build_sfx_prompt(onomatopoeia)

        if not prompt:
            continue

        # Generate SFX
        audio = audio_gen.generate(
            prompt=prompt,
            duration=5.0,  # Typical SFX duration
        )

        if audio:
            panel_id = panel_data.get("panel", {}).get("panel_id", 0)
            output_path = output_dir / f"sfx_panel_{panel_id}_{idx}.wav"
            audio.file_path = output_path
            generated_sfx.append(audio)

    return generated_sfx


def generate_audio_for_chapter(
    chapter_entries: List[Dict],
    output_dir: Path,
    music_gen: Optional[MusicGenWrapper] = None,
    audio_gen: Optional[AudioGenWrapper] = None,
) -> Dict:
    """
    Generate all audio (BGM + SFX) for a chapter.

    Args:
        chapter_entries: List of page entries
        output_dir: Output directory
        music_gen: MusicGen wrapper (optional)
        audio_gen: AudioGen wrapper (optional)

    Returns:
        Dictionary mapping panel_id to audio files
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generators if not provided
    if music_gen is None:
        music_gen = MusicGenWrapper()
    if audio_gen is None:
        audio_gen = AudioGenWrapper()

    audio_map: Dict[int, Dict] = {}

    for page_entry in chapter_entries:
        panel_entries = page_entry.get("content", [])

        for panel_entry in panel_entries:
            panel_id = panel_entry.get("panel", {}).get("panel_id", 0)

            # Generate BGM
            bgm = generate_bgm_for_panel(panel_entry, music_gen, output_dir)

            # Generate SFX
            sfx_list = generate_sfx_for_panel(panel_entry, audio_gen, output_dir)

            # Store in map
            audio_map[panel_id] = {
                "bgm": bgm.file_path if bgm else None,
                "sfx": [sfx.file_path for sfx in sfx_list],
            }

            # Update panel entry
            panel_entry["audio"] = {
                "bgm_path": str(bgm.file_path) if bgm else None,
                "sfx_paths": [str(sfx.file_path) for sfx in sfx_list],
            }

    return audio_map
