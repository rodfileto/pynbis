
# Contributing to PyNBIS

Thank you for your interest in contributing to PyNBIS! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/pynbis.git`
3. Create a new branch: `git checkout -b feature-name`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to your fork: `git push origin feature-name`
8. Create a Pull Request

## Development Setup

### Prerequisites
- Python 3.10 or higher
- C compiler (GCC, Clang, or MSVC)
- Git

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/pynbis.git
cd pynbis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,imaging]"

# Run tests
pytest tests/
```

## Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting: `black pynbis/`
- Use type hints for all functions
- Write docstrings for all public APIs
- Keep line length to 100 characters

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Test on multiple Python versions if possible

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pynbis --cov-report=html
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update CHANGELOG.md
- Add examples for new features

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass
5. Update CHANGELOG.md
6. Submit PR with clear description of changes

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- PyNBIS version
- Minimal code to reproduce the issue
- Error messages and stack traces
- Expected vs actual behavior

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## License

By contributing to PyNBIS, you agree that your contributions will be released to the public domain, consistent with the NBIS license and the existing project license.

## Questions?

Feel free to open an issue for questions or discussions about contributing.
