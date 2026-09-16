"""
URL configuration for ExceptBot DRF API.

Endpoints:
    GET  /exceptbot/api/unresolved/
    GET  /exceptbot/api/resolved/
    GET  /exceptbot/api/settings/
    PUT  /exceptbot/api/settings/
    GET  /exceptbot/api/<log_id>/
    GET  /exceptbot/api/<log_id>/error/
    GET  /exceptbot/api/<log_id>/file/
    POST /exceptbot/api/<log_id>/resolve/
    POST /exceptbot/api/<log_id>/unresolve/
    POST /exceptbot/api/<log_id>/ai/
"""
from django.urls import path

from .views import (
    UnresolvedExceptionListView,
    ResolvedExceptionListView,
    ExceptionDetailView,
    ExceptionErrorMessageView,
    ExceptionFileContentView,
    MarkResolvedView,
    MarkUnresolvedView,
    AIRecommendationView,
    AppSettingsView,
)

app_name = 'exceptbot'

urlpatterns = [
    # ---------- لیست‌ها ----------
    path(
        'api/unresolved/',
        UnresolvedExceptionListView.as_view(),
        name='unresolved-list',
    ),
    path(
        'api/resolved/',
        ResolvedExceptionListView.as_view(),
        name='resolved-list',
    ),

    # ---------- تنظیمات ----------
    path(
        'api/settings/',
        AppSettingsView.as_view(),
        name='app-settings',
    ),

    # ---------- جزئیات ----------
    path(
        'api/<int:log_id>/',
        ExceptionDetailView.as_view(),
        name='exception-detail',
    ),
    path(
        'api/<int:log_id>/error/',
        ExceptionErrorMessageView.as_view(),
        name='exception-error',
    ),
    path(
        'api/<int:log_id>/file/',
        ExceptionFileContentView.as_view(),
        name='exception-file',
    ),

    # ---------- عملیات ----------
    path(
        'api/<int:log_id>/resolve/',
        MarkResolvedView.as_view(),
        name='mark-resolved',
    ),
    path(
        'api/<int:log_id>/unresolve/',
        MarkUnresolvedView.as_view(),
        name='mark-unresolved',
    ),
    path(
        'api/<int:log_id>/ai/',
        AIRecommendationView.as_view(),
        name='ai-recommendation',
    ),
]