# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of MCP GitLab Server
- Core GitLab API integration with python-gitlab
- 50+ GitLab tools for comprehensive repository management
- User and profile management tools (18 tools)
- Project, issue, and merge request management
- Git operations (commits, branches, tags)
- CI/CD pipeline management
- Code review and collaboration tools
- Search functionality across projects and content
- Group and snippet management
- Job and artifact handling
- Comprehensive error handling and retry logic
- Rate limiting support
- Response caching for performance
- Automatic git repository detection
- Environment-based configuration
- Structured logging with JSON support

### Security
- Secure token handling (OAuth and Personal Access Tokens)
- Input validation and sanitization
- Error message sanitization to prevent token leaks

### Documentation
- Comprehensive README with installation and usage instructions
- Contributing guidelines
- Security policy
- Code of conduct
- Issue and PR templates

### Testing
- 100+ unit tests with pytest
- Integration test support
- CI/CD pipeline with GitHub Actions
- Multi-version Python testing (3.10, 3.11, 3.12)
- Code coverage reporting with Codecov
- Security scanning with Bandit, Safety, and pip-audit

## [0.1.0] - TBD

Initial release - see Unreleased section above for features.

[Unreleased]: https://github.com/Vijay-Duke/mcp-gitlab/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Vijay-Duke/mcp-gitlab/releases/tag/v0.1.0