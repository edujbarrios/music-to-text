# music-to-text

Text-to-music models are reaching a peak. What about the reverse? Music-to-text helps songs explain themselves.

`music-to-text` is an open-source, local-first Python framework that converts audio into structured musical intelligence and useful text descriptions powered by LLMs.

```text
audio in -> musical analysis -> structured metadata -> LLM-generated descriptions
```

## Why music-to-text matters

Music catalogs, artists, labels, supervisors, and researchers need language that explains what a track is doing. Today, people still write most of that metadata manually: genre notes, mood tags, playlist pitches, A&R blurbs, and sync descriptions. This project makes that work more reproducible by combining deterministic audio analysis with optional OpenAI-compatible language models.

## Installation

This project is intended for local development from the cloned repository. It does not depend on a package existing on PyPI.

```bash
git clone https://github.com/edujbarrios/music-to-text.git
cd music-to-text
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## CLI

```bash
music-to-text examples/song.mp3 --no-llm
music-to-text examples/song.mp3 --mode pr
music-to-text examples/song.mp3 --mode json --pretty
music-to-text examples/song.mp3 --mode sync --output sync-pitch.json
music-to-text "https://www.youtube.com/watch?v=VIDEO_ID" --no-llm
music-to-text "https://soundcloud.com/artist/track" --mode playlist
```

Options:

- `--mode summary|ar|pr|playlist|sync|json`
- `--model`
- `--base-url`
- `--api-key`
- `--no-llm`
- `--output`
- `--pretty`
- `--download-dir`

## YouTube and SoundCloud inputs

Local files are still the default workflow, but the CLI and Python API also accept YouTube and SoundCloud links. URL inputs are downloaded locally with `yt-dlp` before analysis.

```bash
music-to-text "https://youtu.be/VIDEO_ID" --no-llm --pretty
music-to-text "https://soundcloud.com/artist/track" --mode pr
music-to-text "https://www.youtube.com/watch?v=VIDEO_ID" --download-dir downloads --mode json
```

By default, downloaded URL audio is stored in a temporary folder and removed after analysis. Use `--download-dir` to keep the downloaded file. Only analyze media you have the right to access and process, and follow the terms of the source platform.

## Python API

```python
from music_to_text import MusicToText

analyzer = MusicToText()
result = analyzer.analyze("song.mp3", mode="summary")
print(result.generated_text.short_description)
```

URLs work the same way:

```python
result = analyzer.analyze("https://soundcloud.com/artist/track", mode="playlist", no_llm=True)
```

For local deterministic output without an API key:

```python
result = analyzer.analyze("song.mp3", mode="summary", no_llm=True)
```

## OpenAI-compatible API setup

Create an environment file:

```bash
cp .env.example .env
```

Example `.env`:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.llm7.io/v1
LLM_MODEL=gpt-4o-mini
```

`llm7.io` is only an example of an OpenAI-compatible API provider. Any OpenAI-compatible API should work, including local or self-hosted endpoints, as long as it exposes a compatible `/chat/completions` API.

You can also pass settings per command:

```bash
music-to-text song.mp3 --base-url http://localhost:8000/v1 --model local-model --api-key local-key
```

## Audio analysis

When the local environment supports decoding them, MP3, WAV, FLAC, and M4A files can be analyzed. The framework extracts:

- duration
- estimated tempo
- loudness proxy
- spectral centroid
- chroma features
- approximate key estimate
- onset strength
- rough energy profile
- approximate section changes
- heuristic mood tags
- heuristic genre hints
- production descriptors

## Outputs

The result contains:

- short description
- detailed A&R-style description
- PR pitch
- playlist pitch
- sync licensing pitch
- genre tags
- mood tags
- instrument and production tags
- structured JSON metadata

Example JSON shape:

```json
{
  "source_path": "examples/song.mp3",
  "mode": "summary",
  "features": {
    "duration_seconds": 184.2,
    "tempo_bpm": 122.0,
    "key_estimate": "A major/minor estimate"
  },
  "heuristic_tags": {
    "mood_tags": ["driving", "upbeat"],
    "genre_hints": ["pop", "indie"]
  },
  "generated_text": {
    "short_description": "This track is an approximately 184.2s piece around 122 BPM..."
  },
  "llm_used": false
}
```

## No-LLM mode

Use `--no-llm` to return extracted features, heuristic tags, and deterministic local text without API calls:

```bash
music-to-text examples/song.mp3 --no-llm --pretty
```

Tests run without API keys.

## Roadmap

- Whisper transcription support
- CLAP, MERT, and MuLan embeddings
- similarity search
- batch folder analysis
- dataset export
- web UI
- plugin system for LLM providers
- evaluation benchmarks for music captioning

## Contributing

Contributions are welcome from the beginning. See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md).

## License

MIT License. See [LICENSE](LICENSE).

