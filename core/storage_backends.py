from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Custom S3 storage for media files with presigned URLs.
    """
    location = ''
    file_overwrite = False
    default_acl = None
    querystring_auth = True  # Generate presigned URLs
    querystring_expire = 3600  # URLs valid for 1 hour
    signature_version = 's3v4'
    addressing_style = 'virtual'
    # Add aggressive caching for media (safe for immutable, versioned keys)
    object_parameters = {
        'CacheControl': 'public, max-age=31536000, immutable',
    }
