from django.core.management.base import BaseCommand
from converter.views import cleanup_old_files

class Command(BaseCommand):
    help = 'Clean up old conversion files and jobs'

    def handle(self, *args, **options):
        self.stdout.write('Starting cleanup...')
        cleanup_old_files()
        self.stdout.write(
            self.style.SUCCESS('Successfully cleaned up old files')
        )