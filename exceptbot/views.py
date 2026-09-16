from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from openai import OpenAI

from .models import ExceptionLog, AppSettings
from .permissions import IsSuperUser
from .serializers import (
    ExceptionLogListSerializer,
    ExceptionLogDetailSerializer,
    ExceptionLogResolveSerializer,
    AppSettingsSerializer,
)


# ============================================================
# GET /exceptbot/api/unresolved/
# ============================================================
class UnresolvedExceptionListView(ListAPIView):
    serializer_class = ExceptionLogListSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        return ExceptionLog.objects.filter(
            is_resolved=False
        ).order_by('-timestamp')


# ============================================================
# GET /exceptbot/api/resolved/
# ============================================================
class ResolvedExceptionListView(ListAPIView):
    serializer_class = ExceptionLogListSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        return ExceptionLog.objects.filter(
            is_resolved=True
        ).order_by('-timestamp')


# ============================================================
# GET /exceptbot/api/<log_id>/
# ============================================================
class ExceptionDetailView(RetrieveAPIView):
    queryset = ExceptionLog.objects.all()
    serializer_class = ExceptionLogDetailSerializer
    permission_classes = [IsSuperUser]
    lookup_url_kwarg = 'log_id'


# ============================================================
# GET /exceptbot/api/<log_id>/error/
# ============================================================
class ExceptionErrorMessageView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, log_id):
        try:
            log = ExceptionLog.objects.get(id=log_id)
        except ExceptionLog.DoesNotExist:
            return Response(
                {'detail': 'Exception log not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({
            'id': log.id,
            'exception_type': log.exception_type,
            'full_error_message': log.full_error_message,
        })


# ============================================================
# GET /exceptbot/api/<log_id>/file/
# ============================================================
class ExceptionFileContentView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, log_id):
        try:
            log = ExceptionLog.objects.get(id=log_id)
        except ExceptionLog.DoesNotExist:
            return Response(
                {'detail': 'Exception log not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({
            'id': log.id,
            'file_name': log.file_name,
            'line_number': log.line_number,
            'error_line_content': log.error_line_content,
            'file_content': log.file_content,
        })


# ============================================================
# POST /exceptbot/api/<log_id>/resolve/
# ============================================================
class MarkResolvedView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request, log_id):
        try:
            log = ExceptionLog.objects.get(id=log_id)
        except ExceptionLog.DoesNotExist:
            return Response(
                {'detail': 'Exception log not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ExceptionLogResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if log.is_resolved:
            return Response(
                {'detail': 'این خطا قبلاً رفع شده است.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        log.mark_resolved(
            user=request.user,
            note=serializer.validated_data.get('resolution_note', ''),
        )

        return Response(
            ExceptionLogDetailSerializer(log).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# POST /exceptbot/api/<log_id>/unresolve/
# ============================================================
class MarkUnresolvedView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request, log_id):
        try:
            log = ExceptionLog.objects.get(id=log_id)
        except ExceptionLog.DoesNotExist:
            return Response(
                {'detail': 'Exception log not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        log.is_resolved = False
        log.resolved_by = None
        log.resolved_at = None
        log.resolution_note = ''
        log.save()

        return Response(
            ExceptionLogDetailSerializer(log).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# POST /exceptbot/api/<log_id>/ai/
# ============================================================
class AIRecommendationView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request, log_id):
        try:
            log = ExceptionLog.objects.get(id=log_id)
        except ExceptionLog.DoesNotExist:
            return Response(
                {'detail': 'Exception log not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        app_settings = AppSettings.get_solo()
        if not app_settings.openai_api_key:
            return Response(
                {'detail': 'OpenAI API key is not configured.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if log.ai_suggestion:
            return Response({
                'id': log.id,
                'ai_suggestion': log.ai_suggestion,
                'cached': True,
            })
        exception_information = f"""My Django application has thrown an exception.
An exception happened in line {log.line_number} of file {log.file_name}.
The exception type is: {log.exception_type}

The content of the exception message is:
{log.full_error_message}

text

The content of the file that produced the exception is:
{log.file_content}

text

The specific line from the above that threw the error is:
{log.error_line_content}

text

Please provide a suggestion for how to address the issue.
"""

        messages = [
            {
                "role": "system",
                "content": (
                    "You are ExceptBot. Users send you information about exceptions "
                    "in their Django applications and you respond with useful instructions "
                    "and code on how to fix the issue. Please answer efficiently and use "
                    "an economy of words."
                ),
            },
            {
                "role": "user",
                "content": exception_information,
            },
        ]

        try:
            client = OpenAI(api_key=app_settings.openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
            )

            log.ai_suggestion = response.choices[0].message.content
            log.save(update_fields=['ai_suggestion'])

        except Exception as exc:
            return Response(
                {'detail': f'AI service error: {str(exc)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            'id': log.id,
            'ai_suggestion': log.ai_suggestion,
            'cached': False,
        })


# ============================================================
# GET  /exceptbot/api/settings/
# PUT  /exceptbot/api/settings/
# ============================================================
class AppSettingsView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        app_settings = AppSettings.get_solo()
        serializer = AppSettingsSerializer(app_settings)
        return Response(serializer.data)

    def put(self, request):
        app_settings = AppSettings.get_solo()
        serializer = AppSettingsSerializer(
            app_settings,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)