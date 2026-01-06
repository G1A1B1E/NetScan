# Contributing to NetScan

Thank you for your interest in contributing to NetScan! This document provides guidelines and information about contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/netscan.git`
3. Create a feature branch: `git checkout -b feature/your-feature`

## Development Setup

```bash
cd netscan
./install.sh --check  # Verify dependencies
./install.sh --local  # Install locally for testing
```

## Code Style

### Bash
- Use 4-space indentation
- Quote variables: `"$variable"` not `$variable`
- Use `[[ ]]` for conditionals
- Add comments for complex logic
- Follow existing naming conventions (snake_case for functions)

### Python
- Follow PEP 8
- Use type hints where appropriate
- Document functions with docstrings

## Project Structure

```
lib/           # Bash modules - core functionality
helpers/       # Python acceleration scripts
example/       # Sample input files for testing
docs/          # Additional documentation
```

## Adding Features

### Adding a New Parser
1. Add parse function to `lib/parsers.sh`
2. Update `detect_file_format()` in same file
3. Add Python equivalent to `helpers/fast_parser.py`
4. Add example file to `example/`
5. Update README.md

### Adding a New Menu Option
1. Add option to `show_menu()` in `lib/ui.sh`
2. Add case handler in main loop in `netscan`
3. Implement function in appropriate `lib/*.sh` file

## Testing

Before submitting:
```bash
# Test with example files
./netscan example/arp.txt
./netscan example/scan.xml

# Check all menu options work
./netscan  # Run through menu manually

# Verify install script
./install.sh --check
```

## Commit Messages

Use clear, descriptive commit messages:
- `feat: Add JSON export support`
- `fix: Handle empty MAC addresses in ARP parser`
- `docs: Update installation instructions`
- `refactor: Extract vendor lookup to separate module`

## Pull Request Process

1. Update README.md if adding features
2. Update CHANGELOG.md with your changes
3. Ensure all existing functionality still works
4. Submit PR with clear description of changes

## Reporting Issues

When reporting issues, please include:
- macOS/Linux version
- Bash version (`bash --version`)
- Python version if applicable (`python3 --version`)
- Steps to reproduce
- Expected vs actual behavior
- Sample input file (if relevant)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
