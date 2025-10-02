# Contributing to TTS Service

Thank you for your interest in contributing to the TTS Service! We welcome contributions from the community to help improve this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guide](#style-guide)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as [GitHub issues](https://github.com/yourusername/tts-service/issues). When creating a bug report, please include the following:

1. A clear, descriptive title
2. A description of the problem
3. Steps to reproduce the issue
4. Expected behavior
5. Actual behavior
6. Environment information (OS, Python version, etc.)
7. Any relevant error messages or logs

### Suggesting Enhancements

Enhancement suggestions are also tracked as [GitHub issues](https://github.com/yourusername/tts-service/issues). When suggesting an enhancement, please include:

1. A clear, descriptive title
2. A description of the enhancement
3. Why this enhancement would be useful
4. Any alternative solutions you've considered

### Your First Code Contribution

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Run tests and ensure they pass
6. Commit your changes with a clear commit message
7. Push your changes to your fork
8. Open a pull request

### Pull Requests

When submitting a pull request, please:

1. Reference any related issues
2. Include tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass
5. Follow the style guide

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tts-service.git
   cd tts-service
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run the development server:
   ```bash
   ./run_dev.sh
   ```

## Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function signatures
- Keep functions small and focused
- Write docstrings for all public functions and classes
- Use Google-style docstrings
- Keep lines under 100 characters

## Testing

Run tests with:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=tts_service
```

## Documentation

- Keep docstrings up to date
- Update the README when adding new features
- Add examples for new functionality

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).
