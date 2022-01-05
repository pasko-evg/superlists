from django.contrib import auth, messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from accounts.models import Token


def send_login_email(request):
    """ Отправить сообщение для входа в систему """
    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(f"{reverse('login')}?token={str(token.uid)}")
    message_body = f'Use this link to log in:\n\n{url}'
    send_mail(
        'Your login link for Superlists',
        message_body,
        'superlists@evg-project.org',
        [email]
    )
    messages.success(request, 'Check your email, we have sent you a link that you can use to log in to the site.')
    return redirect('/')


def login(request):
    """ Зарегистрировать вход в систему """
    user = auth.authenticate(uid=request.GET.get('token'))
    if user:
        auth.login(request, user)
    return redirect('/')
