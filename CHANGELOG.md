# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-01-XX

### Added
- Django REST Framework API endpoints for exception management
- Custom user model support via `AUTH_USER_MODEL`
- New fields: `http_method`, `status_code`, `source`, `ip_address`, `user_agent`, `request_data`, `resolution_note`
- Source detection via `X-Client-Type` header
- Sensitive data masking for request bodies
- Singleton pattern for `AppSettings` with `get_solo()` method
- `mark_resolved()` method to `ExceptionLog`

### Changed
- Replaced HTML views with REST API endpoints
- Removed form-based UI and HTML templates
- Removed static files (no longer needed)

### Removed
- `forms.py`
- HTML templates
- Static assets

## [Original] - 2023

Based on [ExceptBot](https://github.com/geneffects/exceptbot) by Brian Risk.