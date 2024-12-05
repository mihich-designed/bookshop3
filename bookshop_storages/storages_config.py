import os
from storages.backends.s3boto3 import S3Boto3Storage, S3StaticStorage
from dotenv import load_dotenv

# Create your storages here.

load_dotenv()

class StaticStorage(S3StaticStorage):
    location = 'static'
    bucket_name = os.getenv('STATIC_BUCKET_NAME')
    default_acl = 'public-read'
    file_overwrite = False
    if bucket_name is None:
        raise ValueError("STATIC_BUCKET_NAME environment variable is not set")

class MediaStorage(S3Boto3Storage):
    location = ''
    bucket_name = os.getenv('MEDIA_BUCKET_NAME')
    default_acl = 'public-read'
    file_overwrite = False

class ContentStorage(S3Boto3Storage):
    location = 'content'
    bucket_name = os.getenv('CONTENT_BUCKET_NAME')
    default_acl = 'public-read'
    file_overwrite = False