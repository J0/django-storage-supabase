from unittest import mock

from django.test import TestCase

from django_storage_supabase import supabase


class SupabaseStorageTests(TestCase):
    def setUp(self):
        self.storage = supabase.SupabaseStorage()
        self.storage._bucket = mock.MagicMock()
        self.storage._client = mock.MagicMock()
        self.storage.bucket_name = "test_bucket"
        self.file_overwrite = False

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
        # TODO: Implement
        # name = "test_storage_save.txt"
        # content = ContentFile("new content")
        # self.storage.save(name, content)
        # self.storage.bucket.Object.assert_called_once_with(name)

        # obj = self.storage.bucket.Object.return_value
        # obj.upload_fileobj.assert_called_with(
        #     content,
        #     ExtraArgs={
        #         "ContentType": "text/plain",
        #     },
        # )

    def test_content_type(self):
        """
        Test saving a file with a None content type.
        """
        # TODO: Implement
        # name = "test_image.jpg"
        # content = ContentFile("data")
        # content.content_type = None
        # self.storage.save(name, content)
        # self.storage._bucket.list.assert_called_once_with(name)

        # obj = self.storage._bucket.list.return_value
        # obj.upload_fileobj.assert_called_with(
        #     content,
        #     ExtraArgs={
        #         "ContentType": "image/jpeg",
        #     },
        # )

    def test_storage_save_gzipped(self):
        """
        Test saving a gzipped file
        """
        # TODO: Implement
        # name = "test_storage_save.gz"
        # content = ContentFile("I am gzip'd")
        # self.storage.save(name, content)
        # obj = self.storage._bucket.upload.return_value
        # obj.upload_fileobj.assert_called_with(
        #     content,
        #     ExtraArgs={
        #         "ContentType": "application/octet-stream",
        #         "ContentEncoding": "gzip",
        #     },
        # )

    def test_storage_exists(self):
        filename = "path/to/file.txt"
        self.storage._bucket = mock.MagicMock()
        self.assertTrue(self.storage.exists(filename))
        self.storage._bucket.list.assert_called_with(filename)

        self.storage._bucket.reset_mock()
        self.storage._bucket.list.return_value = []
        self.assertFalse(self.storage.exists(filename))
        self.storage._bucket.list.assert_called_with(filename)

    def test_storage_exists_false(self):
        # TODO: Implement
        pass

    def test_storage_delete(self):
        self.storage.delete("path/to/file.txt")
        self.storage.bucket.remove.assert_called_with("path/to/file.txt")

    def test_storage_listdir_subdir(self):
        # Files:
        #   some/dir/
        #   some/2.txt
        pages = [
            {
                "name": "dir",
                "id": None,
                "updated_at": None,
                "created_at": None,
                "last_accessed_at": None,
                "metadata": None,
            },
            {
                "name": "2.txt",
                "id": "756dae5b-0ba3-4d50-9ade-1ea24afdf479",
                "updated_at": "2021-08-16T14:38:35.882189+00:00",
                "created_at": "2021-08-16T14:38:35.882189+00:00",
                "last_accessed_at": "2021-08-16T14:38:35.882189+00:00",
                "metadata": {
                    "size": 15,
                    "mimetype": "application/x-www-form-urlencoded",
                    "cacheControl": "no-cache",
                },
            },
        ]
        self.storage._bucket.list.return_value = pages

        dirs, files = self.storage.listdir("some/")

        self.assertEqual(dirs, ["dir"])
        self.assertEqual(files, ["2.txt"])

    def test_storage_listdir_empty(self):
        # Files:
        #   dir/
        pages = [
            {
                "name": "dir",
                "id": None,
                "updated_at": None,
                "created_at": None,
                "last_accessed_at": None,
                "metadata": None,
            },
        ]

        dirs, files = self.storage.listdir("dir/")

        self.storage._bucket.list.return_value = pages

        self.assertEqual(dirs, [])
        self.assertEqual(files, [])

    def test_storage_mtime(self):
        # Test both USE_TZ cases
        for use_tz in (True, False):
            with self.settings(USE_TZ=use_tz):
                self._test_storage_mtime(use_tz)

    def _test_storage_mtime(self, use_tz):
        # TODO: Implement
        # obj = self.storage._bucket.return_value
        # obj.last_modified = datetime.now(utc)

        # name = "file.txt"
        # self.assertFalse(
        #     is_aware(self.storage.modified_time(name)),
        #     "Naive datetime object expected from modified_time()",
        # )

        # self.assertIs(
        #     settings.USE_TZ,
        #     is_aware(self.storage.get_modified_time(name)),
        #     "{} datetime object expected from get_modified_time() when USE_TZ={}".format(
        #         ("Naive", "Aware")[settings.USE_TZ], settings.USE_TZ
        #     ),
        # )
        pass
