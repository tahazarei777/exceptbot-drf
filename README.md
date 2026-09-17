
# ExceptBot DRF

**Exception Logger with AI Suggestions for Django REST Framework.**

[![PyPI version](https://badge.fury.io/py/exceptbot-drf.svg)](https://pypi.org/project/exceptbot-drf/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-3.2%2B-green)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/djangorestframework-3.12%2B-red)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue)](LICENSE.md)

## Overview

ExceptBot DRF is a Django middleware and REST API application that captures, logs, and helps resolve exceptions in Django/DRF projects. Superusers can view exceptions through REST endpoints, request AI-powered fix suggestions from OpenAI, and track resolution status.

This project is a fork of [ExceptBot](https://github.com/geneffects/exceptbot) by Brian Risk, modified to support Django REST Framework APIs, custom user models, and enhanced request metadata.

## Features

- Automatic exception capture via Django middleware
- Full stack trace with code snapshot of the offending file
- File name, line number, and exact line that raised the exception
- Request context: URL path, HTTP method, status code, IP address, user agent, and masked request body
- Source detection (`backend`, `frontend`, `unknown`) via the `X-Client-Type` header
- Smart deduplication: identical exceptions increment a `count` field
- AI-powered fix suggestions via OpenAI ChatGPT
- Resolution tracking with `is_resolved`, `resolved_by`, `resolved_at`, and `resolution_note`
- REST API with superuser-only access
- Singleton `AppSettings` model
- Works with any DRF authentication backend (JWT, Token, Session, OAuth)
- Custom user model support via `AUTH_USER_MODEL`

## Requirements

- Python >= 3.8
- Django >= 3.2
- djangorestframework >= 3.12
- openai >= 1.3.7

## Installation

```bash
pip install exceptbot-drf
```

## Setup

### 1. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'exceptbot',
    # ...
]
```

### 2. Add the middleware

```python
MIDDLEWARE = [
    # ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ...
    'exceptbot.middleware.ExceptBotMiddleware',
]
```

`AuthenticationMiddleware` must appear before `ExceptBotMiddleware` so that `request.user` is available. If you have custom middleware that checks `request.user`, place `ExceptBotMiddleware` before it.

### 3. Configure DRF authentication

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

### 4. Include the URLs

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('exceptbot/', include('exceptbot.urls', namespace='exceptbot')),
    # ...
]
```

### 5. Run migrations

```bash
python manage.py migrate exceptbot
```

### 6. Configure settings

Navigate to `/admin/exceptbot/appsettings/` and set the following fields:

| Field | Description |
| :--- | :--- |
| `project_name` | The directory name of your project (used to locate the correct file in the traceback) |
| `base_url` | Base URL of your site (e.g., `https://myapp.com`) |
| `openai_api_key` | OpenAI API key |

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/exceptbot/api/unresolved/` | List unresolved exceptions |
| GET | `/exceptbot/api/resolved/` | List resolved exceptions |
| GET | `/exceptbot/api/<id>/` | Full exception detail |
| GET | `/exceptbot/api/<id>/error/` | Error message and traceback |
| GET | `/exceptbot/api/<id>/file/` | Content of the offending file |
| POST | `/exceptbot/api/<id>/resolve/` | Mark as resolved |
| POST | `/exceptbot/api/<id>/unresolve/` | Revert to unresolved |
| POST | `/exceptbot/api/<id>/ai/` | Get or generate AI suggestion |
| GET | `/exceptbot/api/settings/` | View settings |
| PUT | `/exceptbot/api/settings/` | Update settings |

All endpoints require superuser authentication.

## Examples

Fetch unresolved exceptions:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/exceptbot/api/unresolved/
```

Mark an exception as resolved:

```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"resolution_note": "Fixed in commit abc123"}' \
     http://localhost:8000/exceptbot/api/1/resolve/
```

Request an AI suggestion:

```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/exceptbot/api/1/ai/
```

Update settings:

```bash
curl -X PUT \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "openai_api_key": "sk-...",
       "base_url": "https://myapp.com",
       "project_name": "my_project"
     }' \
     http://localhost:8000/exceptbot/api/settings/
```

## Source Detection

To distinguish frontend errors from backend errors, include the following header in requests:

```
X-Client-Type: frontend
```

If omitted, the default value is `backend`.

## How It Works

1. The middleware catches exceptions in `process_exception` and inspects the traceback.
2. It walks the traceback in reverse to find the first frame inside the project, matched by `project_name`.
3. It reads the offending file and stores the full source as a code snapshot.
4. It extracts HTTP method, status code, IP address, user agent, and masked request body.
5. Identical exceptions increment `count` instead of creating new records.
6. Superusers query the REST API to view, analyze, and resolve exceptions.

## Security

- Sensitive request fields (`password`, `token`, `api_key`, `authorization`, and similar) are replaced with `***MASKED***` before being stored.
- All endpoints are protected by the `IsSuperUser` permission class.
- The OpenAI API key is hidden in the admin list view and only shown as a boolean.
- Only one `AppSettings` record can exist.

## Project Structure

```
exceptbot/
├── migrations/
├── admin.py
├── apps.py
├── middleware.py
├── models.py
├── permissions.py
├── serializers.py
├── urls.py
└── views.py
```

## Contributing

Issues and pull requests are welcome at:
https://github.com/tahazarei777/exceptbot-drf

## Reporting Issues

Report bugs at:
https://github.com/tahazarei777/exceptbot-drf/issues

## License

This project is a fork of [ExceptBot](https://github.com/geneffects/exceptbot) by Brian Risk.

Original work: Copyright © 2023-present, [D.AT Analytics, LLC](https://d.at/). All rights reserved.

Modifications: Copyright © 2025, Taha Zarei.

Licensed under the BSD 3-Clause License. See [LICENSE.md](LICENSE.md) for details.
```
