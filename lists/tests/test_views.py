from unittest import skip

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import resolve
from django.utils.html import escape

from lists.forms import ItemForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR, ExistingListItemForm
from lists.models import Item, List
from lists.views import home_page


class HomePageTest(TestCase):
    """ Тест домашней страницы """

    def test_home_page_returns_correct_html(self):
        """ Тест: Используется домашний шаблон """
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        """ Тест: Домашняя страница использует форму для элемента """
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):
    """ Тест представления списка """

    def post_invalid_input(self):
        """ Отправляем недопустимый ввод """
        list_ = List.objects.create()
        return self.client.post(f'/lists/{list_.id}/', data={'text': ''})

    def test_uses_list_template(self):
        """ Тест: Используется шаблон списка """
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_passes_correct_list_to_template(self):
        """ Тест: Передается правильный шаблон списка """
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

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
        self.client.post('/lists/new', data={'text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """ Тест: можно сохранить запрос в существующий список """
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        """ Тест: Переадресуется в представление списка """
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

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
        response = self.client.post('/lists/new', data={'text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_displays_item_forms(self):
        """ Тест: Отображение формы для элемента """
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_for_invalid_input_nothing_saved_to_db(self):
        """ Тест на недопустимый ввод: Ничего не сохраняется в БД """
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        """ Тест на недопустимый ввод: Отображается шаблон списка """
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        """ Тест на недопустимый ввод: Форма передается в шаблон """
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        """ Тест на недопустимый ввод: На странице отображается ошибка """
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        """ Тест: Ошибки валидации повторяющегося элемента оканчиваются на странице списков"""
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='Item text')
        response = self.client.post(f'/lists/{list1.id}/', data={'text': 'Item text'})
        expected_error = escape(DUPLICATE_ITEM_ERROR)

        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)


class NewListTest(TestCase):
    """ Тестирование нового списка """

    def test_for_invalid_input_renders_home_template(self):
        """ Тест на недопустимый ввод: Отображение домашнего шаблона """
        response = self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_for_invalid_input_passes_form_to_template(self):
        """ Тест на недопустимый ввод: Форма передается в шаблон """
        response = self.client.post('/lists/new', data={'item_text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_validation_errors_are_show_on_home_page(self):
        """ Тест: Ошибки валидации выводятся на домашней странице """
        response = self.client.post('/lists/new', data={'item_text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_invalid_list_items_arent_saved(self):
        """ Тест: Недопустимые элементы списка не должны сохраняться """
        self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

