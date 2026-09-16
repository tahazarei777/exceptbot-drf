from rest_framework import serializers
from .models import ExceptionLog, AppSettings


class ExceptionLogListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    resolved_by = serializers.StringRelatedField(read_only=True)
    source_display = serializers.SerializerMethodField()

    class Meta:
        model = ExceptionLog
        fields = [
            'id',
            'exception_type',
            'url_path',
            'http_method',
            'status_code',
            'source',
            'source_display',
            'file_name',
            'line_number',
            'user',
            'count',
            'is_resolved',
            'resolved_by',
            'resolved_at',
            'timestamp',
        ]

    def get_source_display(self, obj):
        return obj.get_source_display()



class ExceptionLogDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    resolved_by = serializers.StringRelatedField(read_only=True)
    source_display = serializers.SerializerMethodField()

    class Meta:
        model = ExceptionLog
        fields = '__all__'

    def get_source_display(self, obj):
        return obj.get_source_display()



class ExceptionLogResolveSerializer(serializers.Serializer):
    resolution_note = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        max_length=2000,
    )



class AppSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSettings
        fields = ['openai_api_key', 'base_url', 'project_name']
        extra_kwargs = {
            'openai_api_key': {'write_only': False, 'required': False},
        }