# Supabase storage class for Django pluggable storage system.
# Author: Joel Lee <joel@joellee.org>
# License: MIT

# Add below to settings.py:
# SUPABASE_ACCESS_TOKEN = 'YourOauthToken'
# SUPABASE_URL = "https:<your-supabase-id>"
# SUPABASE_ROOT_PATH = '/dir/'

from typing import Optional

from django.core.files.base import File
from django.utils.deconstruct import deconstructible

from django_storage_supabase.base import BaseStorage
from django_storage_supabase.compress import CompressedFileMixin, CompressStorageMixin


@deconstructible
class SupabaseFile(CompressedFileMixin, File):
    def __init__(self):
        pass


@deconstructible
class SupabaseStorage(CompressStorageMixin, BaseStorage):
    def __init__(self):
        self._bucket = None

    def _open(self):
        pass

    def _save(self):
        pass

    @property
    def bucket(self):
        """
        Get the current bucket. If there is no current bucket object
        create it.
        """
        if self._bucket is None:
            # TODO: Fetch bucket
            self._bucket = None
            # self.connection.Bucket(self.bucket_name)
        return self._bucket

    def get_valid_name(self):
        pass

    def get_default_settings(self):
        # Return Access token and URL
        pass

    def listdir(self, name: str):
        pass

    def delete(self, name: str):
        pass

    def exists(self, name: str):
        pass

    def size(self, name: str):
        pass

    def get_modified_time(self, name: str):
        pass

    def get_available_name(self, name: str, max_length: Optional[int] = ...) -> str:
        return super().get_available_name(name, max_length=max_length)
