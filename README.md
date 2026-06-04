# music-to-text

**Turn any audio file into structured metadata and ready-to-use music industry copy.**

`music-to-text` is an open-source, local-first Python framework that extracts acoustic features from audio and generates A&R notes, PR pitches, playlist descriptions, and sync licensing blurbs — with or without an LLM.

<p align="center">
  <img src="assets/music-to-text-pipeline.svg" alt="Music-to-text framework pipeline" width="100%">
</p>

## Quick Start

```bash
git clone https://github.com/edujbarrios/music-to-text.git
cd music-to-text
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .
```

Run without an API key:

```bash
music-to-text your-track.mp3 --no-llm --pretty
```

Run with an OpenAI-compatible API:

```bash
music-to-text your-track.mp3 --mode pr
```

## CLI

```bash
music-to-text your-track.mp3 --mode json --pretty
music-to-text your-track.mp3 --mode sync --output pitch.json
music-to-text your-track.mp3 --format markdown --output report.md
music-to-text your-track.mp3 --format csv --output track.csv
music-to-text music-folder/ --list-files
music-to-text music-folder/ --recursive --output catalog.json
music-to-text music-folder/ --recursive --limit 10 --no-llm
music-to-text your-track.mp3 --llm-fallback --pretty
music-to-text --version
```

URL sources (YouTube, SoundCloud) are supported via `yt-dlp`. Only use URLs for media you have the right to access and process, and comply with the terms of the source platform.

```bash
music-to-text "https://soundcloud.com/artist/track" --mode playlist
```

**Options:** `--mode summary|ar|pr|playlist|sync|json` · `--format text|json|markdown|csv` · `--no-llm` · `--llm-fallback` · `--output` · `--pretty` · `--model` · `--base-url` · `--api-key` · `--download-dir` · `--cookies` · `--cookies-from-browser` · `--recursive` · `--limit` · `--list-files`

Local directory scans include common catalog formats: `.aac`, `.aif`, `.aiff`, `.flac`, `.m4a`, `.mp3`, `.ogg`, `.opus`, `.wav`, and `.wma`.

Markdown and CSV exports include both raw seconds and human-readable durations for easier review.

## Python API

```python
from music_to_text import MusicToText

analyzer = MusicToText()
result = analyzer.analyze("your-track.mp3", mode="summary")
print(result.generated_text.short_description)

# No API key needed
result = analyzer.analyze("your-track.mp3", mode="summary", no_llm=True)

# Batch
results = analyzer.analyze_many("music-folder/", mode="summary", no_llm=True, recursive=True)
sample = analyzer.analyze_many("music-folder/", mode="summary", no_llm=True, limit=10)
```

## LLM Setup

Set environment variables or pass flags directly:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

Any OpenAI-compatible endpoint works, including local/self-hosted ones.

```bash
music-to-text track.mp3 --base-url http://localhost:8000/v1 --model local-model --api-key local-key
```

## What Gets Extracted

**Acoustic features:** duration · tempo (BPM) · loudness · spectral centroid · chroma · key estimate · onset strength · energy profile · section changes

**Generated outputs:** short description · A&R description · PR pitch · playlist pitch · sync licensing pitch · genre tags · mood tags · production tags · structured JSON · Markdown · CSV

## Example: Billie Jean — Michael Jackson

> [!NOTE]
> The generated text outputs (short description, A&R, PR pitch, playlist pitch, sync pitch) vary significantly depending on the internal prompt used. The same audio features fed to a differently worded system prompt will produce different copy. The example below reflects the default prompt in [`src/music_to_text/prompts.py`](src/music_to_text/prompts.py).

Analysis of a well-known pop track used to validate the pipeline. Full output in [`examples/billiejean_example.json`](examples/billiejean_example.json).

| Feature | Value |
|---|---|
| Duration | 295.8 s |
| Tempo | 117.45 BPM |
| Key estimate | F#/Gb major/minor |
| Loudness proxy | −14.65 dBFS |
| Spectral centroid | 3720.82 Hz |
| Energy | High |

**Tags:** mood `driving · upbeat · high-energy` · genre `pop · indie` · production `bright · crisp top end · forward loudness · dynamic mix`

**Short description:** A high-energy, upbeat pop track with a crisp, bright production and driving rhythm.

**A&R:** This track features a tempo of 117 BPM and a key estimate of F#/Gb major/minor, delivering a dynamic and engaging listening experience. The spectral centroid suggests a bright tonal quality, while the loudness proxy indicates a forward, punchy mix. The energy profile remains consistently high, peaking in the middle sections.

**Sync pitch:** Great for high-energy scenes — action sequences, sports highlights, or vibrant commercials. Its bright production and driving rhythm make it versatile for visual media needing an uplifting soundtrack.

## No-LLM Mode

```bash
music-to-text your-track.mp3 --no-llm --pretty
```

Returns extracted features and heuristic tags with no API calls. All tests run in this mode.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Citation

If you use this project in a publication, article, or research, you must credit the original author.

**APA**

```
Barrios, E. J. (2026). music-to-text: Local-first music analysis and text generation framework [Software]. GitHub. https://github.com/edujbarrios/music-to-text
```

**BibTeX**

```bibtex
@software{barrios2026musictotext,
  author    = {Barrios, Eduardo J.},
  title     = {music-to-text: Local-first music analysis and text generation framework},
  year      = {2026},
  url       = {https://github.com/edujbarrios/music-to-text},
  note      = {Apache License 2.0}
}
```
