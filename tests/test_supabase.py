from datetime import datetime
from unittest import mock

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils.timezone import is_aware, utc

from django_storage_supabase import supabase


class SupabaseStorageTests(TestCase):
    def setUp(self):
        self.storage = supabase.SupabaseStorage()
        self.storage._connections.connection = mock.MagicMock()

    def test_clean_name(self):
        """
        Test the base case of _clean_name
        """
        path = self.storage._clean_name("path/to/somewhere")
        self.assertEqual(path, "path/to/somewhere")

    def test_clean_name_normalize(self):
        """
        Test the normalization of _clean_name
        """
        path = self.storage._clean_name("path/to/../somewhere")
        self.assertEqual(path, "path/somewhere")

    def test_clean_name_trailing_slash(self):
        """
        Test the _clean_name when the path has a trailing slash
        """
        path = self.storage._clean_name("path/to/somewhere/")
        self.assertEqual(path, "path/to/somewhere/")

    def test_clean_name_windows(self):
        """
        Test the _clean_name when the path has a trailing slash
        """
        path = self.storage._clean_name("path\\to\\somewhere")
        self.assertEqual(path, "path/to/somewhere")

    def test_storage_save(self):
        """
        Test saving a file
        """
        name = "test_storage_save.txt"
        content = ContentFile("new content")
        self.storage.save(name, content)
        self.storage.bucket.Object.assert_called_once_with(name)

        obj = self.storage.bucket.Object.return_value
        obj.upload_fileobj.assert_called_with(
            content,
            ExtraArgs={
                "ContentType": "text/plain",
            },
        )

    def test_content_type(self):
        """
        Test saving a file with a None content type.
        """
        name = "test_image.jpg"
        content = ContentFile("data")
        content.content_type = None
        self.storage.save(name, content)
        self.storage.bucket.Object.assert_called_once_with(name)

        obj = self.storage.bucket.Object.return_value
        obj.upload_fileobj.assert_called_with(
            content,
            ExtraArgs={
                "ContentType": "image/jpeg",
            },
        )

    def test_storage_save_gzipped(self):
        """
        Test saving a gzipped file
        """
        name = "test_storage_save.gz"
        content = ContentFile("I am gzip'd")
        self.storage.save(name, content)
        obj = self.storage.bucket.Object.return_value
        obj.upload_fileobj.assert_called_with(
            content,
            ExtraArgs={
                "ContentType": "application/octet-stream",
                "ContentEncoding": "gzip",
            },
        )

    def test_storage_exists(self):
        self.assertTrue(self.storage.exists("file.txt"))
        self.storage.connection.meta.client.head_object.assert_called_with(
            Bucket=self.storage.bucket_name,
            Key="file.txt",
        )

    def test_storage_exists_false(self):
        raise NotImplementedError("TODO")

    def test_storage_delete(self):
        self.storage.delete("path/to/file.txt")
        self.storage.bucket.Object.assert_called_with("path/to/file.txt")
        self.storage.bucket.Object.return_value.delete.assert_called_with()

    def test_storage_listdir_subdir(self):
        # Files:
        #   some/path/1.txt
        #   some/2.txt
        pages = [
            {
                "CommonPrefixes": [
                    {"Prefix": "some/path"},
                ],
                "Contents": [
                    {"Key": "some/2.txt"},
                ],
            },
        ]

        paginator = mock.MagicMock()
        paginator.paginate.return_value = pages
        self.storage._connections.connection.meta.client.get_paginator.return_value = (
            paginator
        )

        dirs, files = self.storage.listdir("some/")
        paginator.paginate.assert_called_with(
            Bucket=None, Delimiter="/", Prefix="some/"
        )

        self.assertEqual(dirs, ["path"])
        self.assertEqual(files, ["2.txt"])

    def test_storage_listdir_empty(self):
        # Files:
        #   dir/
        pages = [
            {
                "Contents": [
                    {"Key": "dir/"},
                ],
            },
        ]

        paginator = mock.MagicMock()
        paginator.paginate.return_value = pages
        self.storage._connections.connection.meta.client.get_paginator.return_value = (
            paginator
        )

        dirs, files = self.storage.listdir("dir/")
        paginator.paginate.assert_called_with(Bucket=None, Delimiter="/", Prefix="dir/")

        self.assertEqual(dirs, [])
        self.assertEqual(files, [])

    def test_storage_mtime(self):
        # Test both USE_TZ cases
        for use_tz in (True, False):
            with self.settings(USE_TZ=use_tz):
                self._test_storage_mtime(use_tz)

    def _test_storage_mtime(self, use_tz):
        obj = self.storage.bucket.Object.return_value
        obj.last_modified = datetime.now(utc)

        name = "file.txt"
        self.assertFalse(
            is_aware(self.storage.modified_time(name)),
            "Naive datetime object expected from modified_time()",
        )

        self.assertIs(
            settings.USE_TZ,
            is_aware(self.storage.get_modified_time(name)),
            "{} datetime object expected from get_modified_time() when USE_TZ={}".format(
                ("Naive", "Aware")[settings.USE_TZ], settings.USE_TZ
            ),
        )
