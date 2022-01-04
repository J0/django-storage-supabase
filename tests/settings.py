MEDIA_URL = "/media/"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

SECRET_KEY = "hailthesunshine"

USE_TZ = True

# TODO: Patch this somewhere
SUPABASE_URL = "https://test-supabase-url.co"
SUPABASE_ACCESS_TOKEN = "e124121"
