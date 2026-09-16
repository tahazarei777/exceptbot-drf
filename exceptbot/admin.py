from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import ExceptionLog, AppSettings


@admin.register(ExceptionLog)
class ExceptionLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'exception_type',
        'short_url',
        'http_method',
        'status_code',
        'source_badge',
        'file_name_short',
        'line_number',
        'user',
        'count',
        'is_resolved_badge',
        'timestamp',
    )

    list_filter = (
        'is_resolved',
        'source',
        'http_method',
        'status_code',
        'exception_type',
        'timestamp',
        'user',
    )

    search_fields = (
        'exception_type',
        'url_path',
        'file_name',
        'full_error_message',
        'error_line_content',
        'user__username',
        'user__email',
    )

    readonly_fields = (
        'url_path',
        'http_method',
        'status_code',
        'source',
        'request_data_display',
        'ip_address',
        'user_agent',
        'exception_type',
        'full_error_message_display',
        'file_name',
        'file_content_display',
        'line_number',
        'error_line_content',
        'user',
        'timestamp',
        'count',
        'resolved_at',
        'ai_suggestion_display',
    )

    ordering = ('-timestamp',)

    list_per_page = 25

    fieldsets = (
        ('error info', {
            'fields': (
                'exception_type',
                'url_path',
                'http_method',
                'status_code',
                'source',
                'timestamp',
                'count',
            )
        }),
        (' position of code', {
            'fields': (
                'file_name',
                'line_number',
                'error_line_content',
                'file_content_display',
            )
        }),
        (' request information', {
            'fields': (
                'request_data_display',
                'ip_address',
                'user_agent',
            ),
            'classes': ('collapse',),
        }),
        (' error message', {
            'fields': (
                'full_error_message_display',
            ),
            'classes': ('collapse',),
        }),
        ('user and status resolved', {
            'fields': (
                'user',
                'is_resolved',
                'resolved_by',
                'resolved_at',
                'resolution_note',
            )
        }),
        ('suggestion of ai', {
            'fields': (
                'ai_suggestion_display',
            ),
            'classes': ('collapse',),
        }),
    )

    # actions = ['mark_as_resolved', 'mark_as_unresolved']

    @admin.display(description='URL')
    def short_url(self, obj):
        if len(obj.url_path) > 40:
            return obj.url_path[:40] + '...'
        return obj.url_path

    @admin.display(description='File')
    def file_name_short(self, obj):
        if not obj.file_name:
            return '-'
        return obj.file_name.split('/')[-1].split('\\')[-1]

    @admin.display(description='Source')
    def source_badge(self, obj):
        colors = {
            'backend': '#007bff',
            'frontend': '#28a745',
            'unknown': '#6c757d',
        }
        color = colors.get(obj.source, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            color,
            obj.get_source_display(),
        )

    @admin.display(description='وضعیت', boolean=True)
    def is_resolved_badge(self, obj):
        return obj.is_resolved

    @admin.display(description='Request Data')
    def request_data_display(self, obj):
        if not obj.request_data:
            return '-'
        import json
        pretty = json.dumps(obj.request_data, indent=2, ensure_ascii=False)
        return format_html(
            '<pre style="background:#f8f9fa;padding:10px;'
            'border-radius:4px;max-height:400px;overflow:auto;">{}</pre>',
            pretty,
        )

    @admin.display(description='Full Error Message')
    def full_error_message_display(self, obj):
        if not obj.full_error_message:
            return '-'
        return format_html(
            '<pre style="background:#fff3cd;padding:10px;'
            'border-radius:4px;max-height:400px;overflow:auto;'
            'white-space:pre-wrap;">{}</pre>',
            obj.full_error_message,
        )

    @admin.display(description='File Content')
    def file_content_display(self, obj):
        if not obj.file_content:
            return '-'
        return format_html(
            '<pre style="background:#f8f9fa;padding:10px;'
            'border-radius:4px;max-height:500px;overflow:auto;'
            'white-space:pre-wrap;">{}</pre>',
            obj.file_content,
        )

    @admin.display(description='AI Suggestion')
    def ai_suggestion_display(self, obj):
        if not obj.ai_suggestion:
            return 'هنوز پیشنهادی ساخته نشده است.'
        return format_html(
            '<div style="background:#e7f3ff;padding:15px;'
            'border-radius:4px;max-height:600px;overflow:auto;'
            'white-space:pre-wrap;">{}</div>',
            obj.ai_suggestion,
        )

    @admin.action(description='✅ علامت‌گذاری به‌عنوان رفع‌شده')
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(
            is_resolved=True,
            resolved_by=request.user,
            resolved_at=timezone.now(),
        )
        self.message_user(
            request,
            f'{updated} خطا به‌عنوان رفع‌شده علامت‌گذاری شد.'
        )

    @admin.action(description='↩️ برگرداندن به حالت رفع‌نشده')
    def mark_as_unresolved(self, request, queryset):
        updated = queryset.update(
            is_resolved=False,
            resolved_by=None,
            resolved_at=None,
            resolution_note='',
        )
        self.message_user(
            request,
            f'{updated} خطا به حالت رفع‌نشده برگشت.'
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'project_name',
        'base_url',
        'has_openai_key',
    )

    fieldsets = (
        ('اطلاعات پروژه', {
            'fields': ('project_name', 'base_url'),
        }),
        ('تنظیمات هوش مصنوعی', {
            'fields': ('openai_api_key',),
            'description': 'برای دریافت پیشنهاد AI، کلید OpenAI خود را وارد کنید.',
        }),
    )

    @admin.display(description='OpenAI Key', boolean=True)
    def has_openai_key(self, obj):
        return bool(obj.openai_api_key)

    def has_add_permission(self, request):
        if AppSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
