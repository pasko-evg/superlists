from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import resolve

from lists.models import Item, List
from lists.views import home_page


class HomePageTest(TestCase):
    """ Тест домашней страницы """

    def test_home_page_returns_correct_html(self):
        """ Тест: Используется домашний шаблон """
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class ListAndItemModelsTest(TestCase):
    """ Тест модели элемента списка """

    def test_saving_and_retrieving_items(self):
        """ Тест: Сохранение и получение элементов списка """
        list_ = List()
        list_.save()
        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)


class ListViewTest(TestCase):
    """ Тест представления списка """

    def test_uses_list_template(self):
        """ Тест: Используется шаблон списка """
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        """ Тест: отображаются элементы только для этого списка """
        correct_list = List.objects.create()
        Item.objects.create(text='Item 1', list=correct_list)
        Item.objects.create(text='Item 2', list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='Item 3', list=other_list)
        Item.objects.create(text='Item 4', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'Item 1')
        self.assertContains(response, 'Item 2')
        self.assertNotContains(response, 'Item 3')
        self.assertNotContains(response, 'Item 4')

    def test_can_save_a_POST_request(self):
        """ Тест: можно сохранить пост запрос """
        self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_displays_all_items(self):
        """ Тест: отображаются все элементы списка """
        list_ = List.objects.create()
        Item.objects.create(text='Item 1', list=list_)
        Item.objects.create(text='Item 2', list=list_)

        response = self.client.get(f'/lists/{list_.id}/')

        self.assertContains(response, 'Item 1')
        self.assertContains(response, 'Item 2')

    def test_redirect_after_POST(self):
        """ Тест: перенаправление после post-запроса """
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_passes_correct_list_to_template(self):
        """ Тест: Передается правильный шаблон списка """
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)


class NewItemTest(TestCase):
    """ Тест нового элемента списка """

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """ Тест: можно сохранить запрос в существующий список """
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        """ Тест: Переадресуется в представление списка """
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')
