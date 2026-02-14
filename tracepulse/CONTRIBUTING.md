# Contributing to Tracepulse

Thank you for your interest in contributing!

## Development Setup

1. Clone the repo:
```bash
git clone https://github.com/ax5hay/TracePulse.git
cd TracePulse/tracepulse
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

3. Install in editable mode with dev dependencies:
```bash
pip install -e ".[dev]"
pip install pytest
```

4. Run tests:
```bash
pytest tests/
```

## Submitting Changes

1. Create a branch for your feature/fix:
```bash
git checkout -b fix/something
```

2. Make your changes and commit with clear messages:
```bash
git add .
git commit -m "Brief description of changes"
```

3. Push and open a PR on GitHub.

## Code Style

- Follow PEP 8
- Use type hints where practical
- Add docstrings to public functions
- Keep functions small and focused

## Testing

- Add tests for new features in `tests/`
- Ensure all tests pass before submitting a PR
- Aim for >80% code coverage for critical paths

## Questions?

Open an issue or discussion on GitHub.
