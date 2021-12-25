# Supabase storage class for Django pluggable storage system.
# Author: Joel Lee <joel@joellee.org>
# License: MIT

# Add below to settings.py:
# SUPABASE_ACCESS_TOKEN = 'YourOauthToken'
# SUPABASE_URL = "https:<your-supabase-id>"
# SUPABASE_ROOT_PATH = '/dir/'

from django.core.files.base import File
from django.utils.deconstruct import deconstructible

from supabase.base import BaseStorage
from supabase.compress import CompressedFileMixin, CompressStorageMixin


@deconstructible
class SupabaseFile(CompressedFileMixin, File):
    def __init__(self):
        pass


@deconstructible
class SupabaseStorage(CompressStorageMixin, BaseStorage):
    def __init__(self):
        pass
