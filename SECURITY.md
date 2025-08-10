# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of MCP GitLab seriously. If you have discovered a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Send details to the maintainers through a private channel
3. Include the following information:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue

### What to Expect

- Acknowledgment of your report within 48 hours
- A more detailed response within 7 days
- Regular updates on the progress
- Credit in the fix announcement (unless you prefer to remain anonymous)

## Security Best Practices

When using MCP GitLab:

### Authentication

- **Never commit tokens**: Store GitLab tokens in environment variables
- **Use minimal scopes**: Only grant the permissions your application needs
- **Rotate tokens regularly**: Update your tokens periodically
- **Use OAuth when possible**: Prefer OAuth tokens over personal access tokens

### Environment Variables

Required environment variables should be set securely:
```bash
export GITLAB_PRIVATE_TOKEN="your-token-here"  # Never commit this
export GITLAB_URL="https://gitlab.com"         # Or your GitLab instance
```

### Configuration

- Store sensitive configuration in `.env` files (not tracked by git)
- Use `.env.example` for configuration templates without secrets
- Review dependencies regularly for known vulnerabilities

## Security Features

MCP GitLab includes several security features:

- **Token validation**: Validates GitLab tokens before use
- **Rate limiting**: Respects GitLab API rate limits
- **Error sanitization**: Sanitizes error messages to avoid token leaks
- **Secure defaults**: Uses HTTPS by default for API calls
- **Input validation**: Validates and sanitizes user inputs

## Dependencies

We regularly update dependencies to patch known vulnerabilities:
- Automated dependency updates via Dependabot
- Security scanning in CI/CD pipeline
- Regular security audits with `pip-audit` and `safety`

## Disclosure Policy

When we receive a security report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported versions
4. Release new security fix versions
5. Announce the vulnerability after the fix is released

## Contact

For security concerns, please contact the maintainers through GitHub.

## Acknowledgments

We thank all security researchers who responsibly disclose vulnerabilities to us.