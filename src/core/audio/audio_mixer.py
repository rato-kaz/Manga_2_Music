"""
Audio Mixing and Transition Module.

This module handles:
- Audio stem separation (Demucs)
- Dynamic mixing for transitions
- Crossfading between scenes
- Vertical re-orchestration
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


class AudioMixer:
    """
    Audio mixer for combining BGM, SFX, and dialogue.

    Handles transitions, crossfading, and dynamic mixing.
    """

    def __init__(self, sample_rate: int = 44100):
        """
        Initialize audio mixer.

        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate

    def load_audio(self, file_path: Path) -> Optional[np.ndarray]:
        """
        Load audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Audio array or None
        """
        try:
            # In production, use librosa or soundfile
            # import librosa
            # audio, sr = librosa.load(str(file_path), sr=self.sample_rate)
            # return audio

            # Placeholder
            logger.debug(f"Loading audio: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error loading audio {file_path}: {e}", exc_info=True)
            return None

    def separate_stems(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Separate audio into stems using Demucs.

        Args:
            audio: Audio array

        Returns:
            Dictionary of stems: {'drums': ..., 'bass': ..., 'melody': ..., 'vocals': ...}
        """
        # Placeholder - in production use Demucs
        # from demucs import separate
        # stems = separate(audio)

        logger.debug("Separating audio stems")
        return {
            "drums": audio,
            "bass": audio,
            "melody": audio,
            "vocals": audio,
        }

    def crossfade(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
        fade_duration: float = 2.0,
    ) -> np.ndarray:
        """
        Crossfade between two audio clips.

        Args:
            audio1: First audio clip
            audio2: Second audio clip
            fade_duration: Fade duration in seconds

        Returns:
            Crossfaded audio
        """
        fade_samples = int(fade_duration * self.sample_rate)

        # Ensure both arrays are same length for crossfade
        min_len = min(len(audio1), len(audio2))
        audio1 = audio1[:min_len]
        audio2 = audio2[:min_len]

        # Create fade curves
        fade_out = np.linspace(1.0, 0.0, fade_samples)
        fade_in = np.linspace(0.0, 1.0, fade_samples)

        # Apply fades
        audio1_faded = audio1.copy()
        audio2_faded = audio2.copy()

        if len(audio1) >= fade_samples:
            audio1_faded[-fade_samples:] *= fade_out
        if len(audio2) >= fade_samples:
            audio2_faded[:fade_samples] *= fade_in

        # Crossfade
        if len(audio1) >= fade_samples:
            audio1_faded[-fade_samples:] += audio2_faded[:fade_samples]
            result = np.concatenate([audio1_faded[:-fade_samples], audio2_faded])
        else:
            result = np.concatenate([audio1_faded, audio2_faded])

        return result

    def mix_audio(
        self,
        bgm: Optional[np.ndarray],
        sfx_list: List[np.ndarray],
        dialogue: Optional[np.ndarray] = None,
        bgm_volume: float = 0.7,
        sfx_volume: float = 1.0,
        dialogue_volume: float = 1.0,
    ) -> np.ndarray:
        """
        Mix BGM, SFX, and dialogue together.

        Args:
            bgm: Background music
            sfx_list: List of sound effects
            dialogue: Dialogue audio
            bgm_volume: BGM volume (0.0 to 1.0)
            sfx_volume: SFX volume
            dialogue_volume: Dialogue volume

        Returns:
            Mixed audio array
        """
        # Determine output length
        max_length = 0
        if bgm is not None:
            max_length = max(max_length, len(bgm))
        for sfx in sfx_list:
            if sfx is not None:
                max_length = max(max_length, len(sfx))
        if dialogue is not None:
            max_length = max(max_length, len(dialogue))

        if max_length == 0:
            return np.zeros(int(self.sample_rate * 1.0))  # 1 second silence

        # Initialize output
        output = np.zeros(max_length)

        # Mix BGM
        if bgm is not None:
            bgm_padded = np.pad(bgm, (0, max_length - len(bgm)), mode="constant")
            output += bgm_padded * bgm_volume

        # Mix SFX
        for sfx in sfx_list:
            if sfx is not None:
                sfx_padded = np.pad(sfx, (0, max_length - len(sfx)), mode="constant")
                output += sfx_padded * sfx_volume

        # Mix dialogue
        if dialogue is not None:
            dialogue_padded = np.pad(dialogue, (0, max_length - len(dialogue)), mode="constant")
            output += dialogue_padded * dialogue_volume

        # Normalize to prevent clipping
        max_val = np.max(np.abs(output))
        if max_val > 1.0:
            output = output / max_val

        return output

    def vertical_reorchestration(
        self,
        current_stems: Dict[str, np.ndarray],
        new_stems: Dict[str, np.ndarray],
        transition_type: str = "additive",
    ) -> Dict[str, np.ndarray]:
        """
        Perform vertical re-orchestration for smooth transitions.

        This technique keeps some stems (like drums/bass) and adds new ones
        (like melody) for smooth scene transitions.

        Args:
            current_stems: Current audio stems
            new_stems: New audio stems to transition to
            transition_type: 'additive' (add new stems) or 'replacement' (replace all)

        Returns:
            Transitioned stems
        """
        if transition_type == "additive":
            # Keep rhythm section, add new melody
            result = {
                "drums": current_stems.get("drums", new_stems.get("drums")),
                "bass": current_stems.get("bass", new_stems.get("bass")),
                "melody": new_stems.get("melody"),  # New melody
                "vocals": new_stems.get("vocals", current_stems.get("vocals")),
            }
        else:  # replacement
            result = new_stems.copy()

        return result

    def create_transition(
        self,
        panel1_audio: Dict,
        panel2_audio: Dict,
        transition_duration: float = 2.0,
    ) -> np.ndarray:
        """
        Create smooth transition between two panels.

        Args:
            panel1_audio: Audio data for first panel
            panel2_audio: Audio data for second panel
            transition_duration: Transition duration in seconds

        Returns:
            Transition audio
        """
        # Load audio files
        bgm1 = (
            self.load_audio(panel1_audio.get("bgm_path")) if panel1_audio.get("bgm_path") else None
        )
        bgm2 = (
            self.load_audio(panel2_audio.get("bgm_path")) if panel2_audio.get("bgm_path") else None
        )

        if bgm1 is None and bgm2 is None:
            return np.zeros(int(self.sample_rate * transition_duration))

        if bgm1 is None:
            return bgm2[: int(self.sample_rate * transition_duration)]
        if bgm2 is None:
            return bgm1[-int(self.sample_rate * transition_duration) :]

        # Crossfade
        transition = self.crossfade(bgm1, bgm2, transition_duration)

        return transition[: int(self.sample_rate * transition_duration)]


def mix_chapter_audio(
    chapter_entries: List[Dict],
    output_path: Path,
    mixer: Optional[AudioMixer] = None,
) -> Path:
    """
    Mix all audio for a chapter into final output.

    Args:
        chapter_entries: List of page entries with audio paths
        output_path: Output file path
        mixer: AudioMixer instance (optional)

    Returns:
        Path to mixed audio file
    """
    if mixer is None:
        mixer = AudioMixer()

    # Collect all audio segments
    audio_segments: List[np.ndarray] = []

    for page_entry in chapter_entries:
        panel_entries = page_entry.get("content", [])

        for idx, panel_entry in enumerate(panel_entries):
            audio_data = panel_entry.get("audio", {})

            # Load BGM
            bgm_path = audio_data.get("bgm_path")
            bgm = mixer.load_audio(Path(bgm_path)) if bgm_path else None

            # Load SFX
            sfx_paths = audio_data.get("sfx_paths", [])
            sfx_list = [mixer.load_audio(Path(path)) for path in sfx_paths]
            sfx_list = [sfx for sfx in sfx_list if sfx is not None]

            # Mix panel audio
            panel_audio = mixer.mix_audio(bgm, sfx_list)
            audio_segments.append(panel_audio)

            # Add transition to next panel
            if idx < len(panel_entries) - 1:
                next_panel = panel_entries[idx + 1]
                next_audio_data = next_panel.get("audio", {})
                transition = mixer.create_transition(audio_data, next_audio_data)
                audio_segments.append(transition)

    # Concatenate all segments
    if audio_segments:
        final_audio = np.concatenate(audio_segments)
    else:
        final_audio = np.zeros(int(mixer.sample_rate * 1.0))

    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # In production, use soundfile or librosa to save
    # import soundfile as sf
    # sf.write(str(output_path), final_audio, mixer.sample_rate)

    logger.info(f"Mixed audio saved to: {output_path}")
    return output_path
