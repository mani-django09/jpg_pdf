from django.contrib import admin
from django.utils.html import format_html
from .models import ConversionJob

@admin.register(ConversionJob)
class ConversionJobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'original_filename', 'conversion_type', 
        'status_with_icon', 'file_size_formatted', 'created_at'
    ]
    list_filter = ['conversion_type', 'status', 'created_at']
    search_fields = ['original_filename', 'converted_filename', 'id']
    readonly_fields = ['id', 'created_at', 'completed_at', 'file_size_formatted']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def status_with_icon(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_with_icon.short_description = 'Status'
    
    def file_size_formatted(self, obj):
        if obj.file_size == 0:
            return '0 Bytes'
        
        size = obj.file_size
        for unit in ['Bytes', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_formatted.short_description = 'File Size'