# Contributing to MCP GitLab

Thank you for your interest in contributing to MCP GitLab! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Issues

- Check if the issue already exists in the [issue tracker](https://github.com/Vijay-Duke/mcp-gitlab/issues)
- Use the appropriate issue template
- Provide clear description and steps to reproduce
- Include relevant logs, error messages, and system information

### Suggesting Features

- Open a feature request issue
- Clearly describe the problem it solves
- Provide use cases and examples
- Discuss implementation approach if possible

### Contributing Code

1. **Fork the Repository**
   ```bash
   git clone https://github.com/Vijay-Duke/mcp-gitlab.git
   cd mcp-gitlab
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev,test]"
   pre-commit install
   ```

4. **Make Your Changes**
   - Follow the existing code style
   - Add/update tests for your changes
   - Update documentation as needed
   - Keep commits focused and atomic

5. **Run Tests Locally**
   ```bash
   make test        # Run all tests
   make lint        # Check code style
   make format      # Auto-format code
   make type-check  # Run type checking
   ```

6. **Submit a Pull Request**
   - Push your branch to your fork
   - Open a PR against the `main` branch
   - Fill out the PR template completely
   - Ensure all CI checks pass
   - Wait for review and address feedback

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use Black for formatting (configured in `pyproject.toml`)
- Use meaningful variable and function names
- Add type hints where appropriate
- Document complex logic with comments

### Testing

- Write tests for new functionality
- Maintain or improve code coverage
- Use pytest for testing
- Mock external dependencies appropriately
- Include both unit and integration tests

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation if applicable
- Include examples in docstrings

### Commit Messages

Follow conventional commits format:
```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

### Adding New GitLab Tools

When adding new GitLab tools:

1. Define the tool constant in `constants.py`
2. Add tool description in `tool_descriptions.py`
3. Implement handler in `tool_handlers.py`
4. Add tool definition in `tool_definitions.py`
5. Update the handler mapping
6. Write comprehensive tests
7. Update README with the new tool

## Review Process

- All PRs require at least one review
- CI checks must pass
- Reviewers will check for:
  - Code quality and style
  - Test coverage
  - Documentation
  - Security concerns
  - Performance implications

## Release Process

Releases are automated through GitHub Actions when a version tag is pushed:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Questions?

- Open a discussion in [GitHub Discussions](https://github.com/Vijay-Duke/mcp-gitlab/discussions)
- Reach out to maintainers through issues
- Check existing documentation and issues first

## License

By contributing, you agree that your contributions will be licensed under the project's Apache 2.0 License.