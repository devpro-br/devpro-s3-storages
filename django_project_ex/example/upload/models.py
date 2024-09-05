from django.db import models


class PrivateFile(models.Model):
    private_file = models.FileField(upload_to='private/right')


class PublicFile(models.Model):
    public_file = models.FileField(upload_to='public/right')


class InvalidFile(models.Model):
    invalid_file = models.FileField(upload_to='invalid/right')
