"""
TTS (Text-to-Speech) Engine Module.

This module handles:
- TTS generation using Style-Bert-VITS2
- Voice profile management
- Emotion-aware prosody control
- Character voice consistency
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VoiceProfile:
    """Represents a voice profile for a character."""

    character_id: int
    voice_seed: int  # Seed for voice generation
    voice_name: Optional[str] = None
    gender: Optional[str] = None  # 'male', 'female', 'neutral'
    age_range: Optional[str] = None  # 'child', 'teen', 'adult', 'elderly'
    pitch: float = 0.0  # Pitch adjustment (-1.0 to 1.0)
    speed: float = 1.0  # Speech speed multiplier
    emotion_style: Optional[str] = None  # Default emotion style


@dataclass
class TTSRequest:
    """Represents a TTS generation request."""

    text: str
    character_id: int
    emotion: Optional[str] = None
    language: str = "ja"
    speed: Optional[float] = None
    pitch: Optional[float] = None


@dataclass
class GeneratedSpeech:
    """Represents generated speech audio."""

    file_path: Path
    duration: float
    character_id: int
    text: str


class StyleBertVITS2Wrapper:
    """
    Wrapper for Style-Bert-VITS2 TTS model.

    Note: This is a placeholder implementation.
    In production, this would interface with the actual model.
    """

    def __init__(self, model_path: Optional[Path] = None, device: str = "cuda"):
        """
        Initialize Style-Bert-VITS2 wrapper.

        Args:
            model_path: Path to model files
            device: Device to use ('cpu' or 'cuda')
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        # In production:
        # from style_bert_vits2 import get_models, get_tokenizer
        # self.model = load_model(model_path)

    def generate(
        self,
        text: str,
        voice_profile: VoiceProfile,
        emotion: Optional[str] = None,
        language: str = "ja",
    ) -> Optional[GeneratedSpeech]:
        """
        Generate speech from text using voice profile.

        Args:
            text: Text to synthesize
            voice_profile: Voice profile for character
            emotion: Emotion style (optional)
            language: Language code

        Returns:
            GeneratedSpeech object or None
        """
        # Placeholder implementation
        # In production, emotion and language will be used:
        # audio = self.model.infer(
        #     text=text,
        #     sdp_ratio=0.2,
        #     noise_scale=0.6,
        #     noise_scale_w=0.8,
        #     length_scale=voice_profile.speed,
        #     seed=voice_profile.voice_seed,
        #     emotion=emotion or voice_profile.emotion_style,
        #     language=language,
        # )

        logger.info(
            "Generating speech for character %s: %s...",
            voice_profile.character_id,
            text[:30],
        )

        # Suppress unused argument warnings - used in production
        _ = emotion
        _ = language

        # Estimate duration (rough)
        duration = len(text) * 0.1  # Rough estimate: 0.1s per character

        return GeneratedSpeech(
            file_path=Path("placeholder_speech.wav"),
            duration=duration,
            character_id=voice_profile.character_id,
            text=text,
        )


class VoiceProfileManager:
    """
    Manages voice profiles for characters.

    Maintains consistency across chapters by assigning
    the same voice seed to the same character.
    """

    def __init__(self, profiles_file: Optional[Path] = None):
        """
        Initialize voice profile manager.

        Args:
            profiles_file: Path to JSON file storing profiles
        """
        self.profiles_file = profiles_file or Path("voice_profiles.json")
        self.profiles: Dict[int, VoiceProfile] = {}
        self.next_seed = 1000  # Starting seed

        # Load existing profiles
        self.load_profiles()

    def load_profiles(self) -> None:
        """Load voice profiles from file."""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for char_id, profile_data in data.items():
                        self.profiles[int(char_id)] = VoiceProfile(**profile_data)
            except Exception as e:
                logger.warning("Error loading voice profiles: %s", e, exc_info=True)

    def save_profiles(self) -> None:
        """Save voice profiles to file."""
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            str(char_id): {
                "character_id": profile.character_id,
                "voice_seed": profile.voice_seed,
                "voice_name": profile.voice_name,
                "gender": profile.gender,
                "age_range": profile.age_range,
                "pitch": profile.pitch,
                "speed": profile.speed,
                "emotion_style": profile.emotion_style,
            }
            for char_id, profile in self.profiles.items()
        }

        with open(self.profiles_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_or_create_profile(
        self,
        character_id: int,
        character_name: Optional[str] = None,
        gender: Optional[str] = None,
        age_range: Optional[str] = None,
    ) -> VoiceProfile:
        """
        Get existing profile or create new one.

        Args:
            character_id: Global character ID
            character_name: Character name (optional)
            gender: Character gender (optional)
            age_range: Character age range (optional)

        Returns:
            VoiceProfile object
        """
        if character_id in self.profiles:
            return self.profiles[character_id]

        # Create new profile
        profile = VoiceProfile(
            character_id=character_id,
            voice_seed=self.next_seed,
            voice_name=character_name,
            gender=gender,
            age_range=age_range,
        )

        # Adjust default settings based on gender/age
        if gender == "male":
            profile.pitch = -0.2
        elif gender == "female":
            profile.pitch = 0.2

        if age_range == "child":
            profile.pitch = 0.3
            profile.speed = 1.1
        elif age_range == "elderly":
            profile.pitch = -0.1
            profile.speed = 0.9

        self.profiles[character_id] = profile
        self.next_seed += 1

        # Save profiles
        self.save_profiles()

        return profile

    def update_profile(
        self,
        character_id: int,
        **kwargs,
    ) -> None:
        """
        Update voice profile.

        Args:
            character_id: Character ID
            **kwargs: Profile attributes to update
        """
        if character_id not in self.profiles:
            return

        profile = self.profiles[character_id]
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        self.save_profiles()


def adjust_prosody_for_emotion(
    base_speed: float,
    base_pitch: float,
    emotion: str,
) -> Tuple[float, float]:
    """
    Adjust prosody (speed, pitch) based on emotion.

    Args:
        base_speed: Base speech speed
        base_pitch: Base pitch
        emotion: Emotion tag

    Returns:
        Tuple of (adjusted_speed, adjusted_pitch)
    """
    speed = base_speed
    pitch = base_pitch

    emotion_adjustments = {
        "anger": {"speed": 1.2, "pitch": 0.1},
        "joy": {"speed": 1.1, "pitch": 0.2},
        "sadness": {"speed": 0.8, "pitch": -0.2},
        "fear": {"speed": 1.15, "pitch": 0.15},
        "excitement": {"speed": 1.2, "pitch": 0.15},
        "nervous": {"speed": 1.1, "pitch": 0.1},
        "calm": {"speed": 0.9, "pitch": -0.1},
    }

    if emotion in emotion_adjustments:
        adj = emotion_adjustments[emotion]
        speed *= adj["speed"]
        pitch += adj["pitch"]

    return speed, pitch


def generate_speech_for_bubble(
    bubble_data: Dict,
    voice_manager: VoiceProfileManager,
    tts_engine: StyleBertVITS2Wrapper,
    output_dir: Path,
) -> Optional[GeneratedSpeech]:
    """
    Generate speech for a speech bubble.

    Args:
        bubble_data: Speech bubble data
        voice_manager: Voice profile manager
        tts_engine: TTS engine
        output_dir: Output directory

    Returns:
        GeneratedSpeech object or None
    """
    text = bubble_data.get("text", "")
    speaker = bubble_data.get("speaker", {})
    character_id = speaker.get("character_id")

    if not text or character_id is None:
        return None

    # Get voice profile
    character_name = speaker.get("character_name")
    voice_profile = voice_manager.get_or_create_profile(
        character_id=character_id,
        character_name=character_name,
    )

    # Get emotion from panel context (if available)
    # This would come from panel_data in full implementation
    emotion = None  # Would extract from panel context

    # Adjust prosody for emotion
    # These will be used in production when full TTS integration is complete
    _speed, _pitch = adjust_prosody_for_emotion(
        voice_profile.speed,
        voice_profile.pitch,
        emotion or "neutral",
    )

    # Generate speech
    speech = tts_engine.generate(
        text=text,
        voice_profile=voice_profile,
        emotion=emotion,
        language=bubble_data.get("lang", "ja"),
    )

    if speech:
        # Save to output directory
        bubble_id = bubble_data.get("bubble", {}).get("bubble_id", 0)
        output_path = output_dir / f"speech_bubble_{bubble_id}.wav"
        speech.file_path = output_path

    return speech


def generate_speech_for_panel(
    panel_data: Dict,
    voice_manager: VoiceProfileManager,
    tts_engine: StyleBertVITS2Wrapper,
    output_dir: Path,
) -> List[GeneratedSpeech]:
    """
    Generate speech for all bubbles in a panel.

    Args:
        panel_data: Panel entry
        voice_manager: Voice profile manager
        tts_engine: TTS engine
        output_dir: Output directory

    Returns:
        List of GeneratedSpeech objects
    """
    bubbles = panel_data.get("content", [])
    generated_speech: List[GeneratedSpeech] = []

    # Get panel emotions for context
    scene_context = panel_data.get("scene_context", {})
    panel_emotions = scene_context.get("emotion_tags", [])
    primary_emotion = panel_emotions[0] if panel_emotions else None

    for bubble in bubbles:
        if bubble.get("is_dialogue", False):
            # Add emotion context to bubble
            bubble_with_emotion = bubble.copy()
            if primary_emotion:
                bubble_with_emotion["emotion"] = primary_emotion

            speech = generate_speech_for_bubble(
                bubble_with_emotion,
                voice_manager,
                tts_engine,
                output_dir,
            )

            if speech:
                generated_speech.append(speech)

                # Update bubble with speech path
                bubble["speech_path"] = str(speech.file_path)

    return generated_speech


def generate_speech_for_chapter(
    chapter_entries: List[Dict],
    output_dir: Path,
    voice_manager: Optional[VoiceProfileManager] = None,
    tts_engine: Optional[StyleBertVITS2Wrapper] = None,
) -> Dict:
    """
    Generate speech for entire chapter.

    Args:
        chapter_entries: List of page entries
        output_dir: Output directory
        voice_manager: Voice profile manager (optional)
        tts_engine: TTS engine (optional)

    Returns:
        Dictionary mapping bubble_id to speech file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize if not provided
    if voice_manager is None:
        voice_manager = VoiceProfileManager()
    if tts_engine is None:
        tts_engine = StyleBertVITS2Wrapper()

    speech_map: Dict[int, Path] = {}

    for page_entry in chapter_entries:
        panel_entries = page_entry.get("content", [])

        for panel_entry in panel_entries:
            speech_list = generate_speech_for_panel(
                panel_entry,
                voice_manager,
                tts_engine,
                output_dir,
            )

            for speech in speech_list:
                bubble_id = speech.character_id  # Simplified
                speech_map[bubble_id] = speech.file_path

    return speech_map
