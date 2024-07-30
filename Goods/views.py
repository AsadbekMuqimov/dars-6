from django.shortcuts import render
from . import models

def main(request):
    banners = models.Banner.objects.filter(is_active = True)[:5]
    context = {'banners': banners}

    return render(request, 'index.html')
