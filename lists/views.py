from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from lists.models import Item


def home_page(request):
    """ Домашняя страница """
    return render(request, 'home.html')


def view_list(request):
    items = Item.objects.all()
    return render(request, 'list.html', {'items': items})


def new_list(request):
    """ Новый список """
    Item.objects.create(text=request.POST.get('item_text', ''))
    return redirect('/lists/best-list-app/')
