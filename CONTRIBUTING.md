# Contributing

Thanks for helping build `music-to-text`.

## Development setup

```bash
git clone https://github.com/edujbarrios/music-to-text.git
cd music-to-text
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run tests:

```bash
python -m pytest
```

## Guidelines

- Keep tests runnable without API keys.
- Prefer typed, modular Python.
- Do not commit secrets, private audio, or generated large files.
- Keep LLM providers OpenAI-compatible and configurable.
- Explain user-facing behavior changes in pull requests.

