from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from lists.models import Item


def home_page(request):
    """ Домашняя страница """
    if request.method == 'POST':
        Item.objects.create(text=request.POST.get('item_text', ''))
        return redirect('/')
    items = Item.objects.all()
    return render(request, 'home.html', {'items': items})
