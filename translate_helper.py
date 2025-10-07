import os
import django
from googletrans import Translator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

# This is just a helper to get initial translations
# You should review and improve them manually

translator = Translator()

languages = {
    'pt': 'portuguese',
    'es': 'spanish',
    'de': 'german',
    'id': 'indonesian',
    'fr': 'french',
    'tr': 'turkish'
}

# Note: Install googletrans: pip install googletrans==3.1.0a0