from django.db import models
from django.utils import timezone
import uuid

class ConversionJob(models.Model):
    CONVERSION_TYPES = [
        ('jpg_to_pdf', 'JPG to PDF'),
        ('png_to_pdf', 'PNG to PDF'),
        ('pdf_to_jpg', 'PDF to JPG'),
        ('resize_image', 'Resize Image'),
        ('compress_image', 'Compress Image'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversion_type = models.CharField(max_length=20, choices=CONVERSION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    original_filename = models.CharField(max_length=255)
    converted_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.conversion_type} - {self.original_filename}"
    
    def get_status_display_with_icon(self):
        status_icons = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'failed': '❌',
        }
        return f"{status_icons.get(self.status, '')} {self.get_status_display()}"