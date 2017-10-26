from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'org/index.html', context)
