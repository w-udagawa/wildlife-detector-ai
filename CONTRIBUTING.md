# Contributing to Wildlife Detector AI

Thank you for your interest in contributing to Wildlife Detector AI! This document provides guidelines for contributing to the project.

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/w-udagawa/wildlife-detector-ai/issues)
- Create a new issue with a clear title and description
- Include steps to reproduce the bug
- Specify your environment (OS, Python version, etc.)

### Suggesting Features

- Check existing feature requests in [Issues](https://github.com/w-udagawa/wildlife-detector-ai/issues)
- Create a new issue with the `enhancement` label
- Describe the feature and its use case

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/w-udagawa/wildlife-detector-ai.git
cd wildlife-detector-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Coding Standards

- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Write tests for new features
- Keep commits atomic and well-described

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

## Questions?

Feel free to open an issue for any questions about contributing!
