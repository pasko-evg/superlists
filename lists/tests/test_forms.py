import unittest
from unittest.mock import patch, Mock

from django.test import TestCase

from lists.forms import ItemForm, ExistingListItemForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR, NewListForm
from lists.models import List, Item


class ItemFormTest(TestCase):
    """ Тестирование формы для элемента списка """

    def test_form_item_input_has_placeholder_and_css_classes(self):
        """ Тест: Поле ввода имеет атрибут placeholder и css-классы """
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-group-lg"', form.as_p())

    def test_form_validation_for_blank_items(self):
        """ Тест: Валидация формы для пустых элементов"""
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])


class ExistingListItemFormTest(TestCase):
    """ Тестирование формы элемента существующего списка """

    def test_form_renders_item_text_input(self):
        """ Тест: Форма отображает текстовый ввод элемента """
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_blank_items(self):
        """ Тест: Валидация формы для пустых элементов """
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test_form_validation_for_duplicate_items(self):
        """ Тест: Валидация формы для пустых элементов """
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='No twins!')
        form = ExistingListItemForm(for_list=list_, data={'text': 'No twins!'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])

    def test_form_save(self):
        """ Тест: Сохранение формы """
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': 'Item text'})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.all()[0])


class NewListFormTest(unittest.TestCase):
    """ Тестирование формы нового списка """

    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_from_post_data_if_user_not_authenticated(self, mock_list_create_view):
        """ Тест: Save создает новый список из POST-данных если пользователь не аутентифицирован """
        user = Mock(is_authenticated=False)
        form = NewListForm(data={'text': 'New item text'})
        form.is_valid()
        form.save(owner=user)
        mock_list_create_view.assert_called_once_with(first_item_text='New item text')

    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_with_owner_if_user_authenticated(self, mock_list_create_new):
        """ Тест: save создает новый список с владельцем, если пользователь аутентифицирован """
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        form.save(owner=user)
        mock_list_create_new.assert_called_once_with(first_item_text='new item text', owner=user)

    @patch('lists.forms.List.create_new')
    def test_save_returns_new_list_object(self, mock_list_create_new):
        """ Тест: Save возвращает новый объект списка """
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        response = form.save(owner=user)
        self.assertEqual(response, mock_list_create_new.return_value)
