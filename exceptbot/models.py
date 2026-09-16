import re

from django.conf import settings
from django.db import models
from django.utils import timezone


class ExceptionLog(models.Model):
    SOURCE_CHOICES = [
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('unknown', 'Unknown'),
    ]
    exception_type = models.CharField(max_length=255, db_index=True)
    full_error_message = models.TextField(blank=True)
    file_name = models.CharField(max_length=500, db_index=True)
    file_content = models.TextField(blank=True)
    line_number = models.PositiveIntegerField(null=True, blank=True)
    error_line_content = models.TextField(blank=True)
    url_path = models.TextField(db_index=True)
    http_method = models.CharField(max_length=10, default='GET', db_index=True)
    status_code = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='backend',
        db_index=True,
    )
    request_data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='caused_exceptions',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_resolved = models.BooleanField(default=False, db_index=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='resolved_exceptions',
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True, default='')
    ai_suggestion = models.TextField(null=True, blank=True)
    count = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Exception Log'
        verbose_name_plural = 'Exception Logs'
        indexes = [
            models.Index(fields=['is_resolved', '-timestamp']),
            models.Index(fields=['exception_type', 'file_name', 'is_resolved']),
            models.Index(fields=['source', 'is_resolved']),
        ]

    def __str__(self):
        return f"[{self.source}] {self.exception_type} at {self.url_path}"

    def mark_resolved(self, user, note=''):
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.resolution_note = note
        self.save()

    def get_blocks(self):
        if not self.ai_suggestion:
            return []
        blocks = re.split(r'(```[a-zA-Z]*\n)', self.ai_suggestion)
        formatted_blocks = []
        in_code_block = False
        language = None
        for block in blocks:
            if block.startswith('```'):
                in_code_block = not in_code_block
                language = block[3:].strip()
                if language == '':
                    language = None
            elif in_code_block:
                formatted_blocks.append({
                    'text': block.strip(),
                    'is_code': True,
                    'language': language,
                })
            else:
                formatted_blocks.append({
                    'text': block,
                    'is_code': False,
                    'language': None,
                })
        return formatted_blocks


class AppSettings(models.Model):
    openai_api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Required for AI recommendations. Get an OpenAI account; google 'openai api key'",
    )
    base_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ex: https://exceptbot.com",
    )
    project_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The directory name of your project. Ex: 'exceptbot'",
    )

    class Meta:
        verbose_name = 'App Setting'
        verbose_name_plural = 'App Settings'

    def __str__(self):
        return self.project_name or 'App Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
