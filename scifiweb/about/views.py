from django.shortcuts import render

from scifiweb.home import MEMBERS


def team(article, request):
    return render(
        request,
        'about/team.html',
        {
            'title': article.title,
            'article': article,
            'members': MEMBERS,
        }
    )
