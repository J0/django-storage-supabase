# Django-Storage-Supabase(Alpha)


## About

This project aims to provide a custom storage backend for Supabase Storage so that it can be used as `/media` storage. This project heavily references the S3/Google Custom Storage backend in  [Django-Storages](https://github.com/jschneier/django-storages)


To do this we follow the [specification provided by Django](https://docs.djangoproject.com/en/4.0/howto/custom-file-storage/)

Eventually, we hope that this can be integrated into the django-storages library
and then write a blogpost/tutorial about it.




## Usage Instructions

1. `pip3 install django-storage-supabase	`

2. In `settings.py` set the following variables 

``` python
DEFAULT_FILE_STORAGE = 'django_storage_supabase.supabase'
SUPABASE_API_KEY = ''
SUPABASE_URL = "https:<your-supabase-id>"
SUPABASE_ROOT_PATH = '/dir/'
```

You can then use the following to upload to your backend.

``` python
photo = models.FileField(
    upload_to='photos',
)
```

Here's a [reference (WIP) example](https://github.com/supabase/supabase/pull/5688) of how to use Supabase storage as a backend together with the rest of the Supabase libraries.


## TODOs:
- Implement save
- Implement open and write
- Test the package.
