# devpro-s3-storages
Django Project to handle Static and Upload Files on s3 the right way

## How to use

Install it using your pacakage manager:

```bash
poetry add devpro-s3-storages
```

Configure your Django Settings to use those handlers:

```python
AWS_STORAGE_BUCKET_NAME = '' # Empty means no s3 configuration so local filesystem will be used. Suitable for dev env 

if AWS_STORAGE_BUCKET_NAME == '':
    # Config to make static files locally
    STATIC_URL = 'static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    
    # Config to make uploading/downloading files locally
    MEDIA_ROOT = BASE_DIR / 'mediafiles'
    MEDIA_URL = '/mediafiles/'
    
    # Configuration to raise error in case ImageField/FileField does not define the property "upload_to" having 
    # "public/" or "private/" as prefix. See Model Usage to check those options
    STORAGES = {
        "default": {
            "BACKEND": "devpro_s3_storages.handlers.FileSystemWithValidationStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    # Configuration to work using S3 bucket for static and file uploads/downloads
    STATIC_URL = f'//{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'

    AWS_S3_ACCESS_KEY_ID = 'AWS_S3_ACCESS_KEY_ID'
    AWS_S3_SECRET_ACCESS_KEY = 'AWS_S3_SECRET_ACCESS_KEY'
    STORAGES = {
        "default": {
            "BACKEND": "devpro_s3_storages.handlers.S3FileStorage",
            "OPTIONS": {
                'default_acl': 'private',
                'location': 'media',
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                'default_acl': 'public-read',
                'location': 'static',
                'querystring_auth': False
            },
        },
    }

```

So what this configuration will do when S3 bucket settings are provided?

### Collect Static

Running `python manage.py collectstatic` will upload files to s3 with public-read permissions (Ensure to allow this on your S3 bucket configuration).
It will upload your static files under "static" folder in your bucket
It will generate unsigned urls for statics. Since static will be accessed on your site, they are already public, so why spending resource on  creation signed urls for them?

### File upload and download

When configuring ImageField/FileField in you models, you will need to define it the file will be public available or private.
This will be setup using the "upload_to" property:

```python
class PrivateFile(models.Model):
    private_file = models.FileField(upload_to='private/right')


class PublicFile(models.Model):
    public_file = models.FileField(upload_to='public/right')
```

So `PrivateFile.private_file` will be uploaded to bucket folder "media/private/right". 
It will have private access, meaning only signed url will be able to access this content.
So `PrivateFile.private_file.url()` method will always generate a private signed url

On the other hand `PublicFile.private_file` will be uploaded to bucket folder "media/public/right". 
It will have public access, meaning ounsigned url will be able to access this content.
So `PublicFile.private_file.url()` method will always generate a public url

Why this organization?

Some files are public, such as your avatar image in a social network. So it can better levarage cache and having a simple url.

Some file need privacy, such as some tax report you are collection. Si a signed url is needed for security puposes.

So this simple library delivery this kind of organization.

### How to serve upload files locally?

The last step to having a proper local environment is making django to serv upload files when in dev environment.
So add this config to the final of your `urls.py` file:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[]  # your mapped paths in here

# Add this path in case s3 bucket is not configured on settings
if settings.AWS_STORAGE_BUCKET_NAME == '':
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
```

You can check a project example on  https://github.com/devpro-br/devpro-s3-storages/tree/main/django_project_ex

Cheers!