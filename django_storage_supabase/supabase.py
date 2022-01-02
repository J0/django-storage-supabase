# Supabase storage class for Django pluggable storage system.
# Author: Joel Lee <joel@joellee.org>
# License: MIT

import posixpath

# Add below to settings.py:
# SUPABASE_ACCESS_TOKEN = 'YourOauthToken'
# SUPABASE_URL = "https:<your-supabase-id>"
# SUPABASE_ROOT_PATH = '/dir/'
import threading
from typing import Optional

from django.core.files.base import File
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from supabase import create_client

from django_storage_supabase.base import BaseStorage
from django_storage_supabase.compress import CompressedFileMixin, CompressStorageMixin

from .utils import clean_name, setting


@deconstructible
class SupabaseFile(CompressedFileMixin, File):
    def __init__(self):
        pass


@deconstructible
class SupabaseStorage(CompressStorageMixin, BaseStorage):
    def __init__(self):
        self._bucket = None
        self._connections = threading.local()
        self._client = None

    def _open(self):
        raise NotImplementedError("TODO")

    def _save(self, name, content):
        raise NotImplementedError("TODO")

    @property
    def client(self):
        if self._client is None:
            settings = self.get_default_setting()

            self._client = create_client(
                settings["SUPABASE_URL"], settings["SUPABASE_ACCESS_TOKEN"]
            )
        return self._client

    @property
    def bucket(self):
        """
        Get the current bucket. If there is no current bucket object
        create it.
        """
        if self._bucket is None:
            self.client.StorageFileAPI(self.bucket_name)
        return self._bucket

    def get_valid_name(self):
        pass

    def get_default_settings(self):
        # Return Access token and URL
        return {
            "SUPABASE_URL": setting("SUPABASE_URL"),
            "SUPABSE_ACCESS_TOKEN": setting("SUPABASE_ACCESS_TOKEN"),
        }

    def _get_blob(self, name):
        pass

    def listdir(self, name: str):
        name = self._normalize_name(clean_name(name))
        # For bucket.list_blobs and logic below name needs to end in /
        # but for the root path "" we leave it as an empty string
        if name and not name.endswith("/"):
            name += "/"

        directory_contents = self._bucket.list(path=name)

        files = []
        dirs = []
        for entry in directory_contents:
            if entry.get("metadata"):
                files.append(entry["name"])
            else:
                dirs.append(entry["name"])

        return files, dirs

    def delete(self, name: str):
        name = self._normalize_name(clean_name(name))
        try:
            self._bucket.remove(name)
        except Exception as e:
            pass

    def exists(self, name: str):
        name = self._normalize_name(clean_name(name))
        return bool(self._bucket.list(name))

    def size(self, name: str) -> int:
        name = self._normalize_name(clean_name(name))
        return int(self._bucket.list(name)[0]["metadata"]["size"])

    def get_created_time(self, name: str):
        name = self._normalize_name(clean_name(name))
        created = self._bucket.list(name)[0]["created_at"]
        return created if setting("USE_TZ") else timezone.make_naive(created)

    def get_modified_time(self, name: str):
        name = self._normalize_name(clean_name(name))
        updated = self._bucket.list(name)[0]["updated_at"]
        return updated if setting("USE_TZ") else timezone.make_naive(updated)

    def get_available_name(self, name: str, max_length: Optional[int] = ...) -> str:
        return super().get_available_name(name, max_length=max_length)

    def _clean_name(self, name: str) -> str:
        """
        Cleans the name so that Windows style paths work
        """
        # Normalize Windows style paths
        clean_name = posixpath.normpath(name).replace("\\", "/")

        # os.path.normpath() can strip trailing slashes so we implement
        # a workaround here.
        if name.endswith("/") and not clean_name.endswith("/"):
            # Add a trailing slash as it was stripped.
            clean_name += "/"
        return clean_name

    def url(self, name: str) -> str:
        name = self._normalize_name(clean_name(name))
        return self._bucket.get_public_url(name)

    def get_available_name(self, name: str, max_length=None):
        raise NotImplementedError("TODO")
