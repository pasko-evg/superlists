from django.db import models


# Create your models here.
from django.urls import reverse


class List(models.Model):
    """ Список дел """
    def get_absolute_url(self):
        """
        Получить абсолютный URL
        :return: absolute List URL
        """
        return reverse('view_list', args=[self.id])


class Item(models.Model):
    """ Элемент списка """
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)
