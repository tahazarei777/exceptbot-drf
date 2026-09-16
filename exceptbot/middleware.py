import sys
import traceback

from django.db import transaction
from django.utils import timezone
from .models import ExceptionLog, AppSettings
SENSITIVE_FIELDS = {
    'password', 'password1', 'password2',
    'token', 'access', 'refresh',
    'secret', 'api_key', 'authorization',
}

def mask_sensitive_data(data):
    if not isinstance(data, dict):
        return data

    masked = {}
    for key, value in data.items():
        if key.lower() in SENSITIVE_FIELDS:
            masked[key] = '***MASKED***'
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value)
        elif isinstance(value, list):
            masked[key] = [
                mask_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            masked[key] = value
    return masked


class ExceptBotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        app_settings = AppSettings.get_solo()
        project_name = app_settings.project_name or ''
        exc_type, exc_value, exc_traceback = sys.exc_info()
        formatted_traceback = traceback.extract_tb(exc_traceback)

        file_name = None
        line_number = None
        error_line_content = None
        if project_name:
            for stack in reversed(formatted_traceback):
                if project_name in stack.filename:
                    file_name = stack.filename
                    line_number = stack.lineno
                    error_line_content = stack.line
                    break
        if not file_name and formatted_traceback:
            stack = formatted_traceback[-1]
            file_name = stack.filename
            line_number = stack.lineno
            error_line_content = stack.line

        full_error_message = ''.join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        file_content = ''
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                file_content = file.read()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, TypeError):
            file_content = f"# Could not read file: {file_name}"
        url_path = request.path
        exception_type = str(type(exception).__name__)
        http_method = request.method
        status_code = 500
        source = request.META.get('HTTP_X_CLIENT_TYPE', 'backend').lower()
        if source not in ('backend', 'frontend'):
            source = 'unknown'
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:1000]

        request_data = None
        try:
            if hasattr(request, 'data'):
                request_data = mask_sensitive_data(dict(request.data))
            elif http_method in ('POST', 'PUT', 'PATCH'):
                request_data = mask_sensitive_data(dict(request.POST))
        except Exception:
            request_data = None
        with transaction.atomic():
            existing_exception = ExceptionLog.objects.filter(
                exception_type=exception_type,
                file_name=file_name,
                is_resolved=False,
            ).first()

            if existing_exception:
                existing_exception.count += 1
                existing_exception.timestamp = timezone.now()
                existing_exception.save(update_fields=['count', 'timestamp'])
            else:
                ExceptionLog.objects.create(
                    url_path=url_path,
                    exception_type=exception_type,
                    full_error_message=full_error_message,
                    file_name=file_name,
                    file_content=file_content,
                    line_number=line_number,
                    error_line_content=error_line_content,
                    user=user,
                    http_method=http_method,
                    status_code=status_code,
                    source=source,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_data=request_data,
                )

        return None