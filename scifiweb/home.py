from django.shortcuts import render


def home(request):
    return render(
        request,
        'home.html',
        {
            'full_title': 'SCIFI Project',
        },
    )
