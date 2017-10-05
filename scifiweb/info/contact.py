from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from scifiweb.utils import store_decorators


# Hopefully these are reasonable numbers
MAX_SUBJECT_LENGTH = 79
MAX_MESSAGE_LENGTH = 79 * 100


class MessageForm(forms.Form):
    sender = forms.EmailField()
    subject = forms.CharField(strip=True, max_length=MAX_SUBJECT_LENGTH)
    message = forms.CharField(max_length=MAX_MESSAGE_LENGTH)
    cc_sender = forms.BooleanField(required=False)


@store_decorators((csrf_exempt,))
def contact(article, request):
    success = False
    if request.method != 'POST':
        form = MessageForm()
    else:
        form = MessageForm(request.POST)
        if form.is_valid():
            if (
                settings.CONTACT_EMAIL is not None
                and settings.UNAUTHENTICATED_EMAIL_HOST is not None
            ):
                with get_connection(host=settings.UNAUTHENTICATED_EMAIL_HOST) as c:
                    EmailMessage(
                        subject=form.cleaned_data['subject'],
                        body=form.cleaned_data['message'],
                        from_email=form.cleaned_data['sender'],
                        to=(settings.CONTACT_EMAIL,),
                        cc=(form.cleaned_data['sender'],) if form.cleaned_data['cc_sender'] else (),
                        connection=c,
                    ).send()
            success = True
            # Display a fresh form after successfully submitting
            form = MessageForm()

    return render(
        request,
        'info/special/contact.html',
        {
            'title': article.title,
            'article': article,
            'form': form,
            'success': success,
        },
    )
