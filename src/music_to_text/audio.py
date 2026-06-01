"""Audio loading and musical feature extraction."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from music_to_text.schemas import AudioFeatures

KEY_NAMES = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]


def analyze_audio(path: str | Path) -> AudioFeatures:
    """Extract deterministic musical features from an audio file."""

    audio_path = Path(path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        import librosa
    except ImportError as exc:
        raise RuntimeError("librosa is required for audio analysis. Install with `pip install -e .`.") from exc

    y, sample_rate = librosa.load(str(audio_path), sr=None, mono=True)
    if y.size == 0:
        raise ValueError(f"Audio file contains no samples: {audio_path}")

    duration = float(librosa.get_duration(y=y, sr=sample_rate))
    tempo_raw, _ = librosa.beat.beat_track(y=y, sr=sample_rate)
    tempo = float(np.asarray(tempo_raw).mean())
    rms = librosa.feature.rms(y=y)[0]
    loudness_proxy = float(20 * np.log10(float(np.mean(rms)) + 1e-9))
    centroid = librosa.feature.spectral_centroid(y=y, sr=sample_rate)[0]
    chroma = librosa.feature.chroma_stft(y=y, sr=sample_rate)
    onset_env = librosa.onset.onset_strength(y=y, sr=sample_rate)
    energy_profile = _energy_profile(rms)
    section_changes = _section_changes_seconds(rms, duration)

    return AudioFeatures(
        path=str(audio_path),
        duration_seconds=round(duration, 3),
        sample_rate=int(sample_rate),
        tempo_bpm=round(tempo, 2),
        loudness_proxy_db=round(loudness_proxy, 2),
        spectral_centroid_mean=round(float(np.mean(centroid)), 2),
        chroma_mean=[round(float(value), 4) for value in np.mean(chroma, axis=1)],
        key_estimate=_estimate_key(chroma),
        onset_strength_mean=round(float(np.mean(onset_env)), 4),
        energy_profile=energy_profile,
        section_changes_seconds=section_changes,
    )


def _estimate_key(chroma: np.ndarray) -> str:
    pitch_class = int(np.argmax(np.mean(chroma, axis=1)))
    return f"{KEY_NAMES[pitch_class]} major/minor estimate"


def _energy_profile(rms: np.ndarray, bins: int = 8) -> list[float]:
    if rms.size == 0:
        return []
    chunks = np.array_split(rms, min(bins, rms.size))
    values = [float(np.mean(chunk)) for chunk in chunks]
    peak = max(values) or 1.0
    return [round(value / peak, 3) for value in values]


def _section_changes_seconds(rms: np.ndarray, duration: float) -> list[float]:
    if rms.size < 8 or duration <= 0:
        return []
    profile = np.array(_energy_profile(rms, bins=16))
    diffs = np.abs(np.diff(profile))
    threshold = float(np.mean(diffs) + np.std(diffs))
    changes: list[float] = []
    for index, diff in enumerate(diffs, start=1):
        if diff >= threshold and diff > 0.08:
            changes.append(round(duration * index / len(profile), 2))
    return changes[:8]

