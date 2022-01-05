# Supabase storage class for Django pluggable storage system.
# Author: Joel Lee <joel@joellee.org>
# License: MIT

import posixpath

# Add below to settings.py:
# SUPABASE_ACCESS_TOKEN = 'YourOauthToken'
# SUPABASE_URL = "https:<your-supabase-id>"
# SUPABASE_ROOT_PATH = '/dir/'
from io import BytesIO
from shutil import copyfileobj
from tempfile import SpooledTemporaryFile

from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.base import File
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from supabase import create_client

from django_storage_supabase.base import BaseStorage
from django_storage_supabase.compress import CompressedFileMixin, CompressStorageMixin

from .utils import (
    check_location,
    clean_name,
    get_available_overwrite_name,
    safe_join,
    setting,
)


@deconstructible
class SupabaseFile(CompressedFileMixin, File):
    """The default file object used by the Supabase Storage.

    Parameters
    ----------
    CompressedFileMixin : [type]
        [description]
    File : [type]
        [description]
    """

    def __init__(self, name, storage):
        self.name = name
        self._file = None
        self._storage = storage

    def _get_file(self):
        if self._file is None:
            self._file = SpooledTemporaryFile()
            response = self._storage_client.download(self.name)
            # TODO: Modify Supabase-py to return response so we can check status == 200 before trying the op
            with BytesIO(response) as file_content:
                copyfileobj(file_content, self._file)
            self._file.seek(0)
        return self._file

    def _set_file(self, value):
        self._file = value

    file = property(_get_file, _set_file)


@deconstructible
class SupabaseStorage(CompressStorageMixin, BaseStorage):
    def __init__(self):
        self._bucket = None
        self._client = None
        self.location = ""
        check_location(self)

    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /path/to/ignored/../something.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """
        try:
            return safe_join(self.location, name)
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)

    def _open(self, name):
        remote_file = SupabaseFile(self._clean_name(name), self)
        return remote_file

    def _save(self, name, content):
        content.open()
        self.client.upload(content.read(), self._clean_name(name))
        content.close()
        return name

    @property
    def client(self):
        if self._client is None:
            settings = self.get_default_settings()
            supabase_url, supabase_access_token = settings.get(
                "SUPABASE_URL"
            ), settings.get("SUPABASE_ACCESS_TOKEN")
            if bool(supabase_url) ^ bool(supabase_access_token):
                raise ImproperlyConfigured(
                    "Both SUPABASE_URL and SUPABASE_ACCESS_TOKEN must be "
                    "provided together."
                )
            self._client = create_client(supabase_url, supabase_access_token).storage()

        return self._client

    @property
    def bucket(self):
        """
        Get the current bucket. If there is no current bucket object
        create it.
        """
        if self._bucket is None:
            self._bucket = self.client.StorageFileAPI(self.bucket_name)
        return self._bucket

    def get_valid_name(self):
        pass

    def get_default_settings(self):
        # Return Access token and URL
        return {
            "SUPABASE_URL": setting("SUPABASE_URL"),
            "SUPABASE_ACCESS_TOKEN": setting("SUPABASE_ACCESS_TOKEN"),
        }

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

        return dirs, files

    def delete(self, name: str):
        name = self._normalize_name(clean_name(name))
        try:
            self._bucket.remove(name)
        except Exception as e:
            pass

    def exists(self, name: str):
        name = self._normalize_name(clean_name(name))
        return bool(self._bucket.list(name))

    def get_accessed_time(self, name: str):
        name = self._normalize_name(clean_name(name))
        accessed = self._bucket.list(name)[0]["accessed_at"]
        return accessed if setting("USE_TZ") else timezone.make_naive(accessed)

    def get_available_name(self, name, max_length=None):
        name = clean_name(name)
        if self.file_overwrite:
            return get_available_overwrite_name(name, max_length)

        return super().get_available_name(name, max_length)

    def get_created_time(self, name: str):
        name = self._normalize_name(clean_name(name))
        created = self._bucket.list(name)[0]["created_at"]
        return created if setting("USE_TZ") else timezone.make_naive(created)

    def get_modified_time(self, name: str):
        name = self._normalize_name(clean_name(name))
        updated = self._bucket.list(name)[0]["updated_at"]
        return updated if setting("USE_TZ") else timezone.make_naive(updated)

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

    def size(self, name: str) -> int:
        name = self._normalize_name(clean_name(name))
        return int(self._bucket.list(name)[0]["metadata"]["size"])

    def url(self, name: str) -> str:
        name = self._normalize_name(clean_name(name))
        return self._bucket.get_public_url(name)
