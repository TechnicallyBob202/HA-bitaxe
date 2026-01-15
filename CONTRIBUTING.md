# Contributing to Bitaxe Integration

Thank you for your interest in contributing to the Bitaxe Home Assistant integration!

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature/fix: `git checkout -b feature/my-feature`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages: `git commit -m "Add feature: XYZ"`
7. Push to your fork
8. Submit a pull request

## Testing Locally

### Manual Testing

1. Copy `custom_components/bitaxe` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via UI
4. Verify all sensors work correctly
5. Test discovery with actual miners if possible
6. Check logs for errors: Settings → System → Logs

### Automated Testing

Run validation locally:

```bash
# HACS validation
docker run --rm -v $(pwd):/github/workspace ghcr.io/hacs/action:latest

# Hassfest validation
docker run --rm -v $(pwd):/github/workspace ghcr.io/home-assistant/hassfest:latest

# Lint with ruff
pip install ruff
ruff check custom_components/bitaxe/
```

## Code Style

This project follows Home Assistant's code style:

- Use `ruff` for linting
- Follow async/await patterns throughout
- Use type hints for all functions
- Add docstrings to all classes and functions
- Keep lines under 88 characters (ruff default)
- Prefer f-strings over .format()

### Example:
```python
async def discover_miners(
    subnet: str,
    concurrency: int = 20,
) -> list[str]:
    """Discover Bitaxe miners in subnet.
    
    Args:
        subnet: Network subnet in CIDR format
        concurrency: Max parallel connections
    
    Returns:
        List of discovered miner IP addresses
    """
    # Implementation
```

## Pull Request Guidelines

- **Title**: Clear, descriptive title (e.g., "Add power sensor" not "Fix stuff")
- **Description**: Explain what you changed and why
- **Testing**: Describe how you tested the changes
- **Breaking Changes**: Note any breaking changes clearly
- **Documentation**: Update README if adding new features
- **One feature per PR**: Keep PRs focused and reviewable

### Example PR Description:
```
## Description
Add power consumption sensor for monitoring miner power draw.

## Changes
- Added POWER sensor type with device class
- Polls `/api/system/metrics` for power data
- Sensor updates every 30 seconds with coordinator

## Testing
- Tested with Bitaxe firmware v0.3.0
- Verified sensor updates correctly
- Checked logs for errors

## Breaking Changes
None
```

## Feature Requests

Have an idea? Open an issue with:
- Clear description of the feature
- Use case / why it's needed
- Any relevant context or examples

## Bug Reports

Found a bug? Open an issue with:
- Home Assistant version
- Integration version
- Exact steps to reproduce
- Expected vs actual behavior
- Relevant logs (Settings → System → Logs)

### Example Bug Report:
```
**HA Version:** 2024.6.0
**Integration Version:** 0.1.0

**Steps to Reproduce:**
1. Add integration with subnet 192.168.1.0/24
2. Select miners to monitor
3. Wait 30 seconds
4. Hashrate sensor shows "unavailable"

**Expected:** Sensor should show hashrate value
**Actual:** Sensor is unavailable

**Logs:**
[Include relevant log entries]
```

## Areas for Contribution

- [ ] Add support for additional Bitaxe API endpoints
- [ ] Improve discovery speed/efficiency
- [ ] Add climate entity for temperature control
- [ ] Add switch entity for power control
- [ ] Improve documentation and examples
- [ ] Add automated tests
- [ ] Support for other mining devices (e.g., Antminer)
- [ ] Performance optimizations

## Code of Conduct

- Be respectful and constructive
- Help others learn and grow
- Focus on technical merit of ideas
- Keep discussions on-topic
- No harassment or discrimination

## Questions?

- Open a discussion issue on GitHub
- Check existing issues/PRs first
- Review Home Assistant integration docs: https://developers.home-assistant.io/

## Commit Message Guidelines

```
<type>: <subject>

<body>

<footer>
```

**Type:**
- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Dependency updates, build changes

**Subject:**
- Use imperative mood ("add" not "adds" or "added")
- Don't capitalize first letter
- No period at the end

**Example:**
```
feat: add power consumption sensor

Add new sensor for monitoring power draw from miner API.
Includes device class for proper HA integration.

Closes #42
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
