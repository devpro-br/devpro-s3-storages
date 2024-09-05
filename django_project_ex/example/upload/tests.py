from unittest.mock import Mock

import pytest
from devpro_s3_storages.handlers import FileConfigurationError, S3FileStorage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from example.upload.models import PrivateFile, PublicFile, InvalidFile


def test_valid_private_file(db, client):
    file = SimpleUploadedFile('private_test_file.txt', 'private_test_file.txt'.encode('UTF8'),
                              content_type='text/plain')
    url = reverse('upload:private')
    client.post(url, {'private_file': file})
    assert PrivateFile.objects.exists()


def test_valid_public_file(db, client):
    file = SimpleUploadedFile('public_test_file.txt', 'public_test_file.txt'.encode('UTF8'),
                              content_type='text/plain')
    url = reverse('upload:public')
    client.post(url, {'public_file': file})
    assert PublicFile.objects.exists()


def test_invalid_file(db, client):
    file = SimpleUploadedFile('invalid_test_file.txt', 'invalid_test_file.txt'.encode('UTF8'),
                              content_type='text/plain')
    url = reverse('upload:invalid')
    with pytest.raises(FileConfigurationError):
        client.post(url, {'invalid_file': file})
        assert not InvalidFile.objects.exists()


@pytest.mark.parametrize('prefix', ['location/public/file', 'location/private/file'])
def test_valid_file_prefix(prefix):
    location = 'location'
    storage = S3FileStorage(location=location)
    storage._validate(prefix)


@pytest.mark.parametrize('prefix', ['location/publi/file', 'location/privat/file'])
def test_invalid_file_prefix(prefix):
    location = 'location'
    storage = S3FileStorage(location=location)
    with pytest.raises(FileConfigurationError):
        storage._validate(prefix)


def test_public_acl():
    location = 'location'
    storage = S3FileStorage(location=location)
    dct = storage.get_object_parameters(f'{location}/public/file')
    assert dct['ACL'] == 'public-read'


def test_private_acl():
    location = 'location'
    storage = S3FileStorage(location=location)
    dct = storage.get_object_parameters(f'{location}/private/file')
    assert dct['ACL'] == 'private'


def test_signed_private_url():
    location = 'location'
    storage = S3FileStorage(location=location)
    signed_url = 'https://your-bucket-name.s3.amazonaws.com/path/to/your-object.txt?AWSAccessKeyId=AKIAIOSFODNN7EXAMPLE&Expires=1611976825&Signature=abc1234xyz5678exampleSignature'
    storage._s3_url = Mock(return_value=signed_url)
    url = storage.url(f'/private/file')
    assert url == signed_url


def test_unsigned_public_url():
    location = 'location'
    storage = S3FileStorage(location=location)
    unsigned_url = 'https://your-bucket-name.s3.amazonaws.com/path/to/your-object.txt'
    signed_url = f'{unsigned_url}?AWSAccessKeyId=AKIAIOSFODNN7EXAMPLE&Expires=1611976825&Signature=abc1234xyz5678exampleSignature'
    storage._s3_url = Mock(return_value=signed_url)
    url = storage.url(f'public/file')
    assert url == unsigned_url
