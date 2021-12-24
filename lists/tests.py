from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import resolve

from lists.views import home_page


class HomePageTest(TestCase):
    """ Тест домашней страницы """

    def test_home_page_returns_correct_html(self):
        """ Тест: Используется домашний шаблон """
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')
