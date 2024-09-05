from django.http import HttpResponse
from django.shortcuts import render

from example.upload.models import PrivateFile, PublicFile, InvalidFile


# Create your views here.
def private(request):
    if request.method == 'POST':
        PrivateFile.objects.create(private_file=request.FILES['private_file'])
        return HttpResponse(request)
    return render(request, 'upload/private_upload.html')


def public(request):
    if request.method == 'POST':
        PublicFile.objects.create(public_file=request.FILES['public_file'])
        return HttpResponse(request)
    return render(request, 'upload/public_upload.html')

def invalid(request):
    if request.method == 'POST':
        InvalidFile.objects.create(invalid_file=request.FILES['invalid_file'])
        return HttpResponse(request)
