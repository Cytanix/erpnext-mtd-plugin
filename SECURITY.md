# Security Policy

## Supported Versions

ERPNext MTD is currently pre-release.

Until the first stable release, security fixes are applied to the latest
development version only.

| Version | Supported |
| --- | --- |
| main / latest pre-release | Yes |
| Older pre-releases | No |
| 1.0 and later | Not yet released |

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues,
discussions, or pull requests.

Use GitHub's **Private Vulnerability Reporting** feature for this repository
instead.

When reporting a vulnerability, please include where possible:

- A description of the issue
- Affected versions or commits
- Steps to reproduce
- Potential impact
- Any suggested mitigation or fix

Please do not include real HMRC credentials, access tokens, refresh tokens,
taxpayer data, or other sensitive information unless absolutely necessary to
demonstrate the issue.

## Scope

Security issues may include, but are not limited to:

- HMRC OAuth or token handling
- Authentication or authorisation bypasses
- Permission boundary failures
- Fraud prevention header spoofing or trust issues
- Exposure of HMRC credentials or taxpayer information
- Replay attacks or OAuth state handling weaknesses
- Server-side request forgery or unsafe network behaviour
- Injection vulnerabilities
- Sensitive information exposure
- Security flaws affecting VAT submission behaviour

## Disclosure

Please allow a reasonable period for investigation and remediation before
public disclosure.

Where appropriate, security fixes may be released before full technical details
are published.

## Security Updates

Security fixes will be documented in release notes where appropriate.