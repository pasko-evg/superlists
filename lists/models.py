from django.db import models


# Create your models here.
class List(models.Model):
    """ Список дел """
    pass


class Item(models.Model):
    """ Элемент списка """
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)
