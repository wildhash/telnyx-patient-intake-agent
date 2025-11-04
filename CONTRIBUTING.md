# Contributing to Telnyx Patient Intake Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/wildhash/telnyx-patient-intake-agent/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing [Issues](https://github.com/wildhash/telnyx-patient-intake-agent/issues) for similar suggestions
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach (optional)

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages (`git commit -m 'Add feature: X'`)
6. Push to your fork (`git push origin feature/your-feature-name`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Write comments for complex logic

### Testing

- Test all new features and bug fixes
- Ensure existing tests still pass
- Add new tests for new functionality
- Test with different configurations

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/telnyx-patient-intake-agent.git
cd telnyx-patient-intake-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run tests
python -m pytest  # if tests are added

# Start development server
python app.py
```

## Project Structure

- `app.py` - Main Flask application
- `models.py` - Database models
- `config.py` - Configuration management
- `routes/` - API and webhook routes
- `services/` - Business logic
- `templates/` - HTML templates
- `cli.py` - Command-line interface

## Areas for Contribution

### High Priority
- Additional test coverage
- Performance optimizations
- Documentation improvements
- Bug fixes

### Feature Ideas
- Additional storage integrations
- More intake question templates
- Advanced analytics dashboard
- Multi-language support
- Voice recognition improvements
- Automated testing framework

### Healthcare Integrations
- FHIR API support
- EHR integrations
- HL7 message support
- SMART on FHIR apps

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Focus on the best solution for the project

## Questions?

Feel free to open an issue for any questions about contributing!
