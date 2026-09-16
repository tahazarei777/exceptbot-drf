# ExceptBot DRF

Exception Logger with AI Suggestions for Django REST Framework.

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

## Requirements

- Python >= 3.8
- Django >= 3.2
- djangorestframework >= 3.12
- openai >= 1.3.7

## Installation

```bash
pip install exceptbot-drf