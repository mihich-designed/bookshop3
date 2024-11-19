import os
from storages.backends.s3boto3 import S3Boto3Storage, S3StaticStorage

# Create your bookshop_storages here.

class StaticStorage(S3StaticStorage):
    location = 'static'
    bucket_name = os.getenv('STATIC_BUCKET_NAME')